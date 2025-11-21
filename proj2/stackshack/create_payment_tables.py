"""
Database Migration Script for Payment Gateway
Creates all payment-related tables in the database
"""
from app import create_app
from database.db import db
from models.payment import Transaction, CampusCard, Receipt, PaymentMethod


def create_payment_tables():
    """Create all payment tables"""
    app = create_app("development")
    
    with app.app_context():
        print("Creating payment gateway tables...")
        print("-" * 50)
        
        # Create all tables
        db.create_all()
        
        # List the payment tables
        payment_tables = [
            "transactions",
            "campus_cards",
            "receipts",
            "payment_methods"
        ]
        
        print("\n✅ Payment tables created successfully:")
        for table in payment_tables:
            print(f"   - {table}")
        
        print("\n" + "-" * 50)
        print("Payment gateway database setup complete!")
        print("\nNext steps:")
        print("1. Run your Flask app: python app.py")
        print("2. Place an order as a customer")
        print("3. Click 'Pay Now' in order history")
        print("4. Test different payment methods")
        print("\nEnjoy your new payment gateway! 🎉")


if __name__ == "__main__":
    create_payment_tables()

