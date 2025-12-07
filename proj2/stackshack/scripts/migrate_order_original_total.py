"""
Migration script to add original_total column to orders table.
This column stores the original order total before any coupon discounts.
"""

import sys
import os

# Add the parent directory to the path so we can import from stackshack
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from database.db import db
from sqlalchemy import text


def migrate():
    """Add original_total column to orders table if it doesn't exist."""
    app = create_app()

    with app.app_context():
        try:
            # Check if column already exists
            result = db.session.execute(
                text(
                    """
                SELECT COUNT(*) as count
                FROM information_schema.COLUMNS
                WHERE TABLE_SCHEMA = DATABASE()
                AND TABLE_NAME = 'orders'
                AND COLUMN_NAME = 'original_total'
            """
                )
            )

            column_exists = result.fetchone()[0] > 0

            if column_exists:
                print(
                    "Column 'original_total' already exists in 'orders' table. Skipping migration."
                )
                return

            # Add the column
            print("Adding 'original_total' column to 'orders' table...")
            db.session.execute(
                text(
                    """
                ALTER TABLE orders
                ADD COLUMN original_total DECIMAL(10, 2) NULL
            """
                )
            )

            # For existing orders, set original_total to total_price
            print("Setting original_total = total_price for existing orders...")
            db.session.execute(
                text(
                    """
                UPDATE orders
                SET original_total = total_price
                WHERE original_total IS NULL
            """
                )
            )

            db.session.commit()
            print("✅ Migration completed successfully!")

        except Exception as e:
            db.session.rollback()
            print(f"❌ Error during migration: {str(e)}")
            raise


if __name__ == "__main__":
    migrate()
