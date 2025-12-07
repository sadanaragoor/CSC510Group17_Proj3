"""
Fixtures for dietary preferences tests.
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
def vegan_user(app):
    """Create a user with vegan preferences."""
    with app.app_context():
        user = User(username="veganuser", email="vegan@test.com", pref_vegan=True)
        user.set_password("testpass")
        db.session.add(user)
        db.session.commit()
        return user.id


@pytest.fixture(scope="function")
def gluten_free_user(app):
    """Create a user with gluten-free preferences."""
    with app.app_context():
        user = User(username="gfuser", email="gf@test.com", pref_gluten_free=True)
        user.set_password("testpass")
        db.session.add(user)
        db.session.commit()
        return user.id


@pytest.fixture(scope="function")
def high_protein_user(app):
    """Create a user with high protein preferences."""
    with app.app_context():
        user = User(
            username="proteinuser", email="protein@test.com", pref_high_protein=True
        )
        user.set_password("testpass")
        db.session.add(user)
        db.session.commit()
        return user.id


@pytest.fixture(scope="function")
def low_calorie_user(app):
    """Create a user with low calorie preferences."""
    with app.app_context():
        user = User(
            username="lowcaluser", email="lowcal@test.com", pref_low_calorie=True
        )
        user.set_password("testpass")
        db.session.add(user)
        db.session.commit()
        return user.id


@pytest.fixture(scope="function")
def sample_menu_items(app):
    """Create sample menu items with various dietary attributes."""
    with app.app_context():
        items = [
            MenuItem(
                name="Vegan Bun",
                category="bun",
                price=Decimal("1.50"),
                is_available=True,
                is_healthy_choice=True,
            ),
            MenuItem(
                name="Gluten Free Bun",
                category="bun",
                price=Decimal("2.00"),
                is_available=True,
                is_healthy_choice=True,
            ),
            MenuItem(
                name="Veggie Patty",
                category="patty",
                price=Decimal("3.00"),
                is_available=True,
                is_healthy_choice=True,
                calories=150,
                protein=15,
            ),
            MenuItem(
                name="Beef Patty",
                category="patty",
                price=Decimal("4.00"),
                is_available=True,
                is_healthy_choice=False,
                calories=300,
                protein=25,
            ),
            MenuItem(
                name="Low Cal Beef",
                category="patty",
                price=Decimal("3.50"),
                is_available=True,
                is_healthy_choice=True,
                calories=200,
                protein=30,
            ),
        ]
        for item in items:
            db.session.add(item)
        db.session.commit()
        return [item.id for item in items]
