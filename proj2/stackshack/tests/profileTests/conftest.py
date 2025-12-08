"""Fixtures for profile tests."""

import pytest
import sys
import os

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from app import create_app
from models.user import User
from database.db import db


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
    """Create a test client."""
    return app.test_client()


@pytest.fixture
def test_user(app):
    """Create a test user."""
    with app.app_context():
        user = User(username="testuser", email="test@example.com", role="customer")
        user.set_password("password123")
        db.session.add(user)
        db.session.commit()
        yield user
        db.session.delete(user)
        db.session.commit()


@pytest.fixture
def authenticated_client(client, test_user):
    """Return a client authenticated with test_user."""
    with client.session_transaction() as sess:
        sess["_user_id"] = str(test_user.id)
    return client
