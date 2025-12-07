"""
Extended test cases for gamification service to increase coverage.
"""

from decimal import Decimal
from models.order import Order
from services.gamification_service import GamificationService
from database.db import db


class TestGamificationServiceExtended:
    """Extended tests for gamification service to increase coverage."""

    def test_process_order_points_bronze(self, app, test_user, sample_order):
        """Test processing order points for Bronze tier."""
        with app.app_context():
            order = db.session.get(Order, sample_order)
            order.original_total = Decimal("10.00")
            db.session.commit()

            GamificationService.process_order_points(order)

            points = GamificationService.get_user_points(test_user)
            # Bronze: 10 points per $1, so $10 = 100 points
            assert points == 100

    def test_process_order_points_silver(self, app, silver_user, sample_order):
        """Test processing order points for Silver tier."""
        with app.app_context():
            order = db.session.get(Order, sample_order)
            order.user_id = silver_user
            order.original_total = Decimal("10.00")
            db.session.commit()

            GamificationService.process_order_points(order)

            points = GamificationService.get_user_points(silver_user)
            # Silver: 12 points per $1, so $10 = 120 points
            assert points == 120

    def test_process_order_points_gold(self, app, gold_user, sample_order):
        """Test processing order points for Gold tier."""
        with app.app_context():
            order = db.session.get(Order, sample_order)
            order.user_id = gold_user
            order.original_total = Decimal("10.00")
            db.session.commit()

            GamificationService.process_order_points(order)

            points = GamificationService.get_user_points(gold_user)
            # Gold: 15 points per $1, so $10 = 150 points
            assert points == 150
