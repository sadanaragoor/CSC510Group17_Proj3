from flask import Blueprint, jsonify
from flask_login import login_required, current_user
from models.menu_item import MenuItem
from data_burgers import PREDEFINED_BURGERS
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
@surprise_bp.route("/api/surprise-burger", methods=["GET"])
@login_required
def surprise():
    """
    Surprise Box:
    Randomly chooses between:
    1. A pre-customized burger from PREDEFINED_BURGERS (weighted by user preferences)
    2. Building a burger from individual ingredients

    Returns burger configuration in consistent format.
    """

    def get_user_preferences():
        """Get user dietary preferences as list"""
        prefs = []
        if hasattr(current_user, "pref_vegan") and current_user.pref_vegan:
            prefs.append("vegan")
        if hasattr(current_user, "pref_low_calorie") and current_user.pref_low_calorie:
            prefs.append("low_calorie")
        if (
            hasattr(current_user, "pref_high_protein")
            and current_user.pref_high_protein
        ):
            prefs.append("high_protein")
        if hasattr(current_user, "pref_gluten_free") and current_user.pref_gluten_free:
            prefs.append("gluten_free")
        if not prefs:
            prefs = ["no_preference"]
        return prefs

    def to_dict(item: MenuItem):
        """Convert MenuItem to dict"""
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

    # Get user preferences
    user_prefs = get_user_preferences()

    # Decide randomly: 50% chance to try pre-customized burger, 50% to build from ingredients
    # This ensures a good mix of both types
    try_predefined = random.choice([True, False])

    # Try to get a pre-customized burger that matches user preferences
    if try_predefined:
        # Filter predefined burgers by user preferences and availability
        matching_burgers = []
        for burger_def in PREDEFINED_BURGERS:
            # Check if burger matches user preferences
            burger_tags = set(burger_def.get("dietary_tags", []))
            user_tags = set(user_prefs)

            # Match if any tag overlaps, or if user has no_preference
            if "no_preference" in user_tags or burger_tags.intersection(user_tags):
                # Check if all ingredients are available
                all_available = True
                for ingredient_name in burger_def["ingredients"]:
                    menu_item = MenuItem.query.filter_by(
                        name=ingredient_name, is_available=True
                    ).first()
                    if not menu_item or (menu_item.stock_quantity or 0) <= 0:
                        all_available = False
                        break

                if all_available:
                    matching_burgers.append(burger_def)

        # If we found matching pre-customized burgers, use one
        if matching_burgers:
            chosen_burger = random.choice(matching_burgers)

            # Build response from predefined burger
            all_items = []
            bun = None
            patty = None
            cheeses = []
            toppings = []
            sauces = []

            for ingredient_name in chosen_burger["ingredients"]:
                menu_item = MenuItem.query.filter_by(name=ingredient_name).first()
                if menu_item:
                    all_items.append(menu_item)
                    category = (menu_item.category or "").lower()
                    if category == "bun":
                        bun = menu_item
                    elif category == "patty":
                        patty = menu_item
                    elif category == "cheese":
                        cheeses.append(menu_item)
                    elif category == "topping":
                        toppings.append(menu_item)
                    elif category == "sauce":
                        sauces.append(menu_item)

            if bun and patty:
                # Ensure we have at least one cheese, topping, and sauce
                # If predefined burger is missing any, add from available items
                if not cheeses:
                    available_cheeses = MenuItem.query.filter_by(
                        is_available=True, category="cheese"
                    ).all()
                    if available_cheeses:
                        # Filter by user preferences if vegan
                        if (
                            hasattr(current_user, "pref_vegan")
                            and current_user.pref_vegan
                        ):
                            healthy_cheeses = [
                                c for c in available_cheeses if c.is_healthy_choice
                            ]
                            if healthy_cheeses:
                                available_cheeses = healthy_cheeses
                        if available_cheeses:
                            cheeses.append(random.choice(available_cheeses))
                            all_items.append(cheeses[0])

                if not toppings:
                    available_toppings = MenuItem.query.filter_by(
                        is_available=True, category="topping"
                    ).all()
                    if available_toppings:
                        toppings.append(random.choice(available_toppings))
                        all_items.append(toppings[0])

                if not sauces:
                    available_sauces = MenuItem.query.filter_by(
                        is_available=True, category="sauce"
                    ).all()
                    if available_sauces:
                        sauces.append(random.choice(available_sauces))
                        all_items.append(sauces[0])

                # Only return if we have all required categories
                if cheeses and toppings and sauces:
                    total_price = sum(float(item.price or 0) for item in all_items)
                    total_calories = sum(item.calories or 0 for item in all_items)
                    total_protein = sum(item.protein or 0 for item in all_items)

                    return jsonify(
                        {
                            "burger_name": chosen_burger["name"],
                            "bun": to_dict(bun),
                            "patty": to_dict(patty),
                            "cheeses": [to_dict(c) for c in cheeses],
                            "toppings": [to_dict(t) for t in toppings],
                            "sauces": [to_dict(s) for s in sauces],
                            "total_price": round(total_price, 2),
                            "total_calories": total_calories,
                            "total_protein": total_protein,
                            "is_predefined": True,
                        }
                    )

    # Fall back to building from ingredients (original logic)
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
        return (
            jsonify(
                {
                    "error": "Not enough ingredients (need at least one bun and one patty)."
                }
            ),
            400,
        )

    # --- Apply user dietary preferences to ingredient selection ---
    def is_veggie_patty(p: MenuItem) -> bool:
        name_desc = ((p.name or "") + " " + (p.description or "")).lower()
        return (
            "veg" in name_desc
            and "beef" not in name_desc
            and "chicken" not in name_desc
            and "pork" not in name_desc
        )

    # Apply vegan preference
    if hasattr(current_user, "pref_vegan") and current_user.pref_vegan:
        veg_patties = [p for p in patties if is_veggie_patty(p)]
        if veg_patties:
            patties = veg_patties
        # Filter cheeses to healthy choices for vegan preference
        healthy_cheeses = [c for c in cheeses if c.is_healthy_choice]
        if healthy_cheeses:
            cheeses = healthy_cheeses
        # If filtering removed all cheeses, keep original list to ensure we have at least one
        if not cheeses:
            cheeses = [
                c
                for c in MenuItem.query.filter_by(
                    is_available=True, category="cheese"
                ).all()
                if c
            ]

    # Apply gluten-free preference
    if hasattr(current_user, "pref_gluten_free") and current_user.pref_gluten_free:
        # Filter buns to gluten-free options (keto, beetroot, carrot buns typically)
        gf_buns = [
            b
            for b in buns
            if any(
                gf_term in (b.name or "").lower()
                for gf_term in ["keto", "beetroot", "carrot", "gluten"]
            )
        ]
        if gf_buns:
            buns = gf_buns

    # Apply low-calorie preference
    if hasattr(current_user, "pref_low_calorie") and current_user.pref_low_calorie:
        # Prefer lower-calorie options
        buns_sorted = sorted(buns, key=lambda x: x.calories or 9999)
        patties_sorted = sorted(patties, key=lambda x: x.calories or 9999)
        cheeses_sorted = sorted(cheeses, key=lambda x: x.calories or 9999)
        toppings_sorted = sorted(toppings, key=lambda x: x.calories or 9999)
        sauces_sorted = sorted(sauces, key=lambda x: x.calories or 9999)

        # Keep top 3 lowest calorie options for each category
        buns = buns_sorted[: max(1, min(len(buns_sorted), 3))]
        patties = patties_sorted[: max(1, min(len(patties_sorted), 3))]
        cheeses = cheeses_sorted[: max(1, min(len(cheeses_sorted), 3))]
        toppings = toppings_sorted[: max(1, min(len(toppings_sorted), 3))]
        sauces = sauces_sorted[: max(1, min(len(sauces_sorted), 3))]

    # Apply high-protein preference
    if hasattr(current_user, "pref_high_protein") and current_user.pref_high_protein:
        # Prefer higher-protein patties
        patties_sorted = sorted(patties, key=lambda x: -(x.protein or 0))
        patties = patties_sorted[: max(1, min(len(patties_sorted), 3))]

    # --- Build the burger from ingredients ---
    # Ensure we have at least one of each category (except bun/patty which are always 1)
    if not cheeses:
        return jsonify({"error": "No available cheeses."}), 400
    if not toppings:
        return jsonify({"error": "No available toppings."}), 400
    if not sauces:
        return jsonify({"error": "No available sauces."}), 400

    bun = random.choice(buns)
    patty = random.choice(patties)
    chosen_cheeses = pick_random(cheeses, 1, 2)  # At least 1 cheese
    chosen_toppings = pick_random(toppings, 1, 3)  # At least 1 topping
    chosen_sauces = pick_random(sauces, 1, 2)  # At least 1 sauce

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
        "is_predefined": False,
    }

    return jsonify(response)
