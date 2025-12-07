"""
Edge case tests for gamification service to increase coverage.
"""
from decimal import Decimal
from datetime import date, datetime, timedelta
from models.gamification import PointsTransaction, Badge, UserBadge, Coupon, Redemption
from models.user import User
from models.order import Order, OrderItem
from models.menu_item import MenuItem
from services.gamification_service import GamificationService
from database.db import db


class TestGamificationServiceEdgeCases:
    """Edge case tests for gamification service."""
    
    def test_earn_points_negative(self, app, test_user):
        """Test earning negative points (redemption)."""
        with app.app_context():
            # First earn some points
            GamificationService.earn_points("purchase", test_user, 200, "Order")
            
            # Then redeem (negative points)
            success, message, points = GamificationService.earn_points(
                "redemption", test_user, -100, "Redeemed reward"
            )
            
            assert success is True
            assert points == -100
            
            final_points = GamificationService.get_user_points(test_user)
            assert final_points == 100
    
    def test_earn_points_zero(self, app, test_user):
        """Test earning zero points."""
        with app.app_context():
            success, message, points = GamificationService.earn_points(
                "test", test_user, 0, "Zero points"
            )
            
            assert success is True
            assert points == 0
    
    def test_get_user_points_no_transactions(self, app, test_user):
        """Test getting points for user with no transactions."""
        with app.app_context():
            points = GamificationService.get_user_points(test_user)
            
            assert points == 0
    
    def test_redeem_reward_invalid_type(self, app, test_user):
        """Test redeeming invalid reward type."""
        with app.app_context():
            success, message, coupon_code = GamificationService.redeem_reward(
                "invalid_reward", test_user
            )
            
            assert success is False
            assert coupon_code is None
    
    def test_validate_coupon_nonexistent(self, app, test_user):
        """Test validating non-existent coupon."""
        with app.app_context():
            is_valid, message, coupon_dict = GamificationService.validate_coupon(
                "SHACK-NONEXISTENT", test_user
            )
            
            assert is_valid is False
            assert coupon_dict is None
    
    def test_update_tier_user_not_found(self, app):
        """Test updating tier for non-existent user."""
        with app.app_context():
            success, message, tier = GamificationService.update_user_tier(99999)
            
            assert success is False
            assert tier is None
    
    
    def test_generate_coupon_code_uniqueness(self, app, test_user):
        """Test that generated coupon codes are unique."""
        with app.app_context():
            codes = set()
            for _ in range(10):
                code = GamificationService.generate_coupon_code()
                codes.add(code)
            
            # All codes should be unique
            assert len(codes) == 10

