"""
Comprehensive error path tests for profile routes.
"""
from models.user import User
from database.db import db


class TestProfileRoutesErrorPaths:
    """Test error paths in profile routes."""
    
    def login(self, client, username="testuser", password="testpassword123"):
        """Helper method to login."""
        return client.post(
            "/auth/login",
            data={"username": username, "password": password},
            follow_redirects=True
        )
    