from controllers.order_controller import OrderController
from models.order import Order
from database.db import db


class TestOrderController:
    """Test cases for OrderController methods."""

    def test_get_user_orders_success(self, app, test_user, sample_order):
        """Test retrieving orders for a user successfully."""
        with app.app_context():
            success, message, orders = OrderController.get_user_orders(test_user)

            assert success is True
            assert message == "Orders retrieved successfully"
            assert orders is not None
            assert len(orders) >= 1
            assert all(isinstance(order, Order) for order in orders)
            assert all(order.user_id == test_user for order in orders)

    def test_get_user_orders_no_orders(self, app, test_user):
        """Test retrieving orders when user has no orders."""
        with app.app_context():
            success, message, orders = OrderController.get_user_orders(test_user)

            assert success is True
            assert message == "Orders retrieved successfully"
            assert orders is not None
            assert len(orders) == 0

    def test_get_user_orders_multiple(self, app, test_user, multiple_orders):
        """Test retrieving multiple orders for a user."""
        with app.app_context():
            success, message, orders = OrderController.get_user_orders(test_user)

            assert success is True
            assert len(orders) == 3
            # Check they are ordered by date descending (most recent first)
            order_dates = [order.ordered_at for order in orders]
            assert order_dates == sorted(order_dates, reverse=True)

    def test_get_user_orders_different_users(self, app, test_user, sample_order):
        """Test that orders are filtered by user_id correctly."""
        with app.app_context():
            # Create another user
            from models.user import User

            another_user = User(username="anotheruser")
            another_user.set_password("password123")
            db.session.add(another_user)
            db.session.commit()

            # Get orders for the other user (should be empty)
            success, message, orders = OrderController.get_user_orders(another_user.id)

            assert success is True
            assert len(orders) == 0

    def test_create_new_order_empty_items(self, app, test_user):
        """Test creating an order with no items."""
        with app.app_context():
            success, message, order = OrderController.create_new_order(test_user, [])

            assert success is False
            assert message == "Order cannot be empty."
            assert order is None

    def test_create_new_order_invalid_quantity_format(
        self, app, test_user, sample_menu_items
    ):
        """Test creating an order with invalid quantity format."""
        with app.app_context():
            item_data = [(sample_menu_items[0], "1.50", "invalid", "Classic Bun")]

            success, message, order = OrderController.create_new_order(
                test_user, item_data
            )

            assert success is False
            assert "Error placing order" in message
            assert order is None

    def test_create_new_order_database_rollback(
        self, app, test_user, sample_menu_items
    ):
        """Test that database is rolled back on error."""
        with app.app_context():
            # Get initial order count
            initial_count = Order.query.count()

            # Try to create order with invalid data
            item_data = [(sample_menu_items[0], "invalid_price", 1, "Classic Bun")]

            success, message, order = OrderController.create_new_order(
                test_user, item_data
            )

            assert success is False
            # Verify no new orders were created
            final_count = Order.query.count()
            assert final_count == initial_count
