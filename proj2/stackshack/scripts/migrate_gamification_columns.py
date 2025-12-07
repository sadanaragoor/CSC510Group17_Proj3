"""
Migration script to add gamification columns to the users table.
Run this script to add tier, total_points, and birthday columns.
"""

import sys
import os

# Add the parent directory to the path so we can import from stackshack
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app
from database.db import db
from sqlalchemy import text, inspect


def migrate_users_table():
    """Add gamification columns to users table"""
    app = create_app("development")

    with app.app_context():
        print("=" * 80)
        print("MIGRATING USERS TABLE - ADDING GAMIFICATION COLUMNS")
        print("=" * 80)

        try:
            # Check if columns already exist
            from sqlalchemy import inspect as sqlalchemy_inspect

            inspector = sqlalchemy_inspect(db.engine)
            columns = [col["name"] for col in inspector.get_columns("users")]

            print("\n[+] Current columns in users table:")
            for col in columns:
                print(f"  - {col}")

            # Add tier column if it doesn't exist
            if "tier" not in columns:
                print("\n[+] Adding 'tier' column...")
                db.session.execute(
                    text(
                        """
                    ALTER TABLE users 
                    ADD COLUMN tier VARCHAR(20) DEFAULT 'Bronze' 
                    AFTER pref_low_calorie
                """
                    )
                )
                print("  ✓ Added 'tier' column")
            else:
                print("\n[!] 'tier' column already exists")

            # Add total_points column if it doesn't exist
            if "total_points" not in columns:
                print("\n[+] Adding 'total_points' column...")
                db.session.execute(
                    text(
                        """
                    ALTER TABLE users 
                    ADD COLUMN total_points INT DEFAULT 0 
                    AFTER tier
                """
                    )
                )
                print("  ✓ Added 'total_points' column")
            else:
                print("\n[!] 'total_points' column already exists")

            # Add birthday column if it doesn't exist
            if "birthday" not in columns:
                print("\n[+] Adding 'birthday' column...")
                db.session.execute(
                    text(
                        """
                    ALTER TABLE users 
                    ADD COLUMN birthday DATE NULL 
                    AFTER total_points
                """
                    )
                )
                print("  ✓ Added 'birthday' column")
            else:
                print("\n[!] 'birthday' column already exists")

            # Commit changes
            db.session.commit()

            # Verify columns were added
            print("\n[+] Verifying migration...")
            from sqlalchemy import inspect as sqlalchemy_inspect

            inspector = sqlalchemy_inspect(db.engine)
            new_columns = [col["name"] for col in inspector.get_columns("users")]

            required_columns = ["tier", "total_points", "birthday"]
            all_present = all(col in new_columns for col in required_columns)

            if all_present:
                print("\n[SUCCESS] All gamification columns added successfully!")
                print("\n[+] Updated columns in users table:")
                for col in new_columns:
                    marker = (
                        "  [NEW]"
                        if col in required_columns and col not in columns
                        else "  [OK]"
                    )
                    print(f"{marker} {col}")
            else:
                missing = [col for col in required_columns if col not in new_columns]
                print(f"\n[ERROR] Missing columns: {missing}")
                return False

            # Update existing users to have default tier and points
            print("\n[+] Updating existing users with default values...")
            db.session.execute(
                text(
                    """
                UPDATE users 
                SET tier = 'Bronze', total_points = 0 
                WHERE tier IS NULL OR total_points IS NULL
            """
                )
            )
            db.session.commit()
            print("  ✓ Updated existing users")

            print("\n" + "=" * 80)
            print("MIGRATION COMPLETE")
            print("=" * 80)
            return True

        except Exception as e:
            db.session.rollback()
            print(f"\n[ERROR] Migration failed: {str(e)}")
            print("\nYou may need to run this manually in your database:")
            print(
                """
ALTER TABLE users ADD COLUMN tier VARCHAR(20) DEFAULT 'Bronze' AFTER pref_low_calorie;
ALTER TABLE users ADD COLUMN total_points INT DEFAULT 0 AFTER tier;
ALTER TABLE users ADD COLUMN birthday DATE NULL AFTER total_points;
UPDATE users SET tier = 'Bronze', total_points = 0 WHERE tier IS NULL OR total_points IS NULL;
            """
            )
            return False


if __name__ == "__main__":
    success = migrate_users_table()
    if success:
        print("\n✓ Users table migration completed successfully!")
        print("\nNext steps:")
        print(
            "  1. Run: python proj2/stackshack/create_tables.py (to create gamification tables)"
        )
        print(
            "  2. Run: python proj2/stackshack/scripts/init_gamification.py (to initialize badges)"
        )
    else:
        print("\n✗ Migration failed. Please check the error messages above.")
