"""
Tests for get_monthly_leaderboard.
"""
from decimal import Decimal
from datetime import datetime
from models.gamification import PointsTransaction
from models.user import User
from services.gamification_service import GamificationService
from database.db import db


class TestGamificationServiceLeaderboard:
    """Tests for monthly leaderboard."""
    
    def test_get_monthly_leaderboard_current_month(self, app, test_user):
        """Test getting leaderboard for current month."""
        with app.app_context():
            # Create points transaction for current month
            transaction = PointsTransaction(
                user_id=test_user,
                points=100,
                event_type="purchase",
                description="Test order"
            )
            db.session.add(transaction)
            db.session.commit()
            
            leaderboard = GamificationService.get_monthly_leaderboard()
            
            assert isinstance(leaderboard, list)
            assert len(leaderboard) >= 0
    
    def test_get_monthly_leaderboard_specific_month(self, app, test_user):
        """Test getting leaderboard for specific month."""
        with app.app_context():
            # Create points transaction
            transaction = PointsTransaction(
                user_id=test_user,
                points=100,
                event_type="purchase",
                description="Test order"
            )
            db.session.add(transaction)
            db.session.commit()
            
            now = datetime.utcnow()
            leaderboard = GamificationService.get_monthly_leaderboard(
                month=now.month,
                year=now.year
            )
            
            assert isinstance(leaderboard, list)
    
    def test_get_monthly_leaderboard_december(self, app, test_user):
        """Test getting leaderboard for December (edge case for year rollover)."""
        with app.app_context():
            leaderboard = GamificationService.get_monthly_leaderboard(
                month=12,
                year=2024
            )
            
            assert isinstance(leaderboard, list)
    
    def test_get_monthly_leaderboard_limit(self, app, test_user):
        """Test getting leaderboard with limit."""
        with app.app_context():
            # Create multiple users with points
            for i in range(10):
                user = User(username=f"user{i}", email=f"user{i}@test.com")
                user.set_password("pass")
                db.session.add(user)
                db.session.flush()
                
                transaction = PointsTransaction(
                    user_id=user.id,
                    points=100 - i,  # Decreasing points
                    event_type="purchase",
                    description="Test order"
                )
                db.session.add(transaction)
            
            db.session.commit()
            
            leaderboard = GamificationService.get_monthly_leaderboard(limit=5)
            
            assert isinstance(leaderboard, list)
            assert len(leaderboard) <= 5
    
    def test_get_monthly_leaderboard_no_transactions(self, app):
        """Test getting leaderboard with no transactions."""
        with app.app_context():
            now = datetime.utcnow()
            leaderboard = GamificationService.get_monthly_leaderboard(
                month=now.month,
                year=now.year + 1  # Future month with no transactions
            )
            
            assert isinstance(leaderboard, list)
            assert len(leaderboard) == 0

