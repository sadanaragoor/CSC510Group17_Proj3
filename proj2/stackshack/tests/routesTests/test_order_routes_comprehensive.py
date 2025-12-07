"""
Comprehensive order route tests to increase coverage.
"""
from decimal import Decimal
from models.order import Order, OrderItem
from models.menu_item import MenuItem
from database.db import db


class TestOrderRoutesComprehensive:
    """Comprehensive order route tests."""
    
    def login(self, client, username="testuser", password="testpassword123"):
        """Helper method to login."""
        return client.post(
            "/auth/login",
            data={"username": username, "password": password},
            follow_redirects=True
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
            follow_redirects=True
        )
        
        assert response.status_code in [200, 404]
    
    def test_remove_cart_item_not_found(self, client, app, test_user):
        """Test removing non-existent cart item."""
        self.login(client)
        response = client.post(
            "/orders/cart/remove",
            json={"item_id": 99999},
            follow_redirects=True
        )
        
        assert response.status_code in [200, 404]
    
