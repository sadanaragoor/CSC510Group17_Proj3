from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from controllers.order_controller import OrderController
from controllers.menu_controller import MenuController
from models.menu_item import MenuItem

VEGAN_INGREDIENT_NAMES = {
    # Buns
    "beetroot bun",
    "carrot bun",

    # Patties
    "veg patty",
    "mixed veg patty",

    # Toppings
    "onion",
    "lettuce",
    "tomato",
    "capsicum",
    "pickles",

    # Sauces
    "tomato sauce",
    "mustard sauce",
    "green sauce",
}

GLUTEN_FREE_INGREDIENT_NAMES = {
    # Gluten-free buns
    "beetroot bun",
    "carrot bun",
    "keto bun",

    # Patties (all gluten-free)
    "chicken patty",
    "beef patty",
    "pork patty",
    "mixed veg patty",
    "low-calorie beef patty",
    "veg patty",

    # Cheeses (all gluten-free)
    "swiss cheese",
    "american cheese",
    "parmesan cheese",
    "cheddar cheese",

    # Toppings (all gluten-free)
    "onion",
    "lettuce",
    "tomato",
    "capsicum",
    "pickles",

    # Sauces (all gluten-free)
    "tomato sauce",
    "mustard sauce",
    "green sauce",
    "mayo",
}

order_bp = Blueprint("order", __name__)


@order_bp.route("/history", methods=["GET"])
@login_required
def order_history():
    user_id = current_user.id
    success, msg, orders = OrderController.get_user_orders(user_id)
    if not success:
        flash(msg, "error")
        orders = []
    return render_template("orders/history.html", orders=orders)


@order_bp.route("/ingredients/<category>")
def get_ingredients(category):
    # Base query: show ALL available, in-stock items in that category
    query = (
        MenuItem.query
        .filter(MenuItem.category.ilike(f"%{category}%"))
        .filter(MenuItem.is_available == True)
        .filter(MenuItem.stock_quantity > 0)
    )

    items = query.all()

    # Determine user preferences (only if logged in)
    pref_vegan = False
    pref_gluten_free = False
    pref_high_protein = False
    pref_low_calorie = False

    if current_user.is_authenticated:
        pref_vegan = getattr(current_user, "pref_vegan", False)
        pref_gluten_free = getattr(current_user, "pref_gluten_free", False)
        pref_high_protein = getattr(current_user, "pref_high_protein", False)
        pref_low_calorie = getattr(current_user, "pref_low_calorie", False)

    data = []
    for item in items:
        matching_tags = []

        # 🔹 Low-calorie match (user prefers + item <= 80 cal)
        if pref_low_calorie and item.calories is not None and item.calories <= 80:
            matching_tags.append("Low calorie")

        # 🔹 High-protein match (user prefers + item >= 15g protein)
        if pref_high_protein and item.protein is not None and item.protein >= 15:
            matching_tags.append("High protein")

        # 🔹 Gluten-free match (based on name list)
        if pref_gluten_free and item.name in GLUTEN_FREE_INGREDIENT_NAMES:
            matching_tags.append("Gluten-free")

        # 🔹 Vegan match (based on name list)
        if pref_vegan and item.name in VEGAN_INGREDIENT_NAMES:
            matching_tags.append("Vegan")

        matches_preferences = len(matching_tags) > 0

        data.append(
            {
                "id": item.id,
                "name": item.name,
                "price": float(item.price),
                "description": item.description,
                "is_healthy": item.is_healthy_choice,
                "image_url": item.image_url,
                # ✅ used by frontend to highlight
                "matches_preferences": matches_preferences,
                "matching_tags": matching_tags,
            }
        )

    return jsonify(data)


@order_bp.route("/new", methods=["GET"])
@login_required
def create_order_form():
    success, msg, items = MenuController.get_available_items()
    if not success:
        flash("Error loading menu items: " + msg, "error")
        items = []
    return render_template("orders/create.html", items=items)


@order_bp.route("/place", methods=["POST"])
@login_required
def place_order():
    user_id = current_user.id
    item_data = []
    for key, value in request.form.items():
        if key.startswith("quantity_"):
            try:
                item_id = key.split("_")[1]
                quantity = int(value)
                if quantity > 0:
                    price = request.form.get(f"price_{item_id}")
                    name = request.form.get(f"name_{item_id}")
                    if price and name:
                        item_data.append((item_id, price, quantity, name))
            except ValueError:
                continue
    success, msg, _ = OrderController.create_new_order(user_id, item_data)
    flash(msg, "success" if success else "error")
    if success:
        return redirect(url_for("order.order_history"))
    else:
        return redirect(url_for("order.create_order_form"))
