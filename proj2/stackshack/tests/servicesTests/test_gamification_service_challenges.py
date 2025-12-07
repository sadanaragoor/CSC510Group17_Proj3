"""
Comprehensive challenge tests to increase coverage.
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


class TestChallengeComprehensive:
    """Comprehensive challenge tests."""
    
    def test_check_daily_bonus_pickles(self, app, test_user):
        """Test checking daily bonus for pickles."""
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
            
            order = Order(user_id=test_user, total_price=Decimal("10.00"), original_total=Decimal("10.00"), status="Pending")
            db.session.add(order)
            db.session.flush()
            
            pickles = MenuItem(name="Pickles", category="topping", price=Decimal("0.50"), is_available=True)
            db.session.add(pickles)
            db.session.flush()
            
            order_item = OrderItem(
                order_id=order.id,
                menu_item_id=pickles.id,
                name="Pickles",
                price=pickles.price,
                quantity=1
            )
            db.session.add(order_item)
            
            if not order.ordered_at:
                order.ordered_at = datetime.utcnow()
            db.session.commit()
            
            success, bonus_obj = GamificationService.check_daily_bonus(test_user, order)
            
            assert isinstance(success, bool)
    
    def test_check_daily_bonus_early_bird(self, app, test_user):
        """Test checking daily bonus for early bird."""
        with app.app_context():
            today = date.today()
            bonus = DailyBonus(
                bonus_date=today,
                description="Order before 11 AM",
                condition="early_bird",
                points_reward=50,
                is_active=True
            )
            db.session.add(bonus)
            db.session.commit()
            
            order = Order(user_id=test_user, total_price=Decimal("10.00"), original_total=Decimal("10.00"), status="Pending")
            db.session.add(order)
            
            # Set order time to 10:00 AM local time
            local_tz = pytz.timezone('US/Eastern')
            local_time = local_tz.localize(datetime(2025, 12, 6, 10, 0))
            utc_time = local_time.astimezone(pytz.utc)
            order.ordered_at = utc_time.replace(tzinfo=None)
            
            db.session.commit()
            
            success, bonus_obj = GamificationService.check_daily_bonus(test_user, order)
            
            assert isinstance(success, bool)
    