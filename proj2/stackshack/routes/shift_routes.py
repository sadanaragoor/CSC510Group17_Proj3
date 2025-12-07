"""
Shift Scheduling routes for admin and staff.
"""
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import date, datetime, time, timedelta
from services.shift_service import ShiftService
from models.user import User
from models.shift import StaffProfile, Shift, ShiftAssignment
from database.db import db
from werkzeug.security import generate_password_hash

shift_bp = Blueprint("shift", __name__)


def admin_required(f):
    """Decorator to require admin role"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != "admin":
            flash("Admin access required.", "error")
            return redirect(url_for("auth.dashboard"))
        return f(*args, **kwargs)
    return decorated_function


def staff_required(f):
    """Decorator to require staff or admin role"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role not in ["admin", "staff"]:
            flash("Staff access required.", "error")
            return redirect(url_for("auth.dashboard"))
        return f(*args, **kwargs)
    return decorated_function


# ==================== ADMIN ROUTES ====================

@shift_bp.route("/admin/shifts", methods=["GET"])
@login_required
@admin_required
def admin_shifts_dashboard():
    """Admin dashboard for shift management"""
    # Initialize default shifts if needed
    ShiftService.initialize_default_shifts()
    
    # Get date range (default to today and next 6 days)
    view_date = request.args.get("date", date.today().isoformat())
    try:
        view_date = datetime.strptime(view_date, "%Y-%m-%d").date()
    except:
        view_date = date.today()
    
    week_start = view_date - timedelta(days=view_date.weekday())
    week_end = week_start + timedelta(days=6)
    
    # Get all shifts
    shifts = ShiftService.get_all_shifts()
    
    # Get all staff
    staff_members = ShiftService.get_all_staff()
    
    # Get assignments for the week
    assignments = ShiftService.get_assignments_for_week(week_start)
    
    # Organize assignments by date and shift
    schedule = {}
    for assignment in assignments:
        date_str = assignment.date.isoformat()
        if date_str not in schedule:
            schedule[date_str] = {}
        if assignment.shift_id not in schedule[date_str]:
            schedule[date_str][assignment.shift_id] = []
        schedule[date_str][assignment.shift_id].append(assignment)
    
    # Calculate all dates for the week
    week_dates = []
    for day_offset in range(7):
        current_date = week_start + timedelta(days=day_offset)
        week_dates.append({
            "date": current_date,
            "date_str": current_date.isoformat(),
            "formatted": current_date.strftime("%A, %B %d")
        })
    
    return render_template(
        "shifts/admin_dashboard.html",
        shifts=shifts,
        staff_members=staff_members,
        schedule=schedule,
        week_start=week_start,
        week_end=week_end,
        view_date=view_date,
        week_dates=week_dates,
        station_roles=ShiftService.STATION_ROLES
    )


@shift_bp.route("/admin/staff", methods=["GET"])
@login_required
@admin_required
def admin_staff_management():
    """Admin page for managing staff"""
    staff_members = ShiftService.get_all_staff()
    
    # Get profiles for each staff member
    staff_with_profiles = []
    for staff in staff_members:
        profile = StaffProfile.query.filter_by(user_id=staff.id).first()
        staff_with_profiles.append({
            "user": staff,
            "profile": profile
        })
    
    return render_template("shifts/admin_staff.html", staff_members=staff_with_profiles)


@shift_bp.route("/admin/staff/create", methods=["POST"])
@login_required
@admin_required
def create_staff():
    """Create a new staff account"""
    username = request.form.get("username")
    email = request.form.get("email")
    password = request.form.get("password")
    role = request.form.get("role", "staff")  # staff or admin
    phone = request.form.get("phone")
    position = request.form.get("position")
    
    if not username or not password:
        flash("Username and password are required.", "error")
        return redirect(url_for("shift.admin_staff_management"))
    
    # Check if username already exists
    if User.query.filter_by(username=username).first():
        flash("Username already exists.", "error")
        return redirect(url_for("shift.admin_staff_management"))
    
    # Create user
    user = User(username=username, email=email, role=role)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    
    # Create staff profile if phone or position provided
    if phone or position:
        ShiftService.create_staff_profile(user.id, phone=phone, position=position)
    
    flash(f"Staff member '{username}' created successfully.", "success")
    return redirect(url_for("shift.admin_staff_management"))


@shift_bp.route("/admin/staff/<int:user_id>/update", methods=["POST"])
@login_required
@admin_required
def update_staff(user_id):
    """Update staff member information"""
    user = db.session.get(User, user_id)
    if not user or user.role not in ["staff", "admin"]:
        flash("Staff member not found.", "error")
        return redirect(url_for("shift.admin_staff_management"))
    
    # Update user fields
    if request.form.get("email"):
        user.email = request.form.get("email")
    if request.form.get("role"):
        user.role = request.form.get("role")
    if request.form.get("password"):
        user.set_password(request.form.get("password"))
    
    # Update or create profile
    ShiftService.create_staff_profile(
        user.id,
        phone=request.form.get("phone"),
        position=request.form.get("position"),
        notes=request.form.get("notes")
    )
    
    db.session.commit()
    flash(f"Staff member '{user.username}' updated successfully.", "success")
    return redirect(url_for("shift.admin_staff_management"))


@shift_bp.route("/admin/staff/<int:user_id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_staff(user_id):
    """Delete a staff member (soft delete by changing role)"""
    user = db.session.get(User, user_id)
    if not user or user.role not in ["staff", "admin"]:
        flash("Staff member not found.", "error")
        return redirect(url_for("shift.admin_staff_management"))
    
    if user.id == current_user.id:
        flash("Cannot delete your own account.", "error")
        return redirect(url_for("shift.admin_staff_management"))
    
    # Change role to customer (soft delete)
    user.role = "customer"
    db.session.commit()
    
    flash(f"Staff member '{user.username}' removed.", "success")
    return redirect(url_for("shift.admin_staff_management"))


@shift_bp.route("/admin/shifts/assign", methods=["POST"])
@login_required
@admin_required
def assign_shift():
    """Assign a staff member to a shift"""
    user_id = request.form.get("user_id", type=int)
    shift_id = request.form.get("shift_id", type=int)
    assignment_date = request.form.get("date")
    station_role = request.form.get("station_role")
    
    if not all([user_id, shift_id, assignment_date, station_role]):
        return jsonify({"success": False, "error": "Missing required fields"}), 400
    
    try:
        assignment_date = datetime.strptime(assignment_date, "%Y-%m-%d").date()
    except:
        return jsonify({"success": False, "error": "Invalid date format"}), 400
    
    assignment, message = ShiftService.assign_shift(user_id, shift_id, assignment_date, station_role)
    if assignment:
        return jsonify({"success": True, "message": message, "assignment": assignment.to_dict()})
    else:
        return jsonify({"success": False, "error": message}), 400


@shift_bp.route("/admin/shifts/assignment/<int:assignment_id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_assignment(assignment_id):
    """Delete a shift assignment"""
    success = ShiftService.remove_shift_assignment(assignment_id)
    if success:
        flash("Shift assignment removed.", "success")
    else:
        flash("Assignment not found.", "error")
    
    return redirect(request.referrer or url_for("shift.admin_shifts_dashboard"))


# ==================== STAFF ROUTES ====================

@shift_bp.route("/staff/shifts", methods=["GET"])
@login_required
@staff_required
def staff_shifts_view():
    """Staff view of their upcoming shifts"""
    # Get upcoming shifts for current user
    upcoming_shifts = ShiftService.get_user_upcoming_shifts(current_user.id)
    
    # Organize by date
    shifts_by_date = {}
    for assignment in upcoming_shifts:
        date_str = assignment.date.isoformat()
        if date_str not in shifts_by_date:
            shifts_by_date[date_str] = []
        shifts_by_date[date_str].append(assignment)
    
    # Convert to sorted list of tuples for template, and format dates
    shifts_by_date_sorted = []
    for date_str, assignments in sorted(shifts_by_date.items()):
        # Parse date for formatting
        date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
        formatted_date = date_obj.strftime("%A, %B %d, %Y")
        shifts_by_date_sorted.append((date_str, assignments, formatted_date))
    
    return render_template("shifts/staff_dashboard.html", shifts_by_date=shifts_by_date_sorted)


# ==================== API ROUTES ====================

@shift_bp.route("/api/shifts", methods=["GET"])
@login_required
@admin_required
def api_get_shifts():
    """API: Get all shifts"""
    shifts = ShiftService.get_all_shifts()
    return jsonify({"shifts": [shift.to_dict() for shift in shifts]})


@shift_bp.route("/api/assignments", methods=["GET"])
@login_required
@admin_required
def api_get_assignments():
    """API: Get assignments for a date range"""
    start_date = request.args.get("start_date", date.today().isoformat())
    end_date = request.args.get("end_date", start_date)
    
    try:
        start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
        end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
    except:
        return jsonify({"error": "Invalid date format"}), 400
    
    assignments = ShiftAssignment.query.filter(
        and_(
            ShiftAssignment.date >= start_date,
            ShiftAssignment.date <= end_date
        )
    ).all()
    
    return jsonify({"assignments": [a.to_dict() for a in assignments]})

