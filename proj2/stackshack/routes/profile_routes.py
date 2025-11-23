"""
Profile Routes
User profile management including email updates
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from database.db import db
from models.user import User

profile_bp = Blueprint("profile", __name__)


@profile_bp.route("/profile", methods=["GET"])
@login_required
def view_profile():
    """View user profile"""
    return render_template("profile/profile.html", user=current_user)


@profile_bp.route("/profile/update-email", methods=["POST"])
@login_required
def update_email():
    """Update user email address"""
    try:
        new_email = request.form.get("email", "").strip()
        
        if not new_email:
            flash("Please enter an email address", "error")
            return redirect(url_for("profile.view_profile"))
        
        # Basic email validation
        if "@" not in new_email or "." not in new_email:
            flash("Please enter a valid email address", "error")
            return redirect(url_for("profile.view_profile"))
        
        # Update email
        current_user.email = new_email
        db.session.commit()
        
        # Check if now eligible for campus card
        if current_user.is_eligible_for_campus_card():
            flash(f"Email updated successfully! You are now eligible for a campus card. 🎓", "success")
        else:
            flash(f"Email updated successfully!", "success")
            
        return redirect(url_for("profile.view_profile"))
        
    except Exception as e:
        db.session.rollback()
        flash(f"Error updating email: {str(e)}", "error")
        return redirect(url_for("profile.view_profile"))


@profile_bp.route("/profile/update-password", methods=["POST"])
@login_required
def update_password():
    """Update user password"""
    try:
        current_password = request.form.get("current_password")
        new_password = request.form.get("new_password")
        confirm_password = request.form.get("confirm_password")
        
        # Validate inputs
        if not current_password or not new_password or not confirm_password:
            flash("All password fields are required", "error")
            return redirect(url_for("profile.view_profile"))
        
        # Check current password
        if not current_user.check_password(current_password):
            flash("Current password is incorrect", "error")
            return redirect(url_for("profile.view_profile"))
        
        # Check new passwords match
        if new_password != confirm_password:
            flash("New passwords do not match", "error")
            return redirect(url_for("profile.view_profile"))
        
        # Update password
        current_user.set_password(new_password)
        db.session.commit()
        
        flash("Password updated successfully!", "success")
        return redirect(url_for("profile.view_profile"))
        
    except Exception as e:
        db.session.rollback()
        flash(f"Error updating password: {str(e)}", "error")
        return redirect(url_for("profile.view_profile"))


@profile_bp.route("/profile/update-preferences", methods=["POST"])
@login_required
def update_preferences():
    """Update user dietary preferences"""
    try:
        # Get checkbox values (checkboxes not checked won't be in form data)
        pref_vegan = 'pref_vegan' in request.form
        pref_gluten_free = 'pref_gluten_free' in request.form
        pref_high_protein = 'pref_high_protein' in request.form
        pref_low_calorie = 'pref_low_calorie' in request.form
        
        # Update user preferences
        current_user.pref_vegan = pref_vegan
        current_user.pref_gluten_free = pref_gluten_free
        current_user.pref_high_protein = pref_high_protein
        current_user.pref_low_calorie = pref_low_calorie
        
        db.session.commit()
        
        # Build message based on selected preferences
        selected_prefs = []
        if pref_vegan:
            selected_prefs.append("Vegan")
        if pref_gluten_free:
            selected_prefs.append("Gluten-Free")
        if pref_high_protein:
            selected_prefs.append("High-Protein")
        if pref_low_calorie:
            selected_prefs.append("Low-Calorie")
        
        if selected_prefs:
            prefs_text = ", ".join(selected_prefs)
            flash(f"Preferences updated! You'll now see {prefs_text} recommendations on your dashboard. 🍔", "success")
        else:
            flash("Preferences cleared! You'll see our top picks on your dashboard. 🍔", "success")
        
        return redirect(url_for("auth.dashboard"))  # Redirect to dashboard to see new recommendations
        
    except Exception as e:
        db.session.rollback()
        flash(f"Error updating preferences: {str(e)}", "error")
        return redirect(url_for("profile.view_profile"))

