"""
Comprehensive status route tests to increase coverage.
"""

from models.order import Order
from database.db import db


class TestStatusRoutesComprehensive:
    """Comprehensive status route tests."""

    def login(self, client, username="testuser", password="testpassword123"):
        """Helper method to login."""
        return client.post(
            "/auth/login",
            data={"username": username, "password": password},
            follow_redirects=True,
        )
