"""
Test cases for shift scheduling models.
"""
from datetime import date, datetime, time
from models.shift import StaffProfile, Shift, ShiftAssignment
from database.db import db


class TestShiftModel:
    """Test cases for Shift model."""
    
    def test_create_shift(self, app):
        """Test creating a shift."""
        with app.app_context():
            shift = Shift(
                name="Morning Prep",
                start_time=time(9, 0),
                end_time=time(11, 0),
                is_active=True
            )
            db.session.add(shift)
            db.session.commit()
            
            assert shift.id is not None
            assert shift.name == "Morning Prep"
            assert shift.start_time == time(9, 0)
            assert shift.end_time == time(11, 0)
            assert shift.is_active is True
    
    def test_shift_to_dict(self, app):
        """Test shift serialization."""
        with app.app_context():
            shift = Shift(
                name="Lunch Rush",
                start_time=time(11, 0),
                end_time=time(14, 0),
                is_active=True
            )
            db.session.add(shift)
            db.session.commit()
            
            shift_dict = shift.to_dict()
            assert shift_dict["name"] == "Lunch Rush"
            assert shift_dict["start_time"] == "11:00"
            assert shift_dict["end_time"] == "14:00"
    
    def test_shift_unique_name(self, app):
        """Test that shift names must be unique."""
        with app.app_context():
            shift1 = Shift(name="Test Shift", start_time=time(9, 0), end_time=time(11, 0))
            db.session.add(shift1)
            db.session.commit()
            
            shift2 = Shift(name="Test Shift", start_time=time(12, 0), end_time=time(14, 0))
            db.session.add(shift2)
            
            import pytest
            from sqlalchemy.exc import IntegrityError
            with pytest.raises(IntegrityError):
                db.session.commit()


class TestShiftAssignmentModel:
    """Test cases for ShiftAssignment model."""
    
    def test_create_assignment(self, app, staff_user, sample_shifts):
        """Test creating a shift assignment."""
        with app.app_context():
            assignment = ShiftAssignment(
                user_id=staff_user,
                shift_id=sample_shifts[0],
                date=date.today(),
                station_role="Grill Master"
            )
            db.session.add(assignment)
            db.session.commit()
            
            assert assignment.id is not None
            assert assignment.user_id == staff_user
            assert assignment.shift_id == sample_shifts[0]
            assert assignment.station_role == "Grill Master"
    
    def test_assignment_to_dict(self, app, staff_user, sample_shifts):
        """Test assignment serialization."""
        with app.app_context():
            assignment = ShiftAssignment(
                user_id=staff_user,
                shift_id=sample_shifts[0],
                date=date.today(),
                station_role="Counter/Cashier"
            )
            db.session.add(assignment)
            db.session.commit()
            
            assignment_dict = assignment.to_dict()
            assert assignment_dict["user_id"] == staff_user
            assert assignment_dict["station_role"] == "Counter/Cashier"
            assert assignment_dict["date"] == date.today().isoformat()
    
    def test_assignment_unique_constraint(self, app, staff_user, sample_shifts):
        """Test that a user can only have one role per shift per day."""
        with app.app_context():
            today = date.today()
            assignment1 = ShiftAssignment(
                user_id=staff_user,
                shift_id=sample_shifts[0],
                date=today,
                station_role="Grill Master"
            )
            db.session.add(assignment1)
            db.session.commit()
            
            # Try to create duplicate assignment
            assignment2 = ShiftAssignment(
                user_id=staff_user,
                shift_id=sample_shifts[0],
                date=today,
                station_role="Assembly"
            )
            db.session.add(assignment2)
            
            import pytest
            from sqlalchemy.exc import IntegrityError
            with pytest.raises(IntegrityError):
                db.session.commit()
    
class TestStaffProfileModel:
    """Test cases for StaffProfile model."""
    
    def test_create_staff_profile(self, app, staff_user):
        """Test creating a staff profile."""
        with app.app_context():
            profile = StaffProfile(
                user_id=staff_user,
                phone="123-456-7890",
                position="Part-time",
                hire_date=date.today()
            )
            db.session.add(profile)
            db.session.commit()
            
            assert profile.id is not None
            assert profile.user_id == staff_user
            assert profile.phone == "123-456-7890"
            assert profile.position == "Part-time"
    
    def test_staff_profile_to_dict(self, app, staff_user):
        """Test staff profile serialization."""
        with app.app_context():
            profile = StaffProfile(
                user_id=staff_user,
                phone="123-456-7890",
                position="Full-time"
            )
            db.session.add(profile)
            db.session.commit()
            
            profile_dict = profile.to_dict()
            assert profile_dict["user_id"] == staff_user
            assert profile_dict["phone"] == "123-456-7890"
            assert profile_dict["position"] == "Full-time"
    
    def test_staff_profile_unique_user(self, app, staff_user):
        """Test that a user can only have one staff profile."""
        with app.app_context():
            profile1 = StaffProfile(user_id=staff_user, phone="123-456-7890")
            db.session.add(profile1)
            db.session.commit()
            
            profile2 = StaffProfile(user_id=staff_user, phone="987-654-3210")
            db.session.add(profile2)
            
            import pytest
            from sqlalchemy.exc import IntegrityError
            with pytest.raises(IntegrityError):
                db.session.commit()

