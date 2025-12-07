"""
Fixtures for staff management and shift scheduling tests.
"""
import pytest
import sys
import os
from datetime import date, datetime, time

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from app import create_app
from database.db import db
from models.user import User
from models.shift import StaffProfile, Shift, ShiftAssignment


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
def staff_user(app):
    """Create a staff user for testing."""
    with app.app_context():
        user = User(username="staff1", email="staff1@test.com", role="staff")
        user.set_password("staffpass")
        db.session.add(user)
        db.session.commit()
        return user.id


@pytest.fixture(scope="function")
def customer_user(app):
    """Create a customer user for testing."""
    with app.app_context():
        user = User(username="customer1", email="customer1@test.com", role="customer")
        user.set_password("customerpass")
        db.session.add(user)
        db.session.commit()
        return user.id


@pytest.fixture(scope="function")
def sample_shifts(app):
    """Create sample shifts for testing."""
    with app.app_context():
        shifts = [
            Shift(name="Morning Prep", start_time=time(9, 0), end_time=time(11, 0), is_active=True),
            Shift(name="Lunch Rush", start_time=time(11, 0), end_time=time(14, 0), is_active=True),
            Shift(name="Afternoon", start_time=time(14, 0), end_time=time(18, 0), is_active=True),
            Shift(name="Dinner/Closing", start_time=time(18, 0), end_time=time(22, 0), is_active=True),
        ]
        for shift in shifts:
            db.session.add(shift)
        db.session.commit()
        return [shift.id for shift in shifts]


@pytest.fixture(scope="function")
def sample_assignments(app, admin_user, staff_user, sample_shifts):
    """Create sample shift assignments for testing."""
    with app.app_context():
        today = date.today()
        assignments = [
            ShiftAssignment(
                user_id=staff_user,
                shift_id=sample_shifts[0],
                date=today,
                station_role="Grill Master"
            ),
            ShiftAssignment(
                user_id=staff_user,
                shift_id=sample_shifts[1],
                date=today + timedelta(days=1),
                station_role="Counter/Cashier"
            ),
        ]
        for assignment in assignments:
            db.session.add(assignment)
        db.session.commit()
        return [assignment.id for assignment in assignments]


@pytest.fixture(scope="function")
def authenticated_admin_client(client, app, admin_user):
    """Create an authenticated admin test client."""
    with app.app_context():
        user = db.session.get(User, admin_user)
        from flask_login import login_user
        
        with client:
            with app.test_request_context():
                login_user(user)
            yield client


@pytest.fixture(scope="function")
def authenticated_staff_client(client, app, staff_user):
    """Create an authenticated staff test client."""
    with app.app_context():
        user = db.session.get(User, staff_user)
        from flask_login import login_user
        
        with client:
            with app.test_request_context():
                login_user(user)
            yield client

