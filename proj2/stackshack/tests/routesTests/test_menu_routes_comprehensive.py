"""
Comprehensive menu route tests to increase coverage.
"""


class TestMenuRoutesComprehensive:
    """Comprehensive menu route tests."""

    def login(self, client, username="testuser", password="testpassword123"):
        """Helper method to login."""
        return client.post(
            "/auth/login",
            data={"username": username, "password": password},
            follow_redirects=True,
        )
