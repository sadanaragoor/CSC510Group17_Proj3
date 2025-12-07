"""
Fixtures for service tests.
"""
import pytest
import sys
import os
from decimal import Decimal

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from app import create_app
from database.db import db
from models.user import User
from models.menu_item import MenuItem
from models.order import Order, OrderItem


@pytest.fixture(scope="function")
def app():
    """Create and configure a test application instance."""
    app = create_app("testing")
    
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "WTF_CSRF_ENABLED": False,
        "SECRET_KEY": "test-secret-key",
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
    })
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture(scope="function")
def test_user(app):
    """Create a test user."""
    with app.app_context():
        user = User(username="testuser", email="test@example.com")
        user.set_password("testpassword123")
        db.session.add(user)
        db.session.commit()
        return user.id

