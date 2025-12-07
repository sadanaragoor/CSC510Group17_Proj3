from models.order import Order, OrderItem
from models.menu_item import MenuItem
from database.db import db


class OrderController:

    @staticmethod
    def get_user_orders(user_id):
        """Retrieves all orders for a specific user."""
        try:
            orders = (
                Order.query.filter_by(user_id=user_id)
                .order_by(Order.ordered_at.desc())
                .all()
            )
            return True, "Orders retrieved successfully", orders
        except Exception as e:
            return False, f"Error retrieving orders: {str(e)}", None

    @staticmethod
    def create_new_order(user_id, item_data):
        """
        Creates a new order for the specified user with the given items.

        item_data: list of tuples:
            - (item_id, price, quantity, name) - legacy format
            - (item_id, price, quantity, name, burger_index) - with burger grouping
            - (item_id, price, quantity, name, burger_index, burger_name) - with burger name
        We IGNORE the client price & name and use DB values for safety.
        """
        if not item_data:
            return False, "Order cannot be empty.", None

        try:
            total_price = 0
            new_order = Order(user_id=user_id, total_price=0, status="Pending")
            db.session.add(new_order)
            db.session.flush()  # Get order ID

            for item_tuple in item_data:
                # Handle different formats
                burger_index = None
                burger_name = None

                if len(item_tuple) == 6:
                    # New format with burger_name
                    (
                        item_id,
                        _client_price,
                        quantity,
                        _client_name,
                        burger_index,
                        burger_name,
                    ) = item_tuple
                elif len(item_tuple) == 5:
                    # Format with burger_index only
                    item_id, _client_price, quantity, _client_name, burger_index = (
                        item_tuple
                    )
                else:
                    # Legacy format
                    item_id, _client_price, quantity, _client_name = item_tuple

                quantity_int = int(quantity)
                if quantity_int <= 0:
                    continue

                item_id_int = int(item_id)
                menu_item = db.session.get(MenuItem, item_id_int)
                if not menu_item:
                    db.session.rollback()
                    return False, f"Menu item {item_id_int} not found.", None

                # Check stock
                if menu_item.stock_quantity < quantity_int:
                    db.session.rollback()
                    return (
                        False,
                        f"Not enough stock for {menu_item.name}. "
                        f"Available: {menu_item.stock_quantity}, requested: {quantity_int}.",
                        None,
                    )

                price = float(menu_item.price)
                name = menu_item.name

                order_item = OrderItem(
                    order_id=new_order.id,
                    menu_item_id=menu_item.id,
                    name=name,
                    price=price,
                    quantity=quantity_int,
                    burger_index=burger_index,  # Track which burger this belongs to
                    burger_name=burger_name,  # Store pre-defined burger name if available
                )
                db.session.add(order_item)

                # Decrement stock & update availability
                menu_item.stock_quantity -= quantity_int
                if menu_item.stock_quantity <= 0:
                    menu_item.stock_quantity = 0
                    menu_item.is_available = False  # hide from customer menus

                total_price += price * quantity_int

            if total_price == 0:
                db.session.rollback()
                return False, "Order cannot be empty.", None

            new_order.total_price = total_price
            new_order.original_total = (
                total_price  # Store original total before any discounts
            )
            db.session.commit()
            return True, f"Order #{new_order.id} placed successfully.", new_order

        except Exception as e:
            db.session.rollback()
            return False, f"Error placing order: {str(e)}", None
