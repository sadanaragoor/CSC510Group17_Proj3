"""
Comprehensive gamification route tests to increase coverage.
"""

from datetime import date, timedelta
from models.gamification import (
    Coupon,
    Redemption,
)
from database.db import db


class TestGamificationRoutesComprehensive:
    """Comprehensive gamification route tests."""

    def login(self, client, username="testuser", password="testpassword123"):
        """Helper method to login."""
        return client.post(
            "/auth/login",
            data={"username": username, "password": password},
            follow_redirects=True,
        )

    def test_api_redemptions_with_coupon(self, client, app, test_user):
        """Test getting redemption history with coupon."""
        with app.app_context():
            redemption = Redemption(
                user_id=test_user, reward_type="free_topping", points_cost=100
            )
            db.session.add(redemption)
            db.session.flush()

            coupon = Coupon(
                user_id=test_user,
                redemption_id=redemption.id,
                coupon_code="SHACK-TEST",
                reward_type="free_topping",
                expiry_date=date.today() + timedelta(days=30),
                is_used=False,
            )
            db.session.add(coupon)
            db.session.commit()

        self.login(client)
        response = client.get("/gamification/api/redemptions")

        assert response.status_code == 200
        data = response.get_json()
        assert "redemptions" in data
        assert len(data["redemptions"]) > 0

    def test_api_daily_bonus_multiple(self, client, app, test_user):
        """Test getting multiple daily bonuses."""
        with app.app_context():
            from services.challenge_service import ChallengeService

            today = date.today()
            ChallengeService.generate_daily_challenges(today, max_challenges=2)

        self.login(client)
        response = client.get("/gamification/api/daily-bonus")

        assert response.status_code == 200
        data = response.get_json()
        # Should return bonuses array
        assert "bonuses" in data or "daily_bonuses" in data or isinstance(data, list)

    def test_api_weekly_challenge_multiple(self, client, app, test_user):
        """Test getting multiple weekly challenges."""
        with app.app_context():
            from services.challenge_service import ChallengeService

            days_since_monday = date.today().weekday()
            week_start = date.today() - timedelta(days=days_since_monday)
            ChallengeService.generate_weekly_challenges(week_start, max_challenges=3)

        self.login(client)
        response = client.get("/gamification/api/weekly-challenge")

        assert response.status_code == 200
        data = response.get_json()
        # Should return challenges array
        assert (
            "challenges" in data
            or "weekly_challenges" in data
            or isinstance(data, list)
        )
