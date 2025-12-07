"""
Migration Script: Add email column to users table
Run this once to update your existing database
"""

from app import create_app
from database.db import db


def add_email_column():
    """Add email column to existing users table"""
    app = create_app("development")

    with app.app_context():
        try:
            # Get the database connection
            connection = db.engine.raw_connection()
            cursor = connection.cursor()

            # Check if column already exists
            cursor.execute(
                """
                SELECT COUNT(*)
                FROM information_schema.columns
                WHERE table_schema = DATABASE()
                AND table_name = 'users'
                AND column_name = 'email'
            """
            )

            column_exists = cursor.fetchone()[0] > 0

            if column_exists:
                print("✅ Email column already exists in users table!")
            else:
                print("Adding email column to users table...")

                # Add the email column
                cursor.execute(
                    """
                    ALTER TABLE users
                    ADD COLUMN email VARCHAR(255) NULL
                """
                )

                connection.commit()
                print("✅ Email column added successfully!")

            cursor.close()
            connection.close()

            print("\n" + "=" * 60)
            print("Database migration completed!")
            print("=" * 60)
            print("\nYou can now:")
            print("1. Restart your Flask app")
            print("2. Add .edu emails to users:")
            print("   python update_user_email.py username user@university.edu")
            print("3. Test campus card creation")

        except Exception as e:
            print(f"❌ Error: {e}")
            print("\nIf you see 'Duplicate column' error, the column already exists.")
            print("You can safely ignore this and restart your app.")


if __name__ == "__main__":
    add_email_column()
