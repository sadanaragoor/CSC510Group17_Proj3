from flask import Blueprint, jsonify
from flask_login import login_required, current_user
from models.menu_item import MenuItem
import random

surprise_bp = Blueprint("surprise", __name__)

def pick_random(items, k_min, k_max):
    """Pick between k_min and k_max unique items from list (if possible)."""
    if not items:
        return []
    k_max = min(k_max, len(items))
    k_min = min(k_min, k_max)
    k = random.randint(k_min, k_max) if k_max > 0 else 0
    if k == 0:
        return []
    return random.sample(items, k)

@surprise_bp.route("/surprise", methods=["GET"])
@login_required
def surprise():
    """
    Surprise Box:
    Build a full surprise burger using menu_items categorized as:
    - bun
    - patty
    - cheese
    - topping
    - sauce
    """

    # Get all available items
    items = MenuItem.query.filter_by(is_available=True).all()
    if not items:
        return jsonify({"error": "No available ingredients"}), 404

    # Group by category
    buns = [i for i in items if (i.category or "").lower() == "bun"]
    patties = [i for i in items if (i.category or "").lower() == "patty"]
    cheeses = [i for i in items if (i.category or "").lower() == "cheese"]
    toppings = [i for i in items if (i.category or "").lower() == "topping"]
    sauces = [i for i in items if (i.category or "").lower() == "sauce"]

    if not buns or not patties:
        return jsonify({"error": "Not enough ingredients (need at least one bun and one patty)."}), 400

    # --- Basic user preference bias (very simple / heuristic) ---
    def is_veggie_patty(p: MenuItem) -> bool:
        name_desc = ((p.name or "") + " " + (p.description or "")).lower()
        return "veg" in name_desc and "beef" not in name_desc and "chicken" not in name_desc and "pork" not in name_desc

    # If user prefers vegan, restrict patties & cheeses to "veg"/healthy ones
    if current_user.pref_vegan:
        veg_patties = [p for p in patties if is_veggie_patty(p)]
        if veg_patties:
            patties = veg_patties
        # crude cheese filter: prefer is_healthy_choice=True for vegan-ish
        healthy_cheeses = [c for c in cheeses if c.is_healthy_choice]
        if healthy_cheeses:
            cheeses = healthy_cheeses

    # If low-calorie, prefer lower-cal buns & patties if possible
    if current_user.pref_low_calorie:
        buns_sorted = sorted(buns, key=lambda x: x.calories or 9999)
        patties_sorted = sorted(patties, key=lambda x: x.calories or 9999)
        buns = buns_sorted[: max(1, min(len(buns_sorted), 3))]
        patties = patties_sorted[: max(1, min(len(patties_sorted), 3))]

    # If high-protein, prefer higher-protein patties
    if current_user.pref_high_protein:
        patties_sorted = sorted(patties, key=lambda x: -(x.protein or 0))
        patties = patties_sorted[: max(1, min(len(patties_sorted), 3))]

    # --- Build the burger ---

    bun = random.choice(buns)
    patty = random.choice(patties)
    chosen_cheeses = pick_random(cheeses, 0, 2)
    chosen_toppings = pick_random(toppings, 1, 3)
    chosen_sauces = pick_random(sauces, 1, 2)

    # Combine all components
    all_components = [bun, patty] + chosen_cheeses + chosen_toppings + chosen_sauces

    # Ensure uniqueness by id
    seen_ids = set()
    unique_components = []
    for comp in all_components:
        if comp.id not in seen_ids:
            seen_ids.add(comp.id)
            unique_components.append(comp)

    # Aggregate nutrition / price
    total_price = sum(float(c.price or 0) for c in unique_components)
    total_calories = sum(c.calories or 0 for c in unique_components)
    total_protein = sum(c.protein or 0 for c in unique_components)

    # Make a fun name
    fun_names = [
        "Stack Shack Surprise",
        "Mystery Stack",
        "Chef's Chaos Burger",
        "Wildcard Whopper",
        "Secret Menu Stack",
    ]
    burger_name = random.choice(fun_names)

    def to_dict(item: MenuItem):
        return {
            "id": item.id,
            "name": item.name,
            "category": item.category,
            "description": item.description,
            "price": float(item.price),
            "calories": item.calories,
            "protein": item.protein,
            "image_url": item.image_url,
        }

    response = {
        "burger_name": burger_name,
        "bun": to_dict(bun),
        "patty": to_dict(patty),
        "cheeses": [to_dict(c) for c in chosen_cheeses],
        "toppings": [to_dict(t) for t in chosen_toppings],
        "sauces": [to_dict(s) for s in chosen_sauces],
        "total_price": round(total_price, 2),
        "total_calories": total_calories,
        "total_protein": total_protein,
    }

    return jsonify(response)
