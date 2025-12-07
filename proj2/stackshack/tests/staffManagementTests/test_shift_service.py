"""
Test cases for shift service.
"""

from datetime import date, datetime, time
from models.shift import Shift, ShiftAssignment, StaffProfile
from models.user import User
from services.shift_service import ShiftService
from database.db import db


class TestShiftService:
    """Test cases for ShiftService."""

    def test_initialize_default_shifts(self, app):
        """Test initializing default shifts."""
        with app.app_context():
            count = ShiftService.initialize_default_shifts()
            assert count == 4  # Should create 4 default shifts

            shifts = ShiftService.get_all_shifts()
            assert len(shifts) == 4
            assert any(s.name == "Morning Prep" for s in shifts)
            assert any(s.name == "Lunch Rush" for s in shifts)

    def test_initialize_default_shifts_idempotent(self, app):
        """Test that initializing shifts multiple times doesn't create duplicates."""
        with app.app_context():
            ShiftService.initialize_default_shifts()
            count1 = len(ShiftService.get_all_shifts())

            ShiftService.initialize_default_shifts()
            count2 = len(ShiftService.get_all_shifts())

            assert count1 == count2

    def test_get_all_shifts(self, app, sample_shifts):
        """Test getting all active shifts."""
        with app.app_context():
            shifts = ShiftService.get_all_shifts()
            assert len(shifts) >= len(sample_shifts)

    def test_get_shift_by_id(self, app, sample_shifts):
        """Test getting a shift by ID."""
        with app.app_context():
            shift = ShiftService.get_shift_by_id(sample_shifts[0])
            assert shift is not None
            assert shift.id == sample_shifts[0]

    def test_create_shift(self, app):
        """Test creating a new shift."""
        with app.app_context():
            shift = ShiftService.create_shift("Test Shift", time(10, 0), time(12, 0))
            assert shift.id is not None
            assert shift.name == "Test Shift"

    def test_assign_shift(self, app, staff_user, sample_shifts):
        """Test assigning a staff member to a shift."""
        with app.app_context():
            today = date.today()
            assignment, message = ShiftService.assign_shift(
                staff_user, sample_shifts[0], today, "Grill Master"
            )

            assert assignment is not None
            assert assignment.user_id == staff_user
            assert assignment.shift_id == sample_shifts[0]
            assert assignment.station_role == "Grill Master"

    def test_get_all_staff(self, app, staff_user, admin_user):
        """Test getting all staff members."""
        with app.app_context():
            staff = ShiftService.get_all_staff()
            staff_ids = [s.id for s in staff]
            assert staff_user in staff_ids
            assert admin_user in staff_ids  # Admin is also staff

    def test_create_staff_profile(self, app, staff_user):
        """Test creating a staff profile."""
        with app.app_context():
            profile = ShiftService.create_staff_profile(
                staff_user, phone="123-456-7890", position="Part-time"
            )

            assert profile is not None
            assert profile.user_id == staff_user
            assert profile.phone == "123-456-7890"

    def test_remove_shift_assignment(self, app, staff_user, sample_shifts):
        """Test removing a shift assignment."""
        with app.app_context():
            today = date.today()
            assignment, _ = ShiftService.assign_shift(
                staff_user, sample_shifts[0], today, "Grill Master"
            )
            assignment_id = assignment.id

            success = ShiftService.remove_shift_assignment(assignment_id)
            assert success is True

            # Verify assignment is deleted
            deleted = db.session.get(ShiftAssignment, assignment_id)
            assert deleted is None
