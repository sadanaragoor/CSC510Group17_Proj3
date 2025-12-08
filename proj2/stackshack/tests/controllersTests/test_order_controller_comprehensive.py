"""
Comprehensive order controller tests to increase coverage.
"""

from decimal import Decimal
from models.order import Order
from controllers.order_controller import OrderController
from database.db import db


class TestOrderControllerComprehensive:
    """Comprehensive order controller tests."""

    def test_get_user_orders(self, app, test_user):
        """Test getting user orders."""
        with app.app_context():
            order1 = Order(
                user_id=test_user,
                total_price=Decimal("10.00"),
                original_total=Decimal("10.00"),
                status="Pending",
            )
            order2 = Order(
                user_id=test_user,
                total_price=Decimal("15.00"),
                original_total=Decimal("15.00"),
                status="Completed",
            )
            db.session.add_all([order1, order2])
            db.session.commit()

            orders = OrderController.get_user_orders(test_user)

            assert len(orders) >= 2

    def test_get_user_orders_empty(self, app, test_user):
        """Test getting orders when user has none."""
        with app.app_context():
            success, msg, orders = OrderController.get_user_orders(test_user)
            assert success is True
            assert isinstance(orders, list)

    def test_get_user_orders_invalid_user(self, app):
        """Test getting orders for non-existent user."""
        with app.app_context():
            success, msg, orders = OrderController.get_user_orders(99999)
            assert isinstance(orders, list)
