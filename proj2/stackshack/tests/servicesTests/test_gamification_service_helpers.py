"""
Tests for gamification service helper methods to increase coverage.
"""
from decimal import Decimal
from datetime import date, datetime, timedelta
from models.gamification import DailyBonus, WeeklyChallenge, UserChallengeProgress
from models.user import User
from models.order import Order, OrderItem
from models.menu_item import MenuItem
from services.gamification_service import GamificationService
from database.db import db
import pytz


class TestGamificationServiceHelpers:
    """Tests for helper methods in gamification service."""
    
    def test_check_daily_condition_bun_conditions(self, app, test_user):
        """Test checking daily conditions for bun types."""
        with app.app_context():
            order = Order(user_id=test_user, total_price=Decimal("10.00"), original_total=Decimal("10.00"), status="Pending")
            db.session.add(order)
            db.session.flush()
            
            # Test keto bun
            keto_bun = MenuItem(name="Keto Bun", category="bun", price=Decimal("2.00"), is_available=True)
            db.session.add(keto_bun)
            db.session.flush()
            
            order_item = OrderItem(order_id=order.id, menu_item_id=keto_bun.id, name="Keto Bun", price=keto_bun.price, quantity=1)
            db.session.add(order_item)
            db.session.commit()
            
            order_items = order.items.all()
            local_tz = pytz.timezone('US/Eastern')
            order_time = local_tz.localize(datetime(2025, 12, 6, 12, 0))
            
            result = GamificationService._check_daily_condition("keto_bun", order_items, order, order_time, 12, 0)
            assert result is True
    
    def test_check_daily_condition_cheese_conditions(self, app, test_user):
        """Test checking daily conditions for cheese types."""
        with app.app_context():
            order = Order(user_id=test_user, total_price=Decimal("10.00"), original_total=Decimal("10.00"), status="Pending")
            db.session.add(order)
            db.session.flush()
            
            cheddar = MenuItem(name="Cheddar Cheese", category="cheese", price=Decimal("1.00"), is_available=True)
            db.session.add(cheddar)
            db.session.flush()
            
            order_item = OrderItem(order_id=order.id, menu_item_id=cheddar.id, name="Cheddar Cheese", price=cheddar.price, quantity=1)
            db.session.add(order_item)
            db.session.commit()
            
            order_items = order.items.all()
            local_tz = pytz.timezone('US/Eastern')
            order_time = local_tz.localize(datetime(2025, 12, 6, 12, 0))
            
            result = GamificationService._check_daily_condition("cheddar_cheese", order_items, order, order_time, 12, 0)
            assert result is True
    
    def test_check_daily_condition_sauce_conditions(self, app, test_user):
        """Test checking daily conditions for sauce types."""
        with app.app_context():
            order = Order(user_id=test_user, total_price=Decimal("10.00"), original_total=Decimal("10.00"), status="Pending")
            db.session.add(order)
            db.session.flush()
            
            green_sauce = MenuItem(name="Green Sauce", category="sauce", price=Decimal("0.15"), is_available=True)
            db.session.add(green_sauce)
            db.session.flush()
            
            order_item = OrderItem(order_id=order.id, menu_item_id=green_sauce.id, name="Green Sauce", price=green_sauce.price, quantity=1)
            db.session.add(order_item)
            db.session.commit()
            
            order_items = order.items.all()
            local_tz = pytz.timezone('US/Eastern')
            order_time = local_tz.localize(datetime(2025, 12, 6, 12, 0))
            
            result = GamificationService._check_daily_condition("green_sauce", order_items, order, order_time, 12, 0)
            assert result is True
    
    def test_check_daily_condition_topping_conditions(self, app, test_user):
        """Test checking daily conditions for topping types."""
        with app.app_context():
            order = Order(user_id=test_user, total_price=Decimal("10.00"), original_total=Decimal("10.00"), status="Pending")
            db.session.add(order)
            db.session.flush()
            
            pickles = MenuItem(name="Pickles", category="topping", price=Decimal("0.50"), is_available=True)
            db.session.add(pickles)
            db.session.flush()
            
            order_item = OrderItem(order_id=order.id, menu_item_id=pickles.id, name="Pickles", price=pickles.price, quantity=1)
            db.session.add(order_item)
            db.session.commit()
            
            order_items = order.items.all()
            local_tz = pytz.timezone('US/Eastern')
            order_time = local_tz.localize(datetime(2025, 12, 6, 12, 0))
            
            result = GamificationService._check_daily_condition("pickles", order_items, order, order_time, 12, 0)
            assert result is True
    
    def test_check_daily_condition_time_conditions(self, app, test_user):
        """Test checking daily conditions for time-based conditions."""
        with app.app_context():
            order = Order(user_id=test_user, total_price=Decimal("10.00"), original_total=Decimal("10.00"), status="Pending")
            db.session.add(order)
            db.session.commit()
            
            order_items = order.items.all()
            local_tz = pytz.timezone('US/Eastern')
            
            # Test before 11am
            order_time = local_tz.localize(datetime(2025, 12, 6, 10, 0))
            result = GamificationService._check_daily_condition("before_11am", order_items, order, order_time, 10, 0)
            assert result is True
            
            # Test between 2-4pm
            order_time = local_tz.localize(datetime(2025, 12, 6, 14, 30))
            result = GamificationService._check_daily_condition("between_2_4pm", order_items, order, order_time, 14, 30)
            assert result is True
            
            # Test after 8pm
            order_time = local_tz.localize(datetime(2025, 12, 6, 20, 30))
            result = GamificationService._check_daily_condition("after_8pm", order_items, order, order_time, 20, 30)
            assert result is True
    
    def test_update_weekly_progress_bun_challenges(self, app, test_user):
        """Test updating weekly progress for bun challenges."""
        with app.app_context():
            days_since_monday = date.today().weekday()
            week_start = date.today() - timedelta(days=days_since_monday)
            week_end = week_start + timedelta(days=6)
            
            challenge = WeeklyChallenge(
                week_start=week_start,
                week_end=week_end,
                description="Try 3 different buns",
                condition="bun_explorer",
                points_reward=150,
                is_active=True
            )
            db.session.add(challenge)
            db.session.commit()
            
            progress = UserChallengeProgress(
                user_id=test_user,
                challenge_id=challenge.id,
                progress=0,
                target=3
            )
            db.session.add(progress)
            db.session.commit()
            
            order = Order(user_id=test_user, total_price=Decimal("10.00"), original_total=Decimal("10.00"), status="Completed")
            db.session.add(order)
            db.session.flush()
            
            bun = MenuItem(name="Sesame Bun", category="bun", price=Decimal("1.50"), is_available=True)
            db.session.add(bun)
            db.session.flush()
            
            order_item = OrderItem(order_id=order.id, menu_item_id=bun.id, name="Sesame Bun", price=bun.price, quantity=1)
            db.session.add(order_item)
            if not order.ordered_at:
                order.ordered_at = datetime.utcnow()
            db.session.commit()
            
            updated = GamificationService._update_weekly_progress(challenge, progress, order, test_user, week_start, week_end)
            
            assert isinstance(updated, bool)

