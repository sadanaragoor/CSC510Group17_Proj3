from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from controllers.auth_controller import AuthController
from database.db import db


auth_bp = Blueprint("auth", __name__)


# User registration
@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    """
    Handles user registration. Renders the registration form on GET.
    Processes form data on POST, defaulting to 'customer' role unless
    an admin is currently logged in.
    """
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        role = "customer"

        if current_user.is_authenticated and current_user.role == "admin":
            role = request.form.get("role", "customer")

        # NEW: get dietary preferences from form
        dietary_prefs = request.form.getlist("dietary_preferences")
        if "no_preference" in dietary_prefs:
            # treat "no preference" as no filters
            dietary_prefs = []

        # ✅ Call AuthController as it was originally (3 args only)
        success, msg, user = AuthController.register_user(username, password, role)
        if success and user:
            # Now apply preferences to the saved user
            user.pref_vegan = "vegan" in dietary_prefs
            user.pref_gluten_free = "gluten_free" in dietary_prefs
            user.pref_high_protein = "high_protein" in dietary_prefs
            user.pref_low_calorie = "low_calorie" in dietary_prefs

            db.session.commit()

        flash(msg, "success" if success else "error")

        if success:
            return redirect(url_for("auth.login"))

    return render_template("register.html")


# Login route
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """
    Handles user login. Redirects logged-in users to the dashboard.
    Processes login form data on POST and establishes the user session upon success.
    """
    if current_user.is_authenticated:
        return redirect(url_for("auth.dashboard"))

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        success, msg, _ = AuthController.login_user_account(username, password)
        flash(msg, "success" if success else "error")

        if success:
            return redirect(url_for("auth.dashboard"))
    return render_template("login.html")


# Dashboard
@auth_bp.route("/dashboard")
@login_required
def dashboard():
    """
    The main dashboard page, accessible only to logged-in users.
    Displays user-specific information and admin links if applicable.
    """
    from services.burger_recommendations import BurgerRecommendationService

    # Get personalized burger recommendations
    burger_sections = BurgerRecommendationService.get_recommendations_for_user(
        current_user
    )

    return render_template(
        "dashboard.html", user=current_user, burger_sections=burger_sections
    )


# Logout
@auth_bp.route("/logout")
@login_required
def logout():
    """
    Logs out the current user and redirects to the login page.
    """
    success, msg = AuthController.logout_user_account()
    flash(msg, "success")
    return redirect(url_for("auth.login"))


# Admin-only: Create users
@auth_bp.route("/admin/create-user", methods=["GET", "POST"])
@login_required
def create_user_admin():
    """
    Admin-only route to create new staff or admin users directly.
    Requires current user role to be 'admin'.
    """
    if current_user.role != "admin":
        flash("Unauthorized access", "error")
        return redirect(url_for("auth.dashboard"))

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        role = request.form.get("role", "staff")

        success, msg, _ = AuthController.register_user(username, password, role)
        flash(msg, "success" if success else "error")

    return render_template("admin_create.html")


# Admin-only: Manage users (view, edit, delete)
@auth_bp.route("/admin/manage-users", methods=["GET", "POST"])
@login_required
def manage_users():
    """
    Admin-only route to view all users, update user roles, and delete accounts.
    Requires current user role to be 'admin'.
    """
    if current_user.role != "admin":
        flash("Unauthorized access", "error")
        return redirect(url_for("auth.dashboard"))

    users = AuthController.get_all_users()

    if request.method == "POST":
        if "update_role" in request.form:
            user_id = request.form.get("user_id")
            new_role = request.form.get("role")

            success, msg = AuthController.update_user_role(user_id, new_role)
            flash(msg, "success" if success else "error")

        elif "delete_user" in request.form:
            user_id = request.form.get("user_id")

            success, msg = AuthController.delete_user(user_id)
            flash(msg, "success" if success else "error")

        return redirect(url_for("auth.manage_users"))

    return render_template("admin_manage.html", users=users)
