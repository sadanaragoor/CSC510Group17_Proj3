"""
Fixtures for surprise box tests.
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
def test_user(app):
    """Create a test user."""
    with app.app_context():
        user = User(username="testuser", email="test@example.com")
        user.set_password("testpassword123")
        db.session.add(user)
        db.session.commit()
        return user.id


@pytest.fixture(scope="function")
def vegan_user(app):
    """Create a user with vegan preferences."""
    with app.app_context():
        user = User(username="veganuser", email="vegan@test.com", pref_vegan=True)
        user.set_password("testpass")
        db.session.add(user)
        db.session.commit()
        return user.id


@pytest.fixture(scope="function")
def sample_menu_items(app):
    """Create sample menu items for surprise box generation."""
    with app.app_context():
        items = [
            MenuItem(
                name="Classic Bun",
                category="bun",
                price=Decimal("1.50"),
                is_available=True,
            ),
            MenuItem(
                name="Sesame Bun",
                category="bun",
                price=Decimal("1.75"),
                is_available=True,
            ),
            MenuItem(
                name="Beef Patty",
                category="patty",
                price=Decimal("3.50"),
                is_available=True,
            ),
            MenuItem(
                name="Veggie Patty",
                category="patty",
                price=Decimal("3.00"),
                is_available=True,
            ),
            MenuItem(
                name="Cheddar Cheese",
                category="cheese",
                price=Decimal("1.00"),
                is_available=True,
            ),
            MenuItem(
                name="Swiss Cheese",
                category="cheese",
                price=Decimal("1.00"),
                is_available=True,
            ),
            MenuItem(
                name="Lettuce",
                category="topping",
                price=Decimal("0.50"),
                is_available=True,
            ),
            MenuItem(
                name="Tomato",
                category="topping",
                price=Decimal("0.50"),
                is_available=True,
            ),
            MenuItem(
                name="Pickles",
                category="topping",
                price=Decimal("0.50"),
                is_available=True,
            ),
            MenuItem(
                name="Ketchup",
                category="sauce",
                price=Decimal("0.25"),
                is_available=True,
            ),
            MenuItem(
                name="Mustard",
                category="sauce",
                price=Decimal("0.25"),
                is_available=True,
            ),
        ]
        for item in items:
            db.session.add(item)
        db.session.commit()
        return [item.id for item in items]


@pytest.fixture(scope="function")
def authenticated_client(client, app, test_user):
    """Create an authenticated test client."""
    with app.app_context():
        user = db.session.get(User, test_user)
        from flask_login import login_user

        with client:
            with app.test_request_context():
                login_user(user)
            yield client
