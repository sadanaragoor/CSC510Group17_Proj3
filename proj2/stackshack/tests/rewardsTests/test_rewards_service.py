"""
Test cases for gamification service.
"""

from datetime import date, datetime, timedelta
from models.gamification import PointsTransaction, Coupon, Redemption
from models.user import User
from services.gamification_service import GamificationService
from database.db import db


class TestPointsSystem:
    """Test cases for points earning and calculation."""

    def test_earn_points_bronze_tier(self, app, test_user):
        """Test earning points with Bronze tier (1.0x multiplier)."""
        with app.app_context():
            success, message, points_earned = GamificationService.earn_points(
                "purchase", test_user, 100, "Test purchase"
            )

            assert success is True
            assert points_earned == 100  # No multiplier for Bronze

            # Check transaction was created
            transaction = PointsTransaction.query.filter_by(user_id=test_user).first()
            assert transaction is not None
            assert transaction.points == 100

    def test_earn_points_silver_tier(self, app, silver_user):
        """Test earning points with Silver tier (1.2x multiplier)."""
        with app.app_context():
            success, message, points_earned = GamificationService.earn_points(
                "purchase", silver_user, 100, "Test purchase"
            )

            assert success is True
            assert points_earned == 120  # 1.2x multiplier

            transaction = PointsTransaction.query.filter_by(user_id=silver_user).first()
            assert transaction.points == 120

    def test_earn_points_gold_tier(self, app, gold_user):
        """Test earning points with Gold tier (1.5x multiplier)."""
        with app.app_context():
            success, message, points_earned = GamificationService.earn_points(
                "purchase", gold_user, 100, "Test purchase"
            )

            assert success is True
            assert points_earned == 150  # 1.5x multiplier

    def test_earn_points_no_multiplier(self, app, test_user):
        """Test earning points without multiplier (non-purchase events)."""
        with app.app_context():
            success, message, points_earned = GamificationService.earn_points(
                "review", test_user, 25, "Test review", apply_multiplier=False
            )

            assert success is True
            assert points_earned == 25  # No multiplier applied

    def test_get_user_points_empty(self, app, test_user):
        """Test getting points for user with no transactions."""
        with app.app_context():
            points = GamificationService.get_user_points(test_user)
            assert points == 0

    def test_get_user_points_with_transactions(self, app, test_user):
        """Test getting points for user with multiple transactions."""
        with app.app_context():
            # Add multiple transactions
            GamificationService.earn_points("purchase", test_user, 100, "Order 1")
            GamificationService.earn_points("purchase", test_user, 50, "Order 2")
            GamificationService.earn_points("review", test_user, 25, "Review")

            points = GamificationService.get_user_points(test_user)
            assert points == 175

    def test_get_user_points_with_redemption(self, app, test_user):
        """Test getting points after redemption."""
        with app.app_context():
            # Earn points
            GamificationService.earn_points("purchase", test_user, 200, "Order")

            # Redeem points
            GamificationService.earn_points(
                "redemption", test_user, -100, "Redeemed reward"
            )

            points = GamificationService.get_user_points(test_user)
            assert points == 100


class TestTierSystem:
    """Test cases for tier updates."""

    def test_update_tier_bronze(self, app, test_user):
        """Test tier remains Bronze with low points."""
        with app.app_context():
            success, message, tier = GamificationService.update_user_tier(test_user)
            user = db.session.get(User, test_user)

            assert success is True
            assert tier == "Bronze"
            assert user.tier == "Bronze"

    def test_update_tier_silver(self, app, test_user):
        """Test tier upgrade to Silver at 501 points."""
        with app.app_context():
            # Earn enough points for Silver
            GamificationService.earn_points("purchase", test_user, 501, "Large order")

            success, message, tier = GamificationService.update_user_tier(test_user)
            user = db.session.get(User, test_user)

            assert success is True
            assert tier == "Silver"
            assert user.tier == "Silver"

    def test_update_tier_gold(self, app, test_user):
        """Test tier upgrade to Gold at 1501 points."""
        with app.app_context():
            # Earn enough points for Gold
            GamificationService.earn_points(
                "purchase", test_user, 1501, "Very large order"
            )

            success, message, tier = GamificationService.update_user_tier(test_user)
            user = db.session.get(User, test_user)

            assert success is True
            assert tier == "Gold"
            assert user.tier == "Gold"

    def test_tier_downgrade(self, app, silver_user):
        """Test tier downgrade when points decrease."""
        with app.app_context():
            # User starts with 600 points (Silver)
            user = db.session.get(User, silver_user)
            assert user.tier == "Silver"

            # Redeem points to go below 501
            GamificationService.earn_points("redemption", silver_user, -200, "Redeemed")

            success, message, tier = GamificationService.update_user_tier(silver_user)
            assert success is True
            assert tier == "Bronze"


class TestRewardRedemption:
    """Test cases for reward redemption."""

    def test_redeem_reward_invalid_type(self, app, test_user):
        """Test redemption with invalid reward type."""
        with app.app_context():
            GamificationService.earn_points("purchase", test_user, 500, "Order")

            success, message, coupon_code = GamificationService.redeem_reward(
                test_user, "invalid_reward"
            )

            assert success is False
            assert coupon_code is None


class TestCouponValidation:
    """Test cases for coupon validation and application."""

    def test_validate_coupon_valid(self, app, test_user, sample_order):
        """Test validating a valid coupon."""
        with app.app_context():
            redemption = Redemption(
                user_id=test_user, reward_type="free_topping", points_cost=100
            )
            db.session.add(redemption)
            db.session.flush()

            # Create coupon
            coupon = Coupon(
                user_id=test_user,
                redemption_id=redemption.id,
                coupon_code="SHACK-VALID",
                reward_type="free_topping",
                expiry_date=date.today() + timedelta(days=30),
                is_used=False,
            )
            db.session.add(coupon)
            db.session.commit()

            # Validate
            is_valid, message, coupon_dict = GamificationService.validate_coupon(
                "SHACK-VALID", test_user, sample_order
            )

            assert is_valid is True
            assert coupon_dict is not None

    def test_validate_coupon_invalid_code(self, app, test_user, sample_order):
        """Test validating non-existent coupon."""
        with app.app_context():
            is_valid, message, coupon_dict = GamificationService.validate_coupon(
                "SHACK-INVALID", test_user, sample_order
            )

            assert is_valid is False
            assert coupon_dict is None

    def test_validate_coupon_wrong_user(
        self, app, test_user, silver_user, sample_order
    ):
        """Test validating coupon belonging to different user."""
        with app.app_context():
            redemption = Redemption(
                user_id=test_user, reward_type="free_topping", points_cost=100
            )
            db.session.add(redemption)
            db.session.flush()

            coupon = Coupon(
                user_id=test_user,
                redemption_id=redemption.id,
                coupon_code="SHACK-WRONG",
                reward_type="free_topping",
                expiry_date=date.today() + timedelta(days=30),
                is_used=False,
            )
            db.session.add(coupon)
            db.session.commit()

            # Try to validate with different user
            is_valid, message, coupon_dict = GamificationService.validate_coupon(
                "SHACK-WRONG", silver_user, sample_order
            )

            assert is_valid is False

    def test_validate_coupon_already_used(self, app, test_user, sample_order):
        """Test validating already used coupon."""
        with app.app_context():
            redemption = Redemption(
                user_id=test_user, reward_type="free_topping", points_cost=100
            )
            db.session.add(redemption)
            db.session.flush()

            coupon = Coupon(
                user_id=test_user,
                redemption_id=redemption.id,
                coupon_code="SHACK-USED",
                reward_type="free_topping",
                expiry_date=date.today() + timedelta(days=30),
                is_used=True,
                used_at=datetime.utcnow(),
                used_order_id=sample_order,
            )
            db.session.add(coupon)
            db.session.commit()

            is_valid, message, coupon_dict = GamificationService.validate_coupon(
                "SHACK-USED", test_user, sample_order
            )

            assert is_valid is False

    def test_validate_coupon_expired(self, app, test_user, sample_order):
        """Test validating expired coupon."""
        with app.app_context():
            redemption = Redemption(
                user_id=test_user, reward_type="free_topping", points_cost=100
            )
            db.session.add(redemption)
            db.session.flush()

            coupon = Coupon(
                user_id=test_user,
                redemption_id=redemption.id,
                coupon_code="SHACK-EXPIRED",
                reward_type="free_topping",
                expiry_date=date.today() - timedelta(days=1),
                is_used=False,
            )
            db.session.add(coupon)
            db.session.commit()

            is_valid, message, coupon_dict = GamificationService.validate_coupon(
                "SHACK-EXPIRED", test_user, sample_order
            )

            assert is_valid is False


class TestBadgeSystem:
    """Test cases for badge awarding."""
