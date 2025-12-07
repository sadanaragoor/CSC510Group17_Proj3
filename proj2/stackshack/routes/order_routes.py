from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    jsonify,
    session,
)
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
        MenuItem.query.filter(MenuItem.category.ilike(f"%{category}%"))
        .filter(MenuItem.is_available)
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


@order_bp.route("/add-to-cart", methods=["POST"])
@login_required
def add_to_cart():
    """Add a burger to the cart (session-based)"""
    # Initialize cart if not exists
    if "cart" not in session:
        session["cart"] = []

    # Extract burger items from form
    burger_items = []
    burger_total = 0.0

    for key, value in request.form.items():
        if key.startswith("quantity_"):
            try:
                item_id = key.split("_")[1]
                quantity = int(value)
                if quantity > 0:
                    price = float(request.form.get(f"price_{item_id}", 0))
                    name = request.form.get(f"name_{item_id}", "")
                    if price and name:
                        item_price = price * quantity
                        burger_total += item_price
                        burger_items.append(
                            {
                                "item_id": item_id,
                                "name": name,
                                "price": price,
                                "quantity": quantity,
                                "item_total": item_price,
                            }
                        )
            except ValueError:
                continue

    if not burger_items:
        flash("Please add ingredients to your burger!", "error")
        return redirect(url_for("order.create_order_form"))

    # Add burger to cart
    burger = {"items": burger_items, "total": burger_total}
    session["cart"].append(burger)
    session.modified = True

    flash(f"🍔 Burger added to cart! (${burger_total:.2f})", "success")
    return redirect(url_for("order.view_cart"))


@order_bp.route("/cart", methods=["GET"])
@login_required
def view_cart():
    """View cart with all burgers"""
    cart = session.get("cart", [])
    cart_total = sum(burger["total"] for burger in cart)
    return render_template("orders/cart.html", cart=cart, cart_total=cart_total)


@order_bp.route("/cart/remove/<int:burger_index>", methods=["POST"])
@login_required
def remove_from_cart(burger_index):
    """Remove a burger from cart"""
    cart = session.get("cart", [])

    if 0 <= burger_index < len(cart):
        removed_burger = cart.pop(burger_index)
        session["cart"] = cart
        session.modified = True
        flash(f"Burger removed from cart! (${removed_burger['total']:.2f})", "info")
    else:
        flash("Invalid burger index", "error")

    return redirect(url_for("order.view_cart"))


@order_bp.route("/cart/clear", methods=["POST"])
@login_required
def clear_cart():
    """Clear entire cart"""
    session["cart"] = []
    session.modified = True
    flash("Cart cleared!", "info")
    return redirect(url_for("order.view_cart"))


@order_bp.route("/cart/checkout", methods=["POST"])
@login_required
def checkout_cart():
    """Checkout: Create order from cart and redirect to payment"""
    cart = session.get("cart", [])

    if not cart:
        flash("Your cart is empty!", "error")
        return redirect(url_for("order.create_order_form"))

    # Flatten all burger items into a single order, tracking burger_index and burger_name
    item_data = []
    for burger_index, burger in enumerate(cart, start=1):
        burger_name = burger.get("name")  # Get pre-defined burger name if exists
        for item in burger["items"]:
            item_data.append(
                (
                    item["item_id"],
                    str(item["price"]),
                    item["quantity"],
                    item["name"],
                    burger_index,  # Track which burger this item belongs to
                    burger_name,  # Store pre-defined burger name
                )
            )

    # Create order
    user_id = current_user.id
    success, msg, order = OrderController.create_new_order(user_id, item_data)

    if success:
        # Clear cart after successful order
        session["cart"] = []
        session.modified = True

        # Redirect to payment checkout
        flash("Order created! Please proceed to payment.", "success")
        return redirect(url_for("payment.checkout", order_id=order.id))
    else:
        flash(f"Error creating order: {msg}", "error")
        return redirect(url_for("order.view_cart"))


@order_bp.route("/place", methods=["POST"])
@login_required
def place_order():
    """Direct order placement (legacy route - redirects to add to cart)"""
    return add_to_cart()


@order_bp.route("/add-predefined-burger", methods=["POST"])
@login_required
def add_predefined_burger():
    """Add a pre-defined burger to cart"""
    from data_burgers import PREDEFINED_BURGERS
    from models.menu_item import MenuItem

    burger_slug = request.form.get("burger_slug")

    if not burger_slug:
        flash("Invalid burger selection", "error")
        return redirect(url_for("auth.dashboard"))

    # Find burger definition
    burger_def = None
    for burger in PREDEFINED_BURGERS:
        if burger["slug"] == burger_slug:
            burger_def = burger
            break

    if not burger_def:
        flash("Burger not found", "error")
        return redirect(url_for("auth.dashboard"))

    # Build burger items for cart
    burger_items = []
    burger_total = 0.0

    # Check if all ingredients are available BEFORE adding to cart
    out_of_stock_ingredients = []
    for ingredient_name in burger_def["ingredients"]:
        menu_item = MenuItem.query.filter_by(name=ingredient_name).first()
        if not menu_item:
            flash(
                f"❌ Ingredient '{ingredient_name}' not available in our menu", "error"
            )
            return redirect(url_for("auth.dashboard"))

        # Check stock
        if menu_item.stock_quantity <= 0:
            out_of_stock_ingredients.append(menu_item.name)

    # If any ingredients are out of stock, show detailed message
    if out_of_stock_ingredients:
        flash(
            f"❌ Cannot add '{burger_def['name']}' - Out of stock: {', '.join(out_of_stock_ingredients)}",
            "error",
        )
        return redirect(url_for("auth.dashboard"))

    # Build burger items for cart (only if all items are in stock)
    for ingredient_name in burger_def["ingredients"]:
        menu_item = MenuItem.query.filter_by(name=ingredient_name).first()

        price = float(menu_item.price)
        burger_total += price

        burger_items.append(
            {
                "item_id": str(menu_item.id),
                "name": menu_item.name,
                "price": price,
                "quantity": 1,
                "item_total": price,
            }
        )

    # Initialize cart if not exists
    if "cart" not in session:
        session["cart"] = []

    # Add burger to cart
    burger = {
        "items": burger_items,
        "total": burger_total,
        "name": burger_def["name"],  # Store burger name for display
    }
    session["cart"].append(burger)
    session.modified = True

    flash(f"🍔 {burger_def['name']} added to cart! (${burger_total:.2f})", "success")
    return redirect(url_for("order.view_cart"))
