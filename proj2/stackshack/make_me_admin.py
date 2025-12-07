"""
Quick Script: Make User an Admin
Run this to give yourself admin access to the payment dashboard
"""
from app import create_app
from database.db import db
from models.user import User


def make_admin(username):
    """Make a user an admin"""
    app = create_app("development")
    
    with app.app_context():
        user = User.query.filter_by(username=username).first()
        
        if not user:
            print(f"❌ User '{username}' not found!")
            return
        
        old_role = user.role
        user.role = "admin"
        db.session.commit()
        
        print(f"✅ Success!")
        print(f"   User: {username}")
        print(f"   Old Role: {old_role}")
        print(f"   New Role: admin")
        print(f"\nYou can now access:")
        print(f"   • Admin Payment Dashboard: /payment/admin/dashboard")
        print(f"   • View all transactions")
        print(f"   • Filter by time period")
        print(f"   • See payment statistics")


if __name__ == "__main__":
    import sys
    
    print("=" * 60)
    print("Make User Admin")
    print("=" * 60)
    
    if len(sys.argv) == 2:
        username = sys.argv[1]
        make_admin(username)
    else:
        print("\nUsage: python make_me_admin.py <username>")
        print("\nExample:")
        print("  python make_me_admin.py sadana21")
        print("\nOr just run and enter your username:")
        username = input("\nEnter your username: ").strip()
        if username:
            make_admin(username)

