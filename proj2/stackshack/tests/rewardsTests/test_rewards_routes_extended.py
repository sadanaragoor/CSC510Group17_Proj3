"""
Extended test cases for gamification routes to increase coverage.
"""

from datetime import date, timedelta
from models.gamification import (
    Badge,
    UserBadge,
)
from database.db import db


class TestRewardsRoutesExtended:
    """Extended test cases for rewards routes to increase coverage."""

    def login(self, client, username="testuser", password="testpassword123"):
        """Helper method to login a user."""
        return client.post(
            "/auth/login",
            data={"username": username, "password": password},
            follow_redirects=True,
        )

    def test_api_points_get(self, client, app, test_user):
        """Test getting user points via API."""
        with app.app_context():
            from services.gamification_service import GamificationService

            GamificationService.earn_points("purchase", test_user, 150, "Test order")

        self.login(client)
        response = client.get("/gamification/api/points")

        assert response.status_code == 200
        data = response.get_json()
        assert "points" in data
        assert "tier" in data
        assert data["points"] >= 150

    def test_api_points_earn(self, client, app, test_user):
        """Test earning points via API."""
        self.login(client)
        response = client.post(
            "/gamification/api/points/earn",
            json={"event_type": "review", "points": 25, "description": "Test review"},
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert "points_earned" in data

    def test_api_points_earn_missing_event_type(self, client, app, test_user):
        """Test earning points without event_type."""
        self.login(client)
        response = client.post("/gamification/api/points/earn", json={"points": 25})

        assert response.status_code == 400
        data = response.get_json()
        assert "error" in data

    def test_api_badges_get(self, client, app, test_user, sample_badges):
        """Test getting user badges."""
        with app.app_context():
            user_badge = UserBadge(user_id=test_user, badge_id=sample_badges[0])
            db.session.add(user_badge)
            db.session.commit()

        self.login(client)
        response = client.get("/gamification/api/badges")

        assert response.status_code == 200
        data = response.get_json()
        assert "badges" in data
        assert len(data["badges"]) > 0

    def test_api_badges_check(self, client, app, test_user, sample_order):
        """Test checking badges for an order."""
        with app.app_context():
            # Create first order badge
            first_order_badge = Badge(
                name="First Order",
                slug="first_order",
                description="Place your first order",
                badge_type="behavioral",
            )
            db.session.add(first_order_badge)
            db.session.commit()

        self.login(client)
        response = client.post(
            "/gamification/api/badges/check", json={"order_id": sample_order}
        )

        assert response.status_code == 200
        data = response.get_json()
        assert "newly_earned" in data
        assert "count" in data

    def test_api_badges_check_missing_order_id(self, client, app, test_user):
        """Test checking badges without order_id."""
        self.login(client)
        response = client.post("/gamification/api/badges/check", json={})

        assert response.status_code == 400

    def test_api_tier_get(self, client, app, test_user):
        """Test getting user tier."""
        self.login(client)
        response = client.get("/gamification/api/tier")

        assert response.status_code == 200
        data = response.get_json()
        assert "tier" in data
        assert "multiplier" in data
        assert "points" in data

    def test_api_rewards_get(self, client, app, test_user):
        """Test getting available rewards."""
        self.login(client)
        response = client.get("/gamification/api/rewards")

        assert response.status_code == 200
        data = response.get_json()
        assert "rewards" in data
        assert "free_topping" in data["rewards"]

    def test_api_daily_bonus_get(self, client, app, test_user):
        """Test getting daily bonuses."""
        with app.app_context():
            from services.challenge_service import ChallengeService

            today = date.today()
            ChallengeService.generate_daily_challenges(today, max_challenges=2)

        self.login(client)
        response = client.get("/gamification/api/daily-bonus")

        assert response.status_code == 200
        data = response.get_json()
        assert "bonuses" in data or "daily_bonuses" in data

    def test_api_weekly_challenge_get(self, client, app, test_user):
        """Test getting weekly challenges."""
        with app.app_context():
            from services.challenge_service import ChallengeService

            days_since_monday = date.today().weekday()
            week_start = date.today() - timedelta(days=days_since_monday)
            ChallengeService.generate_weekly_challenges(week_start, max_challenges=3)

        self.login(client)
        response = client.get("/gamification/api/weekly-challenge")

        assert response.status_code == 200
        data = response.get_json()
        assert "challenges" in data or "weekly_challenges" in data
