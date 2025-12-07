"""
Comprehensive route tests to increase coverage.
Tests all route endpoints across all modules.
"""

from models.user import User
from models.order import Order
from database.db import db


class TestAllRoutes:
    """Comprehensive route tests."""

    def login(self, client, username="testuser", password="testpassword123"):
        """Helper method to login."""
        return client.post(
            "/auth/login",
            data={"username": username, "password": password},
            follow_redirects=True,
        )

    # Auth Routes
    def test_login_page(self, client):
        """Test login page loads."""
        response = client.get("/auth/login")
        assert response.status_code == 200

    def test_register_page(self, client):
        """Test register page loads."""
        response = client.get("/auth/register")
        assert response.status_code == 200

    def test_dashboard_requires_login(self, client):
        """Test dashboard requires authentication."""
        response = client.get("/auth/dashboard")
        assert response.status_code == 302

    # Menu Routes
    def test_menu_page_requires_login(self, client):
        """Test menu page requires authentication."""
        response = client.get("/menu")
        assert response.status_code == 302

    def test_cart_requires_login(self, client):
        """Test cart requires authentication."""
        response = client.get("/orders/cart")
        assert response.status_code == 302

    def test_order_history_requires_login(self, client):
        """Test order history requires authentication."""
        response = client.get("/orders/history")
        assert response.status_code == 302

    # Payment Routes
    def test_checkout_requires_login(self, client):
        """Test checkout requires authentication."""
        response = client.get("/payment/checkout/1")
        assert response.status_code == 302

    def test_payment_history_requires_login(self, client):
        """Test payment history requires authentication."""
        response = client.get("/payment/history")
        assert response.status_code == 302

    # Profile Routes
    def test_rewards_requires_login(self, client):
        """Test rewards page requires authentication."""
        response = client.get("/gamification/rewards")
        assert response.status_code == 302

    def test_api_points_requires_login(self, client):
        """Test points API requires authentication."""
        response = client.get("/gamification/api/points")
        assert response.status_code == 302

    def test_api_badges_requires_login(self, client):
        """Test badges API requires authentication."""
        response = client.get("/gamification/api/badges")
        assert response.status_code == 302

    # Shift Routes
    def test_admin_shifts_requires_login(self, client):
        """Test admin shifts requires authentication."""
        response = client.get("/shifts/admin/shifts")
        assert response.status_code == 302

    def test_staff_shifts_requires_login(self, client):
        """Test staff shifts requires authentication."""
        response = client.get("/shifts/staff/shifts")
        assert response.status_code == 302

    # Surprise Box Routes
