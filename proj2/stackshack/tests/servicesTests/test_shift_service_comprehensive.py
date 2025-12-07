"""
Comprehensive shift service tests to increase coverage.
"""

from datetime import date, time, timedelta
from models.shift import Shift, ShiftAssignment, StaffProfile
from models.user import User
from services.shift_service import ShiftService
from database.db import db


class TestShiftServiceComprehensive:
    """Comprehensive shift service tests."""

    def test_initialize_default_shifts_idempotent(self, app):
        """Test that initializing shifts multiple times doesn't create duplicates."""
        with app.app_context():
            ShiftService.initialize_default_shifts()
            count1 = len(Shift.query.all())

            ShiftService.initialize_default_shifts()
            count2 = len(Shift.query.all())

            # Should have same number of shifts
            assert count1 == count2

    def test_get_all_shifts(self, app):
        """Test getting all shifts."""
        with app.app_context():
            ShiftService.initialize_default_shifts()
            shifts = ShiftService.get_all_shifts()

            assert len(shifts) > 0
            assert all(shift.is_active for shift in shifts)

    def test_get_all_staff(self, app):
        """Test getting all staff members."""
        with app.app_context():
            # Create staff users
            staff1 = User(username="staff1", email="staff1@test.com", role="staff")
            staff1.set_password("pass")
            staff2 = User(username="staff2", email="staff2@test.com", role="staff")
            staff2.set_password("pass")
            admin = User(username="admin", email="admin@test.com", role="admin")
            admin.set_password("pass")
            db.session.add_all([staff1, staff2, admin])
            db.session.commit()

            staff_members = ShiftService.get_all_staff()

            # Should include both staff and admin
            assert len(staff_members) >= 3
            assert any(u.username == "staff1" for u in staff_members)
            assert any(u.username == "admin" for u in staff_members)

    def test_assign_shift(self, app):
        """Test assigning a shift."""
        with app.app_context():
            ShiftService.initialize_default_shifts()
            shifts = ShiftService.get_all_shifts()

            staff = User(username="staff1", email="staff1@test.com", role="staff")
            staff.set_password("pass")
            db.session.add(staff)
            db.session.commit()

            today = date.today()
            assignment, message = ShiftService.assign_shift(
                staff.id, shifts[0].id, today, "Grill Master"
            )

            assert assignment is not None
            assert assignment.user_id == staff.id
            assert assignment.shift_id == shifts[0].id
            assert assignment.station_role == "Grill Master"

    def test_delete_assignment(self, app):
        """Test deleting an assignment."""
        with app.app_context():
            ShiftService.initialize_default_shifts()
            shifts = ShiftService.get_all_shifts()

            staff = User(username="staff1", email="staff1@test.com", role="staff")
            staff.set_password("pass")
            db.session.add(staff)
            db.session.commit()

            today = date.today()
            assignment, message = ShiftService.assign_shift(
                staff.id, shifts[0].id, today, "Grill Master"
            )
            assignment_id = assignment.id

            success = ShiftService.remove_shift_assignment(assignment_id)

            assert success is True
            deleted = db.session.get(ShiftAssignment, assignment_id)
            assert deleted is None

    def test_get_assignments_for_day(self, app):
        """Test getting assignments for a specific day."""
        with app.app_context():
            ShiftService.initialize_default_shifts()
            shifts = ShiftService.get_all_shifts()

            staff = User(username="staff1", email="staff1@test.com", role="staff")
            staff.set_password("pass")
            db.session.add(staff)
            db.session.commit()

            today = date.today()
            ShiftService.assign_shift(staff.id, shifts[0].id, today, "Grill Master")

            # Use get_assignments_for_date if that's the actual method name
            assignments = ShiftService.get_assignments_for_date(today)

            assert len(assignments) > 0
            assert all(a.date == today for a in assignments)

    def test_get_assignments_for_week(self, app):
        """Test getting assignments for a week."""
        with app.app_context():
            ShiftService.initialize_default_shifts()
            shifts = ShiftService.get_all_shifts()

            staff = User(username="staff1", email="staff1@test.com", role="staff")
            staff.set_password("pass")
            db.session.add(staff)
            db.session.commit()

            days_since_monday = date.today().weekday()
            week_start = date.today() - timedelta(days=days_since_monday)

            # Create assignments for multiple days
            for i in range(3):
                ShiftService.assign_shift(
                    staff.id,
                    shifts[0].id,
                    week_start + timedelta(days=i),
                    "Grill Master",
                )[
                    0
                ]  # Get assignment from tuple

            assignments = ShiftService.get_assignments_for_week(week_start)

            assert len(assignments) >= 3

    def test_get_user_upcoming_shifts(self, app):
        """Test getting user's upcoming shifts."""
        with app.app_context():
            ShiftService.initialize_default_shifts()
            shifts = ShiftService.get_all_shifts()

            staff = User(username="staff1", email="staff1@test.com", role="staff")
            staff.set_password("pass")
            db.session.add(staff)
            db.session.commit()

            # Create shifts for past week and future
            days_since_monday = date.today().weekday()
            week_start = date.today() - timedelta(days=days_since_monday)

            # Past shift
            ShiftService.assign_shift(
                staff.id, shifts[0].id, week_start - timedelta(days=1), "Grill Master"
            )[
                0
            ]  # Get assignment from tuple
            # Future shift
            ShiftService.assign_shift(
                staff.id, shifts[0].id, week_start + timedelta(days=2), "Grill Master"
            )[
                0
            ]  # Get assignment from tuple

            start_date = date.today() - timedelta(days=7)
            upcoming = ShiftService.get_user_upcoming_shifts(
                staff.id, start_date=start_date
            )

            assert len(upcoming) >= 1

    def test_create_staff_profile(self, app):
        """Test creating a staff profile."""
        with app.app_context():
            staff = User(username="staff1", email="staff1@test.com", role="staff")
            staff.set_password("pass")
            db.session.add(staff)
            db.session.commit()

            profile = ShiftService.create_staff_profile(
                staff.id, phone="123-456-7890", position="Team Lead"
            )

            assert profile is not None
            assert profile.user_id == staff.id
            assert profile.position == "Team Lead"

    def test_create_staff_profile_update_existing(self, app):
        """Test creating/updating an existing staff profile."""
        with app.app_context():
            staff = User(username="staff1", email="staff1@test.com", role="staff")
            staff.set_password("pass")
            db.session.add(staff)
            db.session.commit()

            # Create initial profile
            profile1 = ShiftService.create_staff_profile(
                staff.id, phone="123-456-7890", position="Junior"
            )

            # Update it
            profile2 = ShiftService.create_staff_profile(
                staff.id, phone="999-999-9999", position="Senior"
            )

            assert profile1.id == profile2.id  # Same profile
            assert profile2.position == "Senior"

    def test_get_shift_by_id(self, app):
        """Test getting shift by ID."""
        with app.app_context():
            ShiftService.initialize_default_shifts()
            shifts = ShiftService.get_all_shifts()

            shift = ShiftService.get_shift_by_id(shifts[0].id)

            assert shift is not None
            assert shift.id == shifts[0].id

    def test_create_shift(self, app):
        """Test creating a new shift."""
        with app.app_context():
            shift = ShiftService.create_shift("Test Shift", time(10, 0), time(12, 0))

            assert shift is not None
            assert shift.name == "Test Shift"

    def test_update_shift(self, app):
        """Test updating a shift."""
        with app.app_context():
            ShiftService.initialize_default_shifts()
            shifts = ShiftService.get_all_shifts()

            updated = ShiftService.update_shift(
                shifts[0].id, name="Updated Shift", is_active=True
            )

            assert updated is not None
            assert updated.name == "Updated Shift"

    def test_delete_shift(self, app):
        """Test deleting a shift (soft delete)."""
        with app.app_context():
            ShiftService.initialize_default_shifts()
            shifts = ShiftService.get_all_shifts()

            success = ShiftService.delete_shift(shifts[0].id)

            assert success is True
            db.session.refresh(shifts[0])
            assert shifts[0].is_active is False

    def test_get_staff_by_id(self, app):
        """Test getting staff by ID."""
        with app.app_context():
            staff = User(username="staff1", email="staff1@test.com", role="staff")
            staff.set_password("pass")
            db.session.add(staff)
            db.session.commit()

            found = ShiftService.get_staff_by_id(staff.id)

            assert found is not None
            assert found.id == staff.id

    def test_get_schedule_table(self, app):
        """Test getting schedule table."""
        with app.app_context():
            ShiftService.initialize_default_shifts()
            shifts = ShiftService.get_all_shifts()

            staff = User(username="staff1", email="staff1@test.com", role="staff")
            staff.set_password("pass")
            db.session.add(staff)
            db.session.commit()

            today = date.today()
            ShiftService.assign_shift(staff.id, shifts[0].id, today, "Grill Master")[0]

            schedule = ShiftService.get_schedule_table(today, today)

            assert isinstance(schedule, dict)
