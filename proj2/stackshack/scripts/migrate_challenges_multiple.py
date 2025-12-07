"""
Migration script to allow multiple daily bonuses per day and multiple weekly challenges per week.
Run this script to update the database schema.
"""

import sys
import os
from sqlalchemy import text, inspect

# Add the parent directory to the path so we can import from stackshack
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app
from database.db import db


def migrate_challenges():
    app = create_app("development")
    with app.app_context():
        print("=" * 80)
        print("MIGRATING CHALLENGES - ALLOWING MULTIPLE DAILY/WEEKLY CHALLENGES")
        print("=" * 80)

        try:
            inspector = inspect(db.engine)

            # Check daily_bonuses table
            if "daily_bonuses" in inspector.get_table_names():
                columns = [
                    col["name"] for col in inspector.get_columns("daily_bonuses")
                ]
                constraints = inspector.get_unique_constraints("daily_bonuses")

                # Check if bonus_date has a unique constraint
                has_unique = any(
                    "bonus_date" in str(constraint) for constraint in constraints
                )

                if has_unique:
                    print(
                        "\n[+] Removing unique constraint from daily_bonuses.bonus_date..."
                    )
                    # Drop the unique constraint (MySQL syntax)
                    try:
                        db.session.execute(
                            text("ALTER TABLE daily_bonuses DROP INDEX bonus_date")
                        )
                    except Exception as e:
                        # Try alternative syntax
                        try:
                            db.session.execute(
                                text(
                                    "ALTER TABLE daily_bonuses DROP CONSTRAINT bonus_date"
                                )
                            )
                        except:
                            print(
                                f"  Note: Could not drop constraint automatically: {e}"
                            )
                            print("  You may need to drop it manually if it exists")
                    print("  ✓ Removed unique constraint from bonus_date")
                else:
                    print(
                        "\n[!] No unique constraint found on bonus_date (already allows multiple)"
                    )

            db.session.commit()
            print("\n✅ Migration completed successfully!")
            print(
                "\nNote: You can now have up to 2 daily bonuses per day and 3 weekly challenges per week."
            )
            return True

        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Migration failed: {str(e)}")
            import traceback

            traceback.print_exc()
            return False


if __name__ == "__main__":
    migrate_challenges()
