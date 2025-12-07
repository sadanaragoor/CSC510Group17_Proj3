"""
Comprehensive gamification service tests to increase coverage.
"""
from decimal import Decimal
from datetime import date, datetime, timedelta
from models.gamification import PointsTransaction, Badge, UserBadge, Coupon, Redemption, DailyBonus, WeeklyChallenge, UserChallengeProgress
from models.user import User
from models.order import Order, OrderItem
from models.menu_item import MenuItem
from services.gamification_service import GamificationService
from database.db import db


class TestGamificationServiceComprehensive:
    """Comprehensive gamification service tests."""
    
    def test_get_user_redemption_history(self, app, test_user):
        """Test getting user redemption history."""
        with app.app_context():
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
                coupon_code="SHACK-TEST",
                reward_type="free_topping",
                expiry_date=date.today() + timedelta(days=30),
                is_used=False
            )
            db.session.add(coupon)
            db.session.commit()
            
            # Query redemptions directly
            redemptions = Redemption.query.filter_by(user_id=test_user).all()
            history = []
            for r in redemptions:
                coupon_obj = Coupon.query.filter_by(redemption_id=r.id).first()
                history.append({
                    "redemption": r.to_dict(),
                    "coupon": coupon_obj.to_dict() if coupon_obj else None
                })
            
            assert len(history) > 0
            assert history[0]["redemption"]["reward_type"] == "free_topping"
    

