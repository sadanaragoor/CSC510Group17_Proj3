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

    def test_browse_ingredients(self, client, app, test_user):
        """Test browsing ingredients."""
        self.login(client)
        response = client.get("/menu/browse-ingredients")
        assert response.status_code == 200

    def test_get_menu_item_api(self, client, app, test_user):
        """Test getting menu item via API."""
        self.login(client)
        response = client.get("/menu/api/item/1")
        assert response.status_code in [200, 404]
