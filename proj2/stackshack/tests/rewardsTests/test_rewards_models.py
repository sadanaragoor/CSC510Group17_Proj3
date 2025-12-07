"""
Test cases for gamification models.
"""
from decimal import Decimal
from datetime import date, datetime, timedelta
from models.gamification import (
    PointsTransaction, Badge, UserBadge, DailyBonus, WeeklyChallenge,
    UserChallengeProgress, Redemption, Coupon
)
from database.db import db


class TestPointsTransaction:
    """Test cases for PointsTransaction model."""
    
    def test_create_points_transaction(self, app, test_user):
        """Test creating a points transaction."""
        with app.app_context():
            transaction = PointsTransaction(
                user_id=test_user,
                points=100,
                event_type="purchase",
                description="Test purchase",
                order_id=None
            )
            db.session.add(transaction)
            db.session.commit()
            
            assert transaction.id is not None
            assert transaction.user_id == test_user
            assert transaction.points == 100
            assert transaction.event_type == "purchase"
            assert transaction.created_at is not None
    
    def test_points_transaction_to_dict(self, app, test_user):
        """Test points transaction serialization."""
        with app.app_context():
            transaction = PointsTransaction(
                user_id=test_user,
                points=50,
                event_type="review",
                description="Test review"
            )
            db.session.add(transaction)
            db.session.commit()
            
            transaction_dict = transaction.to_dict()
            assert transaction_dict["user_id"] == test_user
            assert transaction_dict["points"] == 50
            assert transaction_dict["event_type"] == "review"
            assert "created_at" in transaction_dict
    
    def test_negative_points_transaction(self, app, test_user):
        """Test creating a negative points transaction (redemption)."""
        with app.app_context():
            transaction = PointsTransaction(
                user_id=test_user,
                points=-100,
                event_type="redemption",
                description="Redeemed reward"
            )
            db.session.add(transaction)
            db.session.commit()
            
            assert transaction.points == -100


class TestBadge:
    """Test cases for Badge model."""
    
    def test_create_badge(self, app):
        """Test creating a badge."""
        with app.app_context():
            badge = Badge(
                name="First Order",
                slug="first_order",
                description="Place your first order",
                badge_type="behavioral",
                icon="🎉",
                rarity="common"
            )
            db.session.add(badge)
            db.session.commit()
            
            assert badge.id is not None
            assert badge.name == "First Order"
            assert badge.slug == "first_order"
            assert badge.rarity == "common"
    
    def test_badge_to_dict(self, app):
        """Test badge serialization."""
        with app.app_context():
            badge = Badge(
                name="Century Club",
                slug="century_club",
                description="100 orders",
                badge_type="achievement",
                icon="💯",
                rarity="epic"
            )
            db.session.add(badge)
            db.session.commit()
            
            badge_dict = badge.to_dict()
            assert badge_dict["name"] == "Century Club"
            assert badge_dict["rarity"] == "epic"
            assert badge_dict["badge_type"] == "achievement"


class TestUserBadge:
    """Test cases for UserBadge model."""
    
    def test_create_user_badge(self, app, test_user, sample_badges):
        """Test creating a user badge."""
        with app.app_context():
            user_badge = UserBadge(
                user_id=test_user,
                badge_id=sample_badges[0],
                order_id=None
            )
            db.session.add(user_badge)
            db.session.commit()
            
            assert user_badge.id is not None
            assert user_badge.user_id == test_user
            assert user_badge.badge_id == sample_badges[0]
            assert user_badge.earned_at is not None
    
    def test_user_badge_unique_constraint(self, app, test_user, sample_badges):
        """Test that a user cannot earn the same badge twice."""
        with app.app_context():
            user_badge1 = UserBadge(user_id=test_user, badge_id=sample_badges[0])
            db.session.add(user_badge1)
            db.session.commit()
            
            # Try to create duplicate
            user_badge2 = UserBadge(user_id=test_user, badge_id=sample_badges[0])
            db.session.add(user_badge2)
            
            import pytest
            from sqlalchemy.exc import IntegrityError
            with pytest.raises(IntegrityError):
                db.session.commit()


class TestDailyBonus:
    """Test cases for DailyBonus model."""
    
    def test_create_daily_bonus(self, app):
        """Test creating a daily bonus."""
        with app.app_context():
            today = date.today()
            bonus = DailyBonus(
                bonus_date=today,
                description="Order with pickles",
                condition="has_pickles",
                points_reward=30,
                is_active=True
            )
            db.session.add(bonus)
            db.session.commit()
            
            assert bonus.id is not None
            assert bonus.bonus_date == today
            assert bonus.points_reward == 30
            assert bonus.is_active is True
    
    def test_multiple_daily_bonuses_same_date(self, app):
        """Test that multiple daily bonuses can exist for the same date."""
        with app.app_context():
            today = date.today()
            bonus1 = DailyBonus(
                bonus_date=today,
                description="Order with pickles",
                condition="has_pickles",
                points_reward=30
            )
            bonus2 = DailyBonus(
                bonus_date=today,
                description="Order before 11 AM",
                condition="early_bird",
                points_reward=50
            )
            db.session.add_all([bonus1, bonus2])
            db.session.commit()
            
            assert bonus1.id != bonus2.id
            assert bonus1.bonus_date == bonus2.bonus_date


class TestCoupon:
    """Test cases for Coupon model."""
    
    def test_create_coupon(self, app, test_user):
        """Test creating a coupon."""
        with app.app_context():
            # Create a redemption first (coupon requires redemption_id)
            redemption = Redemption(
                user_id=test_user,
                reward_type="free_topping",
                points_cost=100
            )
            db.session.add(redemption)
            db.session.flush()
            
            coupon = Coupon(
                user_id=test_user,
                redemption_id=redemption.id,
                coupon_code="SHACK-ABC123",
                reward_type="free_topping",
                expiry_date=date.today() + timedelta(days=30),
                is_used=False
            )
            db.session.add(coupon)
            db.session.commit()
            
            assert coupon.id is not None
            assert coupon.coupon_code == "SHACK-ABC123"
            assert coupon.is_used is False
    
    def test_coupon_expiry(self, app, test_user):
        """Test coupon expiry date."""
        with app.app_context():
            redemption = Redemption(user_id=test_user, reward_type="free_topping", points_cost=100)
            db.session.add(redemption)
            db.session.flush()
            
            expired_date = date.today() - timedelta(days=1)
            coupon = Coupon(
                user_id=test_user,
                redemption_id=redemption.id,
                coupon_code="SHACK-EXPIRED",
                reward_type="free_topping",
                expiry_date=expired_date,
                is_used=False
            )
            db.session.add(coupon)
            db.session.commit()
            
            assert coupon.expiry_date < date.today()
            assert coupon.is_valid() is False  # Should be invalid due to expiry
    
    def test_coupon_mark_as_used(self, app, test_user, sample_order):
        """Test marking a coupon as used."""
        with app.app_context():
            redemption = Redemption(user_id=test_user, reward_type="free_topping", points_cost=100)
            db.session.add(redemption)
            db.session.flush()
            
            coupon = Coupon(
                user_id=test_user,
                redemption_id=redemption.id,
                coupon_code="SHACK-TEST",
                reward_type="free_topping",
                expiry_date=date.today() + timedelta(days=30),
                is_used=False
            )
            db.session.add(coupon)
            db.session.commit()
            
            coupon.is_used = True
            coupon.used_at = datetime.utcnow()
            coupon.used_order_id = sample_order
            db.session.commit()
            
            assert coupon.is_used is True
            assert coupon.used_order_id == sample_order
            assert coupon.is_valid() is False  # Should be invalid once used

