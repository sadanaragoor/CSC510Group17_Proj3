"""
Fixtures for rewards and gamification tests.
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
from models.gamification import (
    Badge,
)


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
    """Create a test user with Bronze tier."""
    with app.app_context():
        user = User(
            username="testuser", email="test@example.com", tier="Bronze", total_points=0
        )
        user.set_password("testpassword123")
        db.session.add(user)
        db.session.commit()
        return user.id


@pytest.fixture(scope="function")
def silver_user(app):
    """Create a test user with Silver tier."""
    with app.app_context():
        user = User(
            username="silveruser",
            email="silver@example.com",
            tier="Silver",
            total_points=600,
        )
        user.set_password("testpassword123")
        db.session.add(user)
        db.session.commit()
        return user.id


@pytest.fixture(scope="function")
def gold_user(app):
    """Create a test user with Gold tier."""
    with app.app_context():
        user = User(
            username="golduser",
            email="gold@example.com",
            tier="Gold",
            total_points=1600,
        )
        user.set_password("testpassword123")
        db.session.add(user)
        db.session.commit()
        return user.id


@pytest.fixture(scope="function")
def sample_menu_items(app):
    """Create sample menu items for testing."""
    with app.app_context():
        items = [
            MenuItem(
                name="Classic Bun",
                category="bun",
                price=Decimal("1.50"),
                is_available=True,
                is_healthy_choice=True,
            ),
            MenuItem(
                name="Beef Patty",
                category="patty",
                price=Decimal("3.50"),
                is_available=True,
                is_healthy_choice=False,
            ),
            MenuItem(
                name="Cheddar Cheese",
                category="cheese",
                price=Decimal("1.00"),
                is_available=True,
                is_healthy_choice=False,
            ),
            MenuItem(
                name="Lettuce",
                category="topping",
                price=Decimal("0.50"),
                is_available=True,
                is_healthy_choice=True,
            ),
            MenuItem(
                name="Ketchup",
                category="sauce",
                price=Decimal("0.25"),
                is_available=True,
                is_healthy_choice=True,
            ),
            MenuItem(
                name="Pickles",
                category="topping",
                price=Decimal("0.50"),
                is_available=True,
                is_healthy_choice=True,
            ),
        ]
        for item in items:
            db.session.add(item)
        db.session.commit()
        return [item.id for item in items]


@pytest.fixture(scope="function")
def sample_order(app, test_user, sample_menu_items):
    """Create a sample order for testing."""
    with app.app_context():
        order = Order(
            user_id=test_user,
            total_price=Decimal("10.00"),
            original_total=Decimal("10.00"),
            status="Pending",
        )
        db.session.add(order)
        db.session.flush()

        bun = db.session.get(MenuItem, sample_menu_items[0])
        patty = db.session.get(MenuItem, sample_menu_items[1])

        order_items = [
            OrderItem(
                order_id=order.id,
                menu_item_id=bun.id,
                name=bun.name,
                price=bun.price,
                quantity=1,
            ),
            OrderItem(
                order_id=order.id,
                menu_item_id=patty.id,
                name=patty.name,
                price=patty.price,
                quantity=1,
            ),
        ]
        for item in order_items:
            db.session.add(item)
        db.session.commit()
        return order.id


@pytest.fixture(scope="function")
def sample_badges(app):
    """Create sample badges for testing."""
    with app.app_context():
        badges = [
            Badge(
                name="First Order",
                slug="first_order",
                description="Place your first order",
                badge_type="behavioral",
                icon="🎉",
                rarity="common",
            ),
            Badge(
                name="Sauce Collector",
                slug="sauce_collector",
                description="Try all sauces",
                badge_type="ingredient",
                icon="🍯",
                rarity="rare",
            ),
            Badge(
                name="Century Club",
                slug="century_club",
                description="100 total orders",
                badge_type="achievement",
                icon="💯",
                rarity="epic",
            ),
        ]
        for badge in badges:
            db.session.add(badge)
        db.session.commit()
        return [badge.id for badge in badges]


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
