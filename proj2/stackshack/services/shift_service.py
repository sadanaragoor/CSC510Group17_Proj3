"""
Shift Scheduling Service - Handles shift management and assignments.
"""
from models.shift import StaffProfile, Shift, ShiftAssignment
from models.user import User
from database.db import db
from datetime import date, datetime, time, timedelta
from sqlalchemy import and_, or_


class ShiftService:
    """Service for managing shifts and staff assignments"""
    
    # Available station roles
    STATION_ROLES = [
        "Grill Master",
        "Assembly",
        "Counter/Cashier",
        "Prep",
        "Floater"
    ]
    
    @staticmethod
    def initialize_default_shifts():
        """Initialize default shifts if they don't exist"""
        default_shifts = [
            {"name": "Morning Prep", "start_time": time(9, 0), "end_time": time(11, 0)},
            {"name": "Lunch Rush", "start_time": time(11, 0), "end_time": time(14, 0)},
            {"name": "Afternoon", "start_time": time(14, 0), "end_time": time(18, 0)},
            {"name": "Dinner/Closing", "start_time": time(18, 0), "end_time": time(22, 0)},
        ]
        
        created = 0
        for shift_data in default_shifts:
            existing = Shift.query.filter_by(name=shift_data["name"]).first()
            if not existing:
                shift = Shift(
                    name=shift_data["name"],
                    start_time=shift_data["start_time"],
                    end_time=shift_data["end_time"],
                    is_active=True
                )
                db.session.add(shift)
                created += 1
        
        if created > 0:
            db.session.commit()
        
        return created
    
    @staticmethod
    def get_all_shifts():
        """Get all active shifts"""
        return Shift.query.filter_by(is_active=True).order_by(Shift.start_time).all()
    
    @staticmethod
    def get_shift_by_id(shift_id):
        """Get a shift by ID"""
        return db.session.get(Shift, shift_id)
    
    @staticmethod
    def create_shift(name, start_time, end_time):
        """Create a new shift"""
        shift = Shift(
            name=name,
            start_time=start_time,
            end_time=end_time,
            is_active=True
        )
        db.session.add(shift)
        db.session.commit()
        return shift
    
    @staticmethod
    def update_shift(shift_id, name=None, start_time=None, end_time=None, is_active=None):
        """Update a shift"""
        shift = db.session.get(Shift, shift_id)
        if not shift:
            return None
        
        if name is not None:
            shift.name = name
        if start_time is not None:
            shift.start_time = start_time
        if end_time is not None:
            shift.end_time = end_time
        if is_active is not None:
            shift.is_active = is_active
        
        db.session.commit()
        return shift
    
    @staticmethod
    def delete_shift(shift_id):
        """Delete a shift (soft delete by setting is_active=False)"""
        shift = db.session.get(Shift, shift_id)
        if not shift:
            return False
        
        shift.is_active = False
        db.session.commit()
        return True
    
    @staticmethod
    def get_all_staff():
        """Get all staff members (users with role 'staff' or 'admin')"""
        return User.query.filter(User.role.in_(["staff", "admin"])).all()
    
    @staticmethod
    def get_staff_by_id(user_id):
        """Get a staff member by user ID"""
        user = db.session.get(User, user_id)
        if user and user.role in ["staff", "admin"]:
            return user
        return None
    
    @staticmethod
    def create_staff_profile(user_id, phone=None, position=None, hire_date=None, notes=None):
        """Create or update staff profile"""
        profile = StaffProfile.query.filter_by(user_id=user_id).first()
        if not profile:
            profile = StaffProfile(user_id=user_id)
            db.session.add(profile)
        
        if phone is not None:
            profile.phone = phone
        if position is not None:
            profile.position = position
        if hire_date is not None:
            profile.hire_date = hire_date
        if notes is not None:
            profile.notes = notes
        
        db.session.commit()
        return profile
    
    @staticmethod
    def assign_shift(user_id, shift_id, assignment_date, station_role):
        """Assign a staff member to a shift"""
        if station_role not in ShiftService.STATION_ROLES:
            return None, "Invalid station role"
        
        # Check if assignment already exists
        existing = ShiftAssignment.query.filter_by(
            user_id=user_id,
            shift_id=shift_id,
            date=assignment_date
        ).first()
        
        if existing:
            # Update existing assignment
            existing.station_role = station_role
            db.session.commit()
            return existing, "Assignment updated"
        else:
            # Create new assignment
            assignment = ShiftAssignment(
                user_id=user_id,
                shift_id=shift_id,
                date=assignment_date,
                station_role=station_role
            )
            db.session.add(assignment)
            db.session.commit()
            return assignment, "Assignment created"
    
    @staticmethod
    def remove_shift_assignment(assignment_id):
        """Remove a shift assignment"""
        assignment = db.session.get(ShiftAssignment, assignment_id)
        if not assignment:
            return False
        
        db.session.delete(assignment)
        db.session.commit()
        return True
    
    @staticmethod
    def get_assignments_for_date(assignment_date):
        """Get all shift assignments for a specific date"""
        return ShiftAssignment.query.filter_by(date=assignment_date).all()
    
    @staticmethod
    def get_assignments_for_week(week_start_date):
        """Get all shift assignments for a week (starting from week_start_date)"""
        week_end_date = week_start_date + timedelta(days=6)
        return ShiftAssignment.query.filter(
            and_(
                ShiftAssignment.date >= week_start_date,
                ShiftAssignment.date <= week_end_date
            )
        ).all()
    
    @staticmethod
    def get_user_upcoming_shifts(user_id, start_date=None):
        """Get upcoming shifts for a specific user"""
        if start_date is None:
            start_date = date.today()
        
        return ShiftAssignment.query.filter(
            and_(
                ShiftAssignment.user_id == user_id,
                ShiftAssignment.date >= start_date
            )
        ).order_by(ShiftAssignment.date, Shift.start_time).join(Shift).all()
    
    @staticmethod
    def get_schedule_table(start_date, end_date=None):
        """Get schedule in table format for date range"""
        if end_date is None:
            end_date = start_date
        
        assignments = ShiftAssignment.query.filter(
            and_(
                ShiftAssignment.date >= start_date,
                ShiftAssignment.date <= end_date
            )
        ).join(Shift).join(User).all()
        
        # Organize by date and shift
        schedule = {}
        for assignment in assignments:
            date_str = assignment.date.isoformat()
            if date_str not in schedule:
                schedule[date_str] = {}
            if assignment.shift_id not in schedule[date_str]:
                schedule[date_str][assignment.shift_id] = []
            schedule[date_str][assignment.shift_id].append(assignment)
        
        return schedule

