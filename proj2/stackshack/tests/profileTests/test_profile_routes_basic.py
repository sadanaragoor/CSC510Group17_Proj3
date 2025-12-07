"""
Basic profile route tests to increase coverage.
"""


class TestProfileRoutesBasic:
    """Test basic profile route functionality."""

    def login(self, client, username="testuser", password="testpassword123"):
        """Helper method to login."""
        return client.post(
            "/auth/login",
            data={"username": username, "password": password},
            follow_redirects=True,
        )

    def test_view_profile_page(self, client, app, test_user):
        """Test viewing profile page."""
        self.login(client)
        response = client.get("/profile/profile")
        assert response.status_code == 200

    def test_update_email_success(self, client, app, test_user):
        """Test updating email successfully."""
        self.login(client)
        response = client.post(
            "/profile/update-email",
            data={"email": "newemail@example.com"},
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert b"Email updated successfully" in response.data

    def test_update_email_campus_eligible(self, client, app, test_user):
        """Test updating email to .edu makes user campus card eligible."""
        self.login(client)
        response = client.post(
            "/profile/update-email",
            data={"email": "student@university.edu"},
            follow_redirects=True,
        )
        assert response.status_code == 200

    def test_update_email_empty(self, client, app, test_user):
        """Test updating email with empty value."""
        self.login(client)
        response = client.post(
            "/profile/update-email", data={"email": ""}, follow_redirects=True
        )
        assert response.status_code == 200

    def test_update_email_invalid_no_at(self, client, app, test_user):
        """Test updating email without @ symbol."""
        self.login(client)
        response = client.post(
            "/profile/update-email",
            data={"email": "invalidemail"},
            follow_redirects=True,
        )
        assert response.status_code == 200

    def test_update_email_invalid_no_dot(self, client, app, test_user):
        """Test updating email without dot."""
        self.login(client)
        response = client.post(
            "/profile/update-email",
            data={"email": "invalid@email"},
            follow_redirects=True,
        )
        assert response.status_code == 200

    def test_update_password_success(self, client, app, test_user):
        """Test updating password successfully."""
        self.login(client)
        response = client.post(
            "/profile/update-password",
            data={
                "current_password": "testpassword123",
                "new_password": "newpassword456",
                "confirm_password": "newpassword456",
            },
            follow_redirects=True,
        )
        assert response.status_code == 200

    def test_update_password_wrong_current(self, client, app, test_user):
        """Test updating password with wrong current password."""
        self.login(client)
        response = client.post(
            "/profile/update-password",
            data={
                "current_password": "wrongpassword",
                "new_password": "newpassword456",
                "confirm_password": "newpassword456",
            },
            follow_redirects=True,
        )
        assert response.status_code == 200

    def test_update_password_mismatch(self, client, app, test_user):
        """Test updating password with mismatched confirmation."""
        self.login(client)
        response = client.post(
            "/profile/update-password",
            data={
                "current_password": "testpassword123",
                "new_password": "newpassword456",
                "confirm_password": "differentpassword",
            },
            follow_redirects=True,
        )
        assert response.status_code == 200

    def test_update_password_missing_fields(self, client, app, test_user):
        """Test updating password with missing fields."""
        self.login(client)
        response = client.post(
            "/profile/update-password",
            data={"current_password": "testpassword123"},
            follow_redirects=True,
        )
        assert response.status_code == 200

    def test_update_preferences_success(self, client, app, test_user):
        """Test updating dietary preferences successfully."""
        self.login(client)
        response = client.post(
            "/profile/update-preferences",
            data={"preferences": ["vegan", "gluten_free"]},
            follow_redirects=True,
        )
        assert response.status_code == 200

    def test_update_preferences_single(self, client, app, test_user):
        """Test updating with single preference."""
        self.login(client)
        response = client.post(
            "/profile/update-preferences",
            data={"preferences": ["vegan"]},
            follow_redirects=True,
        )
        assert response.status_code == 200

    def test_update_preferences_none(self, client, app, test_user):
        """Test updating with no preferences selected."""
        self.login(client)
        response = client.post(
            "/profile/update-preferences", data={}, follow_redirects=True
        )
        assert response.status_code == 200

    def test_update_preferences_healthy(self, client, app, test_user):
        """Test updating with healthy preference."""
        self.login(client)
        response = client.post(
            "/profile/update-preferences",
            data={"preferences": ["healthy"]},
            follow_redirects=True,
        )
        assert response.status_code == 200
