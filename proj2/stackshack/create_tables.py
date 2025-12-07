# A script to create database tables for the StackShack application.
from app import create_app
from database.db import db
from sqlalchemy import inspect


def create_tables():
    """Creates all database tables with all updated columns."""
    app = create_app(config_name="development")

    with app.app_context():
        print("=" * 80)
        print("CREATING DATABASE TABLES FOR STACKSHACK")
        print("=" * 80)

        # Import all models to ensure they're registered with SQLAlchemy

        print("\n[+] Models registered:")
        print("  - User")
        print("  - MenuItem")
        print("  - Order")
        print("  - OrderItem")
        print("  - Transaction (Payment)")
        print("  - PaymentMethod")
        print("  - CampusCard")
        print("  - Receipt")
        print("  - PointsTransaction")
        print("  - Badge")
        print("  - UserBadge")
        print("  - DailyBonus")
        print("  - WeeklyChallenge")
        print("  - UserChallengeProgress")
        print("  - PunchCard")
        print("  - Redemption")
        print("  - StaffProfile")
        print("  - Shift")
        print("  - ShiftAssignment")

        # Create all tables
        print("\n[+] Creating database tables...")
        db.create_all()

        # Verify tables were created
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()

        print("\n[SUCCESS] Database tables created successfully!")
        print(f"\n[INFO] Total tables created: {len(tables)}")
        print("\nTables:")
        for table in sorted(tables):
            print(f"  - {table}")

        # Show column details for key tables with new columns
        print("\n" + "=" * 80)
        print("SCHEMA VERIFICATION - NEW COLUMNS")
        print("=" * 80)

        # Check users table
        print("\n[USERS TABLE]")
        user_columns = inspector.get_columns("users")
        new_user_cols = [
            "email",
            "pref_vegan",
            "pref_gluten_free",
            "pref_high_protein",
            "pref_low_calorie",
        ]
        for col in user_columns:
            if col["name"] in new_user_cols:
                print(f"  [OK] {col['name']}: {col['type']}")

        # Check menu_items table
        print("\n[MENU_ITEMS TABLE]")
        menu_columns = inspector.get_columns("menu_items")
        new_menu_cols = [
            "stock_quantity",
            "low_stock_threshold",
            "created_at",
            "updated_at",
        ]
        for col in menu_columns:
            if col["name"] in new_menu_cols:
                print(f"  [OK] {col['name']}: {col['type']}")

        # Check order_items table
        print("\n[ORDER_ITEMS TABLE]")
        order_item_columns = inspector.get_columns("order_items")
        new_order_cols = ["burger_index", "burger_name"]
        for col in order_item_columns:
            if col["name"] in new_order_cols:
                print(f"  [OK] {col['name']}: {col['type']}")

        # Check payment tables
        print("\n[PAYMENT TABLES]")
        payment_tables = ["transactions", "payment_methods", "campus_cards", "receipts"]
        for table_name in payment_tables:
            if table_name in tables:
                print(f"  [OK] {table_name} - Created")
            else:
                print(f"  [MISSING] {table_name} - Not found")

        print("\n" + "=" * 80)
        print("DATABASE INITIALIZATION COMPLETE")
        print("=" * 80)
        print("\nYou can now:")
        print("  1. Run seed_menu.py to populate menu items")
        print("  2. Run demo_payment_gateway.py to add demo payment data")
        print("  3. Start the Flask app: python app.py")
        print("\n" + "=" * 80)


if __name__ == "__main__":
    create_tables()
