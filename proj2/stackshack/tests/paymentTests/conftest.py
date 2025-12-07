"""
Fixtures for payment tests.
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
from models.order import Order


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
        user = User(username="testuser", email="test@example.com", role="customer")
        user.set_password("testpassword123")
        db.session.add(user)
        db.session.commit()
        return user.id


@pytest.fixture(scope="function")
def campus_user(app):
    """Create a user with .edu email for campus card testing."""
    with app.app_context():
        user = User(username="student", email="student@university.edu", role="customer")
        user.set_password("testpassword123")
        db.session.add(user)
        db.session.commit()
        return user.id


@pytest.fixture(scope="function")
def sample_order(app, test_user):
    """Create a sample order for testing."""
    with app.app_context():
        order = Order(
            user_id=test_user,
            total_price=Decimal("15.00"),
            original_total=Decimal("15.00"),
            status="Pending",
        )
        db.session.add(order)
        db.session.commit()
        return order.id


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
