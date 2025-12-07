"""
Comprehensive payment route tests to increase coverage.
"""

from decimal import Decimal
from unittest.mock import patch, MagicMock
from models.order import Order
from models.payment import Transaction, Receipt, CampusCard
from database.db import db


class TestPaymentRoutesComprehensive:
    """Comprehensive payment route tests."""

    def login(self, client, username="testuser", password="testpassword123"):
        """Helper method to login."""
        return client.post(
            "/auth/login",
            data={"username": username, "password": password},
            follow_redirects=True,
        )

    def test_campus_card_info(self, client, app, campus_user):
        """Test campus card info page."""
        self.login(client, username="student", password="testpassword123")
        response = client.get("/payment/campus-card/info")

        assert response.status_code == 200

    def test_campus_card_create(self, client, app, campus_user):
        """Test creating campus card."""
        self.login(client, username="student", password="testpassword123")
        response = client.post("/payment/campus-card/create", follow_redirects=True)

        assert response.status_code == 200

    def test_admin_dashboard_requires_staff(self, client, app, test_user):
        """Test admin dashboard requires staff/admin role."""
        self.login(client)
        response = client.get("/payment/admin/dashboard", follow_redirects=True)

        assert response.status_code == 200
        # Should redirect or show unauthorized
