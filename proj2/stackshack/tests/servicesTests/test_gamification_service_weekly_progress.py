"""
Comprehensive tests for _update_weekly_progress covering all challenge types.
"""
from decimal import Decimal
from datetime import date, timedelta
from models.gamification import WeeklyChallenge, UserChallengeProgress
from models.order import Order, OrderItem
from models.menu_item import MenuItem
from services.gamification_service import GamificationService
from database.db import db


class TestGamificationServiceWeeklyProgress:
    """Comprehensive tests for weekly progress updates."""
    
    def test_update_weekly_progress_three_prefix(self, app, test_user):
        """Test weekly progress update for conditions starting with 'three_'."""
        with app.app_context():
            days_since_monday = date.today().weekday()
            week_start = date.today() - timedelta(days=days_since_monday)
            week_end = week_start + timedelta(days=6)
            
            challenge = WeeklyChallenge(
                week_start=week_start,
                week_end=week_end,
                description="Test Challenge",
                condition="three_different_buns",
                points_reward=150,
                is_active=True
            )
            db.session.add(challenge)
            db.session.flush()
            
            progress = UserChallengeProgress(
                user_id=test_user,
                challenge_id=challenge.id,
                progress=0,
                target=3
            )
            db.session.add(progress)
            db.session.flush()
            
            order = Order(user_id=test_user, total_price=Decimal("10.00"), original_total=Decimal("10.00"), status="Pending")
            db.session.add(order)
            db.session.commit()
            
            updated = GamificationService._update_weekly_progress(
                challenge, progress, order, test_user, week_start, week_end
            )
            
            assert updated is True
            assert progress.progress == 1
    
    def test_update_weekly_progress_four_prefix(self, app, test_user):
        """Test weekly progress update for conditions starting with 'four_'."""
        with app.app_context():
            days_since_monday = date.today().weekday()
            week_start = date.today() - timedelta(days=days_since_monday)
            week_end = week_start + timedelta(days=6)
            
            challenge = WeeklyChallenge(
                week_start=week_start,
                week_end=week_end,
                description="Test Challenge",
                condition="four_patties",
                points_reward=200,
                is_active=True
            )
            db.session.add(challenge)
            db.session.flush()
            
            progress = UserChallengeProgress(
                user_id=test_user,
                challenge_id=challenge.id,
                progress=0,
                target=4
            )
            db.session.add(progress)
            db.session.flush()
            
            order = Order(user_id=test_user, total_price=Decimal("10.00"), original_total=Decimal("10.00"), status="Pending")
            db.session.add(order)
            db.session.commit()
            
            updated = GamificationService._update_weekly_progress(
                challenge, progress, order, test_user, week_start, week_end
            )
            
            assert updated is True
            assert progress.progress == 1
    
    def test_update_weekly_progress_five_prefix(self, app, test_user):
        """Test weekly progress update for conditions starting with 'five_'."""
        with app.app_context():
            days_since_monday = date.today().weekday()
            week_start = date.today() - timedelta(days=days_since_monday)
            week_end = week_start + timedelta(days=6)
            
            challenge = WeeklyChallenge(
                week_start=week_start,
                week_end=week_end,
                description="Test Challenge",
                condition="five_different_burgers",
                points_reward=250,
                is_active=True
            )
            db.session.add(challenge)
            db.session.flush()
            
            progress = UserChallengeProgress(
                user_id=test_user,
                challenge_id=challenge.id,
                progress=0,
                target=5
            )
            db.session.add(progress)
            db.session.flush()
            
            order = Order(user_id=test_user, total_price=Decimal("10.00"), original_total=Decimal("10.00"), status="Pending")
            db.session.add(order)
            db.session.commit()
            
            updated = GamificationService._update_weekly_progress(
                challenge, progress, order, test_user, week_start, week_end
            )
            
            assert updated is True
            assert progress.progress == 1
    
    def test_update_weekly_progress_all_buns(self, app, test_user):
        """Test weekly progress update for 'all_buns' condition."""
        with app.app_context():
            days_since_monday = date.today().weekday()
            week_start = date.today() - timedelta(days=days_since_monday)
            week_end = week_start + timedelta(days=6)
            
            challenge = WeeklyChallenge(
                week_start=week_start,
                week_end=week_end,
                description="Test Challenge",
                condition="all_buns",
                points_reward=200,
                is_active=True
            )
            db.session.add(challenge)
            db.session.flush()
            
            progress = UserChallengeProgress(
                user_id=test_user,
                challenge_id=challenge.id,
                progress=0,
                target=3
            )
            db.session.add(progress)
            db.session.flush()
            
            # Create order with 3 different buns
            bun1 = MenuItem(name="Keto Bun", category="bun", price=Decimal("2.00"), is_available=True)
            bun2 = MenuItem(name="Sesame Bun", category="bun", price=Decimal("1.50"), is_available=True)
            bun3 = MenuItem(name="Wheat Bun", category="bun", price=Decimal("1.50"), is_available=True)
            db.session.add_all([bun1, bun2, bun3])
            db.session.flush()
            
            order = Order(user_id=test_user, total_price=Decimal("10.00"), original_total=Decimal("10.00"), status="Pending")
            db.session.add(order)
            db.session.flush()
            
            item1 = OrderItem(order_id=order.id, menu_item_id=bun1.id, name="Keto Bun", price=Decimal("2.00"), quantity=1)
            item2 = OrderItem(order_id=order.id, menu_item_id=bun2.id, name="Sesame Bun", price=Decimal("1.50"), quantity=1)
            item3 = OrderItem(order_id=order.id, menu_item_id=bun3.id, name="Wheat Bun", price=Decimal("1.50"), quantity=1)
            db.session.add_all([item1, item2, item3])
            db.session.commit()
            
            updated = GamificationService._update_weekly_progress(
                challenge, progress, order, test_user, week_start, week_end
            )
            
            assert updated is True
            assert progress.progress == 1
    
    def test_update_weekly_progress_default(self, app, test_user):
        """Test weekly progress update for default condition."""
        with app.app_context():
            days_since_monday = date.today().weekday()
            week_start = date.today() - timedelta(days=days_since_monday)
            week_end = week_start + timedelta(days=6)
            
            challenge = WeeklyChallenge(
                week_start=week_start,
                week_end=week_end,
                description="Test Challenge",
                condition="unknown_condition",
                points_reward=100,
                is_active=True
            )
            db.session.add(challenge)
            db.session.flush()
            
            progress = UserChallengeProgress(
                user_id=test_user,
                challenge_id=challenge.id,
                progress=0,
                target=3
            )
            db.session.add(progress)
            db.session.flush()
            
            order = Order(user_id=test_user, total_price=Decimal("10.00"), original_total=Decimal("10.00"), status="Pending")
            db.session.add(order)
            db.session.commit()
            
            updated = GamificationService._update_weekly_progress(
                challenge, progress, order, test_user, week_start, week_end
            )
            
            assert updated is True
            assert progress.progress == 1

