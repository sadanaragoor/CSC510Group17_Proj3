"""
Comprehensive error path tests for profile routes.
"""


class TestProfileRoutesErrorPaths:
    """Test error paths in profile routes."""

    def login(self, client, username="testuser", password="testpassword123"):
        """Helper method to login."""
        return client.post(
            "/auth/login",
            data={"username": username, "password": password},
            follow_redirects=True,
        )

    def test_update_email_missing_email(self, client, app, test_user):
        """Submitting update-email with missing value shows error and redirects."""
        self.login(client)
        response = client.post(
            "/profile/profile/update-email",
            data={"email": ""},
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert b"Please enter an email address" in response.data

    def test_update_email_invalid_email(self, client, app, test_user):
        """Submitting invalid email address shows validation error."""
        self.login(client)
        response = client.post(
            "/profile/profile/update-email",
            data={"email": "not-an-email"},
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert b"Please enter a valid email address" in response.data

    def test_update_password_missing_fields(self, client, app, test_user):
        """Missing password fields should show error and redirect."""
        self.login(client)
        response = client.post(
            "/profile/profile/update-password",
            data={
                "current_password": "",
                "new_password": "",
                "confirm_password": "",
            },
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert b"All password fields are required" in response.data

    def test_update_password_incorrect_current(self, client, app, test_user):
        """Incorrect current password should be rejected."""
        self.login(client)
        response = client.post(
            "/profile/profile/update-password",
            data={
                "current_password": "wrong-password",
                "new_password": "newpass123!",
                "confirm_password": "newpass123!",
            },
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert b"Current password is incorrect" in response.data

    def test_update_password_mismatched_new(self, client, app, test_user):
        """Mismatched new and confirm passwords should show error."""
        self.login(client)
        response = client.post(
            "/profile/profile/update-password",
            data={
                "current_password": "testpassword123",
                "new_password": "one-password",
                "confirm_password": "different-password",
            },
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert b"New passwords do not match" in response.data

    def test_update_preferences_clears_when_none_selected(self, client, app, test_user):
        """Submitting preferences form with no checkboxes clears preferences."""
        self.login(client)
        response = client.post(
            "/profile/profile/update-preferences",
            data={},
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert b"Preferences cleared!" in response.data
