"""
Comprehensive order route tests to increase coverage.
"""


class TestOrderRoutesComprehensive:
    """Comprehensive order route tests."""

    def login(self, client, username="testuser", password="testpassword123"):
        """Helper method to login."""
        return client.post(
            "/auth/login",
            data={"username": username, "password": password},
            follow_redirects=True,
        )

    def test_order_history_empty(self, client, app, test_user):
        """Test viewing order history with no orders."""
        self.login(client)
        response = client.get("/orders/history")

        assert response.status_code == 200

    def test_get_cart_empty(self, client, app, test_user):
        """Test getting empty cart."""
        self.login(client)
        response = client.get("/orders/cart")

        assert response.status_code == 200

    def test_update_cart_item_not_found(self, client, app, test_user):
        """Test updating non-existent cart item."""
        self.login(client)
        response = client.post(
            "/orders/cart/update",
            json={"item_id": 99999, "quantity": 2},
            follow_redirects=True,
        )

        assert response.status_code in [200, 404]

    def test_remove_cart_item_not_found(self, client, app, test_user):
        """Test removing non-existent cart item."""
        self.login(client)
        response = client.post(
            "/orders/cart/remove", json={"item_id": 99999}, follow_redirects=True
        )

        assert response.status_code in [200, 404]

    def test_clear_cart(self, client, app, test_user):
        """Test clearing the cart."""
        self.login(client)
        response = client.post("/orders/cart/clear", follow_redirects=True)
        assert response.status_code == 200

    def test_checkout_empty_cart(self, client, app, test_user):
        """Test checkout with empty cart."""
        self.login(client)
        response = client.post("/orders/cart/checkout", follow_redirects=True)
        assert response.status_code == 200

    def test_create_order_form(self, client, app, test_user):
        """Test accessing order creation form."""
        self.login(client)
        response = client.get("/orders/new")
        assert response.status_code == 200

    def test_place_order_redirects(self, client, app, test_user):
        """Test legacy place order route."""
        self.login(client)
        response = client.post("/orders/place", data={}, follow_redirects=True)
        assert response.status_code == 200

    def test_get_ingredients_api(self, client, app, test_user):
        """Test getting ingredients by category."""
        self.login(client)
        response = client.get("/orders/ingredients/buns")
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)

    def test_view_cart_authenticated(self, client, app, test_user):
        """Test viewing cart when authenticated."""
        self.login(client)
        response = client.get("/orders/cart")
        assert response.status_code == 200
