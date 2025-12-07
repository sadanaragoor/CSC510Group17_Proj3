"""
Fixtures for inventory tests.
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


@pytest.fixture(scope="function")
def app():
    """Create and configure a test application instance."""
    app = create_app("testing")

    app.config.update(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "WTF_CSRF_ENABLED": False,
            "SECRET_KEY": "test-secret-key",
            "SQLALCHEMY_TRACK_MODIFICATIONS": False,
        }
    )

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture(scope="function")
def client(app):
    """Create a test client for the app."""
    return app.test_client()


@pytest.fixture(scope="function")
def admin_user(app):
    """Create an admin user for testing."""
    with app.app_context():
        user = User(username="admin", email="admin@test.com", role="admin")
        user.set_password("adminpass")
        db.session.add(user)
        db.session.commit()
        return user.id


@pytest.fixture(scope="function")
def sample_menu_items(app):
    """Create sample menu items for inventory testing."""
    with app.app_context():
        items = [
            MenuItem(
                name="Item 1",
                category="bun",
                price=Decimal("1.50"),
                is_available=True,
                stock_quantity=10,
            ),
            MenuItem(
                name="Item 2",
                category="patty",
                price=Decimal("3.50"),
                is_available=False,
                stock_quantity=0,
            ),
            MenuItem(
                name="Item 3",
                category="cheese",
                price=Decimal("1.00"),
                is_available=True,
                stock_quantity=5,
            ),
        ]
        for item in items:
            db.session.add(item)
        db.session.commit()
        return [item.id for item in items]
