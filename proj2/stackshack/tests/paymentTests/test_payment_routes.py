"""
Test cases for payment routes.
"""
from decimal import Decimal
from models.order import Order
from database.db import db


class TestPaymentRoutes:
    """Test cases for payment routes."""
    
    def login(self, client, username="testuser", password="testpassword123"):
        """Helper method to login a user."""
        return client.post(
            "/auth/login",
            data={"username": username, "password": password},
            follow_redirects=True
        )
    
    def test_checkout_requires_login(self, client):
        """Test that checkout page requires authentication."""
        response = client.get("/payment/checkout/1")
        assert response.status_code == 302  # Redirect to login
    
    def test_checkout_authenticated(self, client, app, test_user, sample_order):
        """Test accessing checkout when authenticated."""
        self.login(client)
        response = client.get(f"/payment/checkout/{sample_order}")
        assert response.status_code == 200
    
