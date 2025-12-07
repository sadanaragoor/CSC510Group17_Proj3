"""
Comprehensive error path tests for payment routes.
"""

from decimal import Decimal
from unittest.mock import patch, MagicMock
from models.order import Order
from models.payment import Transaction, CampusCard, Receipt
from models.user import User
from database.db import db


class TestPaymentRoutesErrorPaths:
    """Test error paths in payment routes."""

    def login(self, client, username="testuser", password="testpassword123"):
        """Helper method to login."""
        return client.post(
            "/auth/login",
            data={"username": username, "password": password},
            follow_redirects=True,
        )

    def test_process_payment_missing_order_id(self, client, app, test_user):
        """Test process payment with missing order_id."""
        self.login(client)
        response = client.post(
            "/payment/process", data={"payment_method": "card"}, follow_redirects=True
        )

        assert response.status_code == 200
        # Should redirect with error flash

    def test_admin_dashboard_unauthorized(self, client, app, test_user):
        """Test admin dashboard unauthorized access."""
        self.login(client)
        response = client.get("/payment/admin/dashboard", follow_redirects=True)

        assert response.status_code == 200

    def test_admin_dashboard_week_filter(self, client, app, test_user):
        """Test admin dashboard with week filter."""
        with app.app_context():
            user = db.session.get(User, test_user)
            user.role = "admin"
            db.session.commit()

        self.login(client)
        response = client.get("/payment/admin/dashboard?period=week")

        assert response.status_code == 200

    def test_admin_dashboard_month_filter(self, client, app, test_user):
        """Test admin dashboard with month filter."""
        with app.app_context():
            user = db.session.get(User, test_user)
            user.role = "admin"
            db.session.commit()

        self.login(client)
        response = client.get("/payment/admin/dashboard?period=month")

        assert response.status_code == 200

    def test_admin_dashboard_invalid_filter(self, client, app, test_user):
        """Test admin dashboard with invalid filter."""
        with app.app_context():
            user = db.session.get(User, test_user)
            user.role = "admin"
            db.session.commit()

        self.login(client)
        response = client.get("/payment/admin/dashboard?period=invalid")

        assert response.status_code == 200

    def test_simulate_otp_invalid(self, client, app, test_user):
        """Test simulate OTP with invalid OTP."""
        self.login(client)
        response = client.post(
            "/payment/api/simulate-otp",
            json={"otp": "12345"},  # Not 6 digits
            content_type="application/json",
        )

        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False

    def test_simulate_otp_no_otp(self, client, app, test_user):
        """Test simulate OTP without OTP."""
        self.login(client)
        response = client.post(
            "/payment/api/simulate-otp", json={}, content_type="application/json"
        )

        assert response.status_code == 400

    def test_process_balance_addition_invalid_amount_string(
        self, client, app, test_user
    ):
        """Test process balance addition with invalid amount string."""
        with app.app_context():
            user = db.session.get(User, test_user)
            user.email = "student@ncsu.edu"  # Make eligible for campus card
            db.session.commit()

            campus_card = CampusCard(
                user_id=test_user, card_number="1234567890", balance=Decimal("50.00")
            )
            db.session.add(campus_card)
            db.session.commit()

        self.login(client)
        response = client.post(
            "/payment/campus-card/process-balance-addition",
            data={"amount": "not_a_number"},
            follow_redirects=True,
        )

        assert response.status_code == 200

    def test_process_balance_addition_value_error(self, client, app, test_user):
        """Test process balance addition with ValueError."""
        with app.app_context():
            user = db.session.get(User, test_user)
            user.email = "student@ncsu.edu"
            db.session.commit()

            campus_card = CampusCard(
                user_id=test_user, card_number="1234567890", balance=Decimal("50.00")
            )
            db.session.add(campus_card)
            db.session.commit()

        self.login(client)
        response = client.post(
            "/payment/campus-card/process-balance-addition",
            data={"amount": "-10.00"},  # Invalid negative amount
            follow_redirects=True,
        )

        assert response.status_code == 200
