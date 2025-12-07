"""
Shift Scheduling models for staff management.
"""

from database.db import db
from datetime import datetime, date, time
from sqlalchemy import UniqueConstraint


class StaffProfile(db.Model):
    """Optional profile information for staff members"""

    __tablename__ = "staff_profiles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=False, unique=True
    )
    phone = db.Column(db.String(20), nullable=True)
    position = db.Column(
        db.String(100), nullable=True
    )  # e.g., "Part-time", "Full-time"
    hire_date = db.Column(db.Date, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    user = db.relationship("User", backref=db.backref("staff_profile", uselist=False))

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "phone": self.phone,
            "position": self.position,
            "hire_date": self.hire_date.isoformat() if self.hire_date else None,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class Shift(db.Model):
    """Defines available shift types"""

    __tablename__ = "shifts"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(
        db.String(100), nullable=False, unique=True
    )  # e.g., "Morning Prep", "Lunch Rush"
    start_time = db.Column(db.Time, nullable=False)  # e.g., 09:00:00
    end_time = db.Column(db.Time, nullable=False)  # e.g., 11:00:00
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    assignments = db.relationship(
        "ShiftAssignment", backref="shift", lazy="dynamic", cascade="all, delete-orphan"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "start_time": (
                self.start_time.strftime("%H:%M") if self.start_time else None
            ),
            "end_time": self.end_time.strftime("%H:%M") if self.end_time else None,
            "is_active": self.is_active,
        }

    def __repr__(self):
        return f"<Shift {self.name} ({self.start_time} - {self.end_time})>"


class ShiftAssignment(db.Model):
    """Assigns staff to shifts with specific roles"""

    __tablename__ = "shift_assignments"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    shift_id = db.Column(db.Integer, db.ForeignKey("shifts.id"), nullable=False)
    date = db.Column(db.Date, nullable=False)  # The date of the shift
    station_role = db.Column(
        db.String(50), nullable=False
    )  # Grill Master, Assembly, Counter/Cashier, Prep, Floater
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    user = db.relationship(
        "User", backref=db.backref("shift_assignments", lazy="dynamic")
    )

    # Ensure a user can only have one role per shift per day
    __table_args__ = (
        UniqueConstraint("user_id", "shift_id", "date", name="unique_user_shift_date"),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "user_name": self.user.username if self.user else None,
            "shift_id": self.shift_id,
            "shift_name": self.shift.name if self.shift else None,
            "shift_start": (
                self.shift.start_time.strftime("%H:%M")
                if self.shift and self.shift.start_time
                else None
            ),
            "shift_end": (
                self.shift.end_time.strftime("%H:%M")
                if self.shift and self.shift.end_time
                else None
            ),
            "date": self.date.isoformat() if self.date else None,
            "station_role": self.station_role,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f"<ShiftAssignment user_id={self.user_id} shift_id={self.shift_id} date={self.date} role={self.station_role}>"
