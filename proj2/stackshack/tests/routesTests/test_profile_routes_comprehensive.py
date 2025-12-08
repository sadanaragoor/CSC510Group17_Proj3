"""
Comprehensive profile route tests to increase coverage.
"""

from database.db import db
from models.user import User


class TestProfileRoutesComprehensive:
    """Comprehensive profile route tests."""

    def login(self, client, username="testuser", password="testpassword123"):
        """Helper method to login."""
        return client.post(
            "/auth/login",
            data={"username": username, "password": password},
            follow_redirects=True,
        )

    def test_view_profile(self, client, app, test_user):
        """Test viewing user profile."""
        self.login(client)
        response = client.get("/profile/profile")
        assert response.status_code == 200

    def test_update_email_success_not_eligible(self, client, app, test_user):
        """Update email with valid address when not eligible for campus card."""
        self.login(client)

        response = client.post(
            "/profile/profile/update-email",
            data={"email": "new@example.com"},
            follow_redirects=True,
        )

        assert response.status_code == 200
        assert b"Email updated successfully!" in response.data

        with app.app_context():
            user = db.session.get(User, test_user)
            assert user.email == "new@example.com"

    def test_update_email_success_eligible_for_campus_card(
        self, client, app, test_user, monkeypatch
    ):
        """Update email when user becomes eligible for campus card."""
        # Force eligibility check to return True
        monkeypatch.setattr(
            User,
            "is_eligible_for_campus_card",
            lambda self: True,
        )

        self.login(client)

        response = client.post(
            "/profile/profile/update-email",
            data={"email": "campus@example.edu"},
            follow_redirects=True,
        )

        assert response.status_code == 200
        assert b"now eligible for a campus card" in response.data

    def test_update_password_success(self, client, app, test_user):
        """Successfully update password with correct current password."""
        self.login(client)

        response = client.post(
            "/profile/profile/update-password",
            data={
                "current_password": "testpassword123",
                "new_password": "newpass123!",
                "confirm_password": "newpass123!",
            },
            follow_redirects=True,
        )

        assert response.status_code == 200
        assert b"Password updated successfully!" in response.data

        with app.app_context():
            user = db.session.get(User, test_user)
            assert user.check_password("newpass123!")

    def test_update_preferences_sets_flags(self, client, app, test_user):
        """Update dietary preferences and ensure flags are stored."""
        self.login(client)

        response = client.post(
            "/profile/profile/update-preferences",
            data={
                "pref_vegan": "on",
                "pref_gluten_free": "on",
            },
            follow_redirects=True,
        )

        assert response.status_code == 200
        assert b"Preferences updated!" in response.data

        with app.app_context():
            user = db.session.get(User, test_user)
            assert user.pref_vegan is True
            assert user.pref_gluten_free is True
