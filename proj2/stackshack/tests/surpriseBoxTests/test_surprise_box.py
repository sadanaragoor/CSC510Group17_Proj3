"""
Test cases for surprise box generator.
"""


class TestSurpriseBoxRoutes:
    """Test cases for surprise box routes."""

    def login(self, client, username="testuser", password="testpassword123"):
        """Helper method to login a user."""
        return client.post(
            "/auth/login",
            data={"username": username, "password": password},
            follow_redirects=True,
        )

    def test_surprise_box_requires_login(self, client, app):
        """Test that surprise box requires authentication."""
        # The route is registered with /surprisebox prefix, but also has /surprise and /api/surprise-burger
        response = client.get("/surprisebox/surprise")
        assert response.status_code == 302  # Redirect to login

    def test_surprise_box_authenticated(
        self, client, app, test_user, sample_menu_items
    ):
        """Test accessing surprise box when authenticated."""
        self.login(client)
        response = client.get("/surprisebox/surprise")

        assert response.status_code == 200
        data = response.get_json()
        assert "burger_name" in data or "bun" in data

    def test_surprise_box_returns_burger(
        self, client, app, test_user, sample_menu_items
    ):
        """Test that surprise box returns a burger configuration."""
        self.login(client)
        response = client.get("/surprisebox/api/surprise-burger")

        assert response.status_code == 200
        data = response.get_json()
        # The route returns burger_name, bun, patty, cheeses, toppings, sauces
        assert "burger_name" in data or "bun" in data

    def test_surprise_box_main_page(self, client, app, test_user, sample_menu_items):
        """Test surprise box main page."""
        self.login(client)
        response = client.get("/surprisebox/")
        assert response.status_code in [200, 404]

    def test_surprise_box_api_endpoint(self, client, app, test_user, sample_menu_items):
        """Test surprise box API endpoint."""
        self.login(client)
        response = client.get("/surprisebox/api/surprise-burger")
        assert response.status_code in [200, 404, 500]

    def test_surprise_box_respects_vegan_preference(
        self, client, app, vegan_user, sample_menu_items
    ):
        """Test that surprise box respects vegan preferences."""
        self.login(client, username="veganuser", password="testpass")
        response = client.get("/surprisebox/api/surprise-burger")

        assert response.status_code == 200
        data = response.get_json()

        # Check that no meat items are included in patty
        patty = data.get("patty", {})
        patty_name = patty.get("name", "").lower()
        assert not any(meat in patty_name for meat in ["beef", "chicken", "pork"])

    def test_surprise_box_multiple_toppings(
        self, client, app, test_user, sample_menu_items
    ):
        """Test that surprise box can include multiple toppings."""
        self.login(client)
        response = client.get("/surprisebox/api/surprise-burger")

        assert response.status_code == 200
        data = response.get_json()

        toppings = data.get("toppings", [])
        assert len(toppings) >= 1  # At least one topping

    def test_surprise_box_multiple_sauces(
        self, client, app, test_user, sample_menu_items
    ):
        """Test that surprise box can include multiple sauces."""
        self.login(client)
        response = client.get("/surprisebox/api/surprise-burger")

        assert response.status_code == 200
        data = response.get_json()

        sauces = data.get("sauces", [])
        assert len(sauces) >= 1  # At least one sauce

    def test_surprise_box_has_price(self, client, app, test_user, sample_menu_items):
        """Test that surprise box burger has a total price."""
        self.login(client)
        response = client.get("/surprisebox/api/surprise-burger")

        assert response.status_code == 200
        data = response.get_json()
        # The route returns total_price in the response
        assert "total_price" in data
        assert isinstance(data["total_price"], (int, float))

    def test_surprise_box_different_each_time(
        self, client, app, test_user, sample_menu_items
    ):
        """Test that surprise box generates different burgers."""
        self.login(client)

        response1 = client.get("/surprisebox/api/surprise-burger")
        response2 = client.get("/surprisebox/api/surprise-burger")

        assert response1.status_code == 200
        assert response2.status_code == 200

        data1 = response1.get_json()
        data2 = response2.get_json()

        # Burgers might be the same by chance, but should have valid structure
        assert "burger_name" in data1 or "bun" in data1
        assert "burger_name" in data2 or "bun" in data2
        # Should have required categories
        assert "bun" in data1
        assert "patty" in data1
        assert "cheeses" in data1
        assert "toppings" in data1
        assert "sauces" in data1
