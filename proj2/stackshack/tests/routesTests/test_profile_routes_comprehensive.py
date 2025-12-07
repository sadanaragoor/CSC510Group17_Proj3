"""
Comprehensive profile route tests to increase coverage.
"""


class TestProfileRoutesComprehensive:
    """Comprehensive profile route tests."""

    def login(self, client, username="testuser", password="testpassword123"):
        """Helper method to login."""
        return client.post(
            "/auth/login",
            data={"username": username, "password": password},
            follow_redirects=True,
        )
