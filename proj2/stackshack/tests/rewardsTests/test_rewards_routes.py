"""
Test cases for gamification routes.
"""

from datetime import date, timedelta
from models.gamification import (
    UserBadge,
    Coupon,
    Redemption,
)
from models.order import Order
from database.db import db


class TestRewardsRoutes:
    """Test cases for rewards page and API routes."""

    def login(self, client, username="testuser", password="testpassword123"):
        """Helper method to login a user."""
        return client.post(
            "/auth/login",
            data={"username": username, "password": password},
            follow_redirects=True,
        )

    def test_rewards_page_requires_login(self, client):
        """Test that rewards page requires authentication."""
        response = client.get("/gamification/rewards")
        assert response.status_code == 302  # Redirect to login

    def test_rewards_page_authenticated(self, client, app, test_user):
        """Test accessing rewards page when authenticated."""
        self.login(client)
        response = client.get("/gamification/rewards")
        assert response.status_code == 200
        assert b"rewards" in response.data.lower() or b"points" in response.data.lower()

    def test_rewards_page_displays_points(self, client, app, test_user):
        """Test that rewards page displays user points."""
        with app.app_context():
            from services.gamification_service import GamificationService

            GamificationService.earn_points("purchase", test_user, 150, "Test order")

        self.login(client)
        response = client.get("/gamification/rewards")
        assert response.status_code == 200

    def test_rewards_page_displays_tier(self, client, app, silver_user):
        """Test that rewards page displays user tier."""
        self.login(client, username="silveruser", password="testpassword123")
        response = client.get("/gamification/rewards")
        assert response.status_code == 200
        assert b"silver" in response.data.lower()

    def test_api_get_badges_all(self, client, app, test_user, sample_badges):
        """Test API endpoint to get all badges."""
        self.login(client)
        response = client.get("/gamification/api/badges/all")

        assert response.status_code == 200
        data = response.get_json()
        assert "badges" in data
        assert len(data["badges"]) > 0

    def test_api_get_user_badges(self, client, app, test_user, sample_badges):
        """Test API endpoint to get user badges."""
        with app.app_context():
            # Award a badge
            user_badge = UserBadge(user_id=test_user, badge_id=sample_badges[0])
            db.session.add(user_badge)
            db.session.commit()

        self.login(client)
        response = client.get("/gamification/api/badges/all")

        assert response.status_code == 200
        data = response.get_json()
        assert "badges" in data

    def test_api_redemptions(self, client, app, test_user):
        """Test API endpoint to get redemption history."""
        with app.app_context():
            # Create a redemption
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

    def test_api_coupon_validate_valid(self, client, app, test_user, sample_order):
        """Test validating a valid coupon via API."""
        with app.app_context():
            redemption = Redemption(
                user_id=test_user, reward_type="free_topping", points_cost=100
            )
            db.session.add(redemption)
            db.session.flush()

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

        self.login(client)
        response = client.post(
            "/gamification/api/coupon/validate",
            json={"coupon_code": "SHACK-VALID", "order_id": sample_order},
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True

    def test_api_coupon_apply_success(self, client, app, test_user, sample_order):
        """Test applying a valid coupon via API."""
        with app.app_context():
            # Create order and coupon
            db.session.get(Order, sample_order)
            redemption = Redemption(
                user_id=test_user, reward_type="free_topping", points_cost=100
            )
            db.session.add(redemption)
            db.session.flush()

            coupon = Coupon(
                user_id=test_user,
                redemption_id=redemption.id,
                coupon_code="SHACK-APPLY",
                reward_type="free_topping",
                expiry_date=date.today() + timedelta(days=30),
                is_used=False,
            )
            db.session.add(coupon)
            db.session.commit()

        self.login(client)
        response = client.post(
            "/gamification/api/coupon/apply",
            json={"coupon_code": "SHACK-APPLY", "order_id": sample_order},
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True

    def test_api_daily_bonus(self, client, app, test_user):
        """Test API endpoint to get daily bonuses."""
        with app.app_context():
            from services.challenge_service import ChallengeService

            today = date.today()
            ChallengeService.generate_daily_challenges(today, max_challenges=2)

        self.login(client)
        response = client.get("/gamification/api/daily-bonus")

        assert response.status_code == 200
        data = response.get_json()
        assert "bonuses" in data or "daily_bonuses" in data

    def test_api_weekly_challenge(self, client, app, test_user):
        """Test API endpoint to get weekly challenges."""
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

    def test_api_redeem_reward_success(self, client, app, test_user):
        """Test redeeming a reward via API."""
        with app.app_context():
            from services.gamification_service import GamificationService

            GamificationService.earn_points("purchase", test_user, 200, "Order")

        self.login(client)
        response = client.post(
            "/gamification/api/points/redeem", json={"reward_type": "free_topping"}
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert "coupon_code" in data
