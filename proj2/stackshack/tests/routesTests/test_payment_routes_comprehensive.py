"""
Comprehensive payment route tests to increase coverage.
"""


class TestPaymentRoutesComprehensive:
    """Comprehensive payment route tests."""

    def login(self, client, username="testuser", password="testpassword123"):
        """Helper method to login."""
        return client.post(
            "/auth/login",
            data={"username": username, "password": password},
            follow_redirects=True,
        )

    def test_payment_history_empty(self, client, app, test_user):
        """Test viewing payment history with no payments."""
        self.login(client)
        response = client.get("/payment/history")
        assert response.status_code == 200
