"""
Helper Script: Add .edu Email to User Account
For testing campus card eligibility
"""
from app import create_app
from database.db import db
from models.user import User


def add_email_to_user(username, email):
    """Add email address to a user account"""
    app = create_app("development")
    
    with app.app_context():
        user = User.query.filter_by(username=username).first()
        
        if not user:
            print(f"❌ User '{username}' not found!")
            return
        
        user.email = email
        db.session.commit()
        
        print(f"✅ Updated user '{username}'")
        print(f"   Email: {email}")
        print(f"   Eligible for campus card: {user.is_eligible_for_campus_card()}")
        
        if user.is_eligible_for_campus_card():
            print(f"\n🎓 User can now create a campus card!")
        else:
            print(f"\n⚠️  Email does not end with .edu - not eligible for campus card")


def show_all_users():
    """Display all users and their email/eligibility status"""
    app = create_app("development")
    
    with app.app_context():
        users = User.query.all()
        
        print("=" * 80)
        print("ALL USERS - CAMPUS CARD ELIGIBILITY")
        print("=" * 80)
        
        for user in users:
            eligible = "✅ Eligible" if user.is_eligible_for_campus_card() else "❌ Not Eligible"
            email_display = user.email if user.email else "(No email)"
            print(f"\nUsername: {user.username}")
            print(f"Email: {email_display}")
            print(f"Eligibility: {eligible}")
        
        print("\n" + "=" * 80)


if __name__ == "__main__":
    import sys
    
    print("=" * 80)
    print("Campus Card Email Manager")
    print("=" * 80)
    
    if len(sys.argv) == 1:
        # No arguments - show all users
        show_all_users()
        print("\nUsage:")
        print("  python update_user_email.py <username> <email>")
        print("\nExamples:")
        print("  python update_user_email.py john john@university.edu")
        print("  python update_user_email.py demo_customer student@college.edu")
        print("  python update_user_email.py alice alice@mit.edu")
        
    elif len(sys.argv) == 3:
        # Add email to user
        username = sys.argv[1]
        email = sys.argv[2]
        add_email_to_user(username, email)
        
    else:
        print("❌ Invalid arguments!")
        print("\nUsage:")
        print("  python update_user_email.py                    # Show all users")
        print("  python update_user_email.py <username> <email> # Add email to user")

