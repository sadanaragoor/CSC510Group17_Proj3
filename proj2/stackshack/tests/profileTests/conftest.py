"""
Fixtures for profile tests.
"""

import pytest
import sys
import os

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from app import create_app
from database.db import db
from models.user import User
from werkzeug.security import generate_password_hash


@pytest.fixture
def app():
    """Create application for testing"""
    app = create_app()
    app.config.update(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "WTF_CSRF_ENABLED": False,
            "SECRET_KEY": "test-secret-key",
        }
    )

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()


@pytest.fixture
def test_user(app):
    """Create a test user."""
    with app.app_context():
        user = User(
            username="testuser",
            password_hash=generate_password_hash("testpassword123"),
            role="customer",
            email="test@example.com",
        )
        db.session.add(user)
        db.session.commit()
        yield user.id
