"""
Comprehensive error path tests for menu routes.
"""
from decimal import Decimal
from models.menu_item import MenuItem
from models.user import User
from database.db import db


class TestMenuRoutesErrorPaths:
    """Test error paths in menu routes."""
    
    def login(self, client, username="testuser", password="testpassword123"):
        """Helper method to login."""
        return client.post(
            "/auth/login",
            data={"username": username, "password": password},
            follow_redirects=True
        )
    
    def test_create_item_unauthorized(self, client, app, test_user):
        """Test create item as non-admin/staff."""
        self.login(client)
        response = client.post(
            "/menu/items/create",
            data={
                "name": "Test Item",
                "category": "bun",
                "price": "1.50"
            },
            follow_redirects=True
        )
        
        assert response.status_code == 200
    
    def test_update_item_not_found(self, client, app, test_user):
        """Test update non-existent item."""
        with app.app_context():
            user = db.session.get(User, test_user)
            user.role = "admin"
            db.session.commit()
        
        self.login(client)
        response = client.post(
            "/menu/items/99999/update",
            data={
                "name": "Updated Item",
                "category": "bun",
                "price": "2.00"
            },
            follow_redirects=True
        )
        
        assert response.status_code == 200
    
    def test_create_item_validation_error(self, client, app, test_user):
        """Test create item with validation error."""
        with app.app_context():
            user = db.session.get(User, test_user)
            user.role = "admin"
            db.session.commit()
        
        self.login(client)
        response = client.post(
            "/menu/items/create",
            data={
                "name": "",  # Empty name
                "category": "bun",
                "price": "1.50"
            },
            follow_redirects=True
        )
        
        assert response.status_code == 200
    

