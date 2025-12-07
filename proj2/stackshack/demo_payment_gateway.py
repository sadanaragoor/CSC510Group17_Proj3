"""
Demo Script for Payment Gateway
Helps test and demonstrate the payment gateway functionality
"""

from app import create_app
from database.db import db
from models.user import User
from models.order import Order, OrderItem
from models.payment import CampusCard
from datetime import datetime


def create_demo_data():
    """Create demo data for testing payment gateway"""
    app = create_app("development")

    with app.app_context():
        print("=" * 60)
        print("🎬 Payment Gateway Demo Setup")
        print("=" * 60)

        # Check if demo user exists
        demo_user = User.query.filter_by(username="demo_customer").first()

        if not demo_user:
            print("\n📝 Creating demo customer account...")
            demo_user = User(username="demo_customer", role="customer")
            demo_user.set_password("demo123")
            db.session.add(demo_user)
            db.session.commit()
            print("✅ Demo customer created:")
            print(f"   Username: demo_customer")
            print(f"   Password: demo123")
        else:
            print("\n✅ Demo customer already exists:")
            print(f"   Username: {demo_user.username}")
            print(f"   User ID: {demo_user.id}")

        # Create campus card for demo user
        campus_card = CampusCard.query.filter_by(user_id=demo_user.id).first()

        if not campus_card:
            print("\n🎓 Creating demo campus card...")
            campus_card = CampusCard(
                user_id=demo_user.id,
                card_number="CAMPUS123456",
                balance=150.00,
                is_active=True,
            )
            db.session.add(campus_card)
            db.session.commit()
            print("✅ Campus card created:")
            print(f"   Card Number: {campus_card.card_number}")
            print(f"   Balance: ${campus_card.balance}")
        else:
            print("\n✅ Campus card already exists:")
            print(f"   Card Number: {campus_card.card_number}")
            print(f"   Balance: ${campus_card.balance}")

        # Create a demo order
        print("\n🍔 Creating demo order...")
        demo_order = Order(
            user_id=demo_user.id,
            total_price=25.99,
            status="Pending",
            ordered_at=datetime.utcnow(),
        )
        db.session.add(demo_order)
        db.session.commit()

        # Add order items
        order_items = [
            OrderItem(
                order_id=demo_order.id,
                menu_item_id=1,
                name="Classic Burger",
                price=12.99,
                quantity=1,
            ),
            OrderItem(
                order_id=demo_order.id,
                menu_item_id=2,
                name="French Fries",
                price=4.99,
                quantity=2,
            ),
            OrderItem(
                order_id=demo_order.id,
                menu_item_id=3,
                name="Soft Drink",
                price=3.02,
                quantity=1,
            ),
        ]

        for item in order_items:
            db.session.add(item)

        db.session.commit()

        print("✅ Demo order created:")
        print(f"   Order ID: #{demo_order.id}")
        print(f"   Total: ${demo_order.total_price}")
        print(f"   Status: {demo_order.status}")
        print(f"   Items: {len(order_items)}")

        print("\n" + "=" * 60)
        print("🎉 Demo Setup Complete!")
        print("=" * 60)

        print("\n📋 Quick Start Guide:")
        print("-" * 60)
        print("1. Start your Flask app:")
        print("   python app.py")
        print()
        print("2. Login with demo account:")
        print("   URL: http://localhost:5000/auth/login")
        print("   Username: demo_customer")
        print("   Password: demo123")
        print()
        print("3. Go to Order History:")
        print("   URL: http://localhost:5000/orders/history")
        print()
        print("4. Click 'Pay Now' on the pending order")
        print()
        print("5. Test different payment methods:")
        print("   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("   💳 CREDIT/DEBIT CARD:")
        print("      Card Number: 4111111111111111 (Visa)")
        print("      Expiry: 12/25")
        print("      CVV: 123")
        print()
        print("   🎓 CAMPUS CARD:")
        print("      Card Number: CAMPUS123456")
        print("      Balance: $150.00")
        print()
        print("   📱 DIGITAL WALLETS:")
        print("      - Google Pay")
        print("      - Apple Pay")
        print("      - PayPal")
        print("      - Samsung Pay")
        print("   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print()
        print("6. View receipt after successful payment")
        print()
        print("7. Check payment history:")
        print("   URL: http://localhost:5000/payment/history")
        print()
        print("8. Admin dashboard (if you have admin account):")
        print("   URL: http://localhost:5000/payment/admin/dashboard")
        print()
        print("-" * 60)
        print("💡 Tip: The gateway uses 90% success rate simulation.")
        print("   If a payment fails, just try again!")
        print()
        print("🎬 Happy Testing! 🎉")
        print("=" * 60)


if __name__ == "__main__":
    create_demo_data()
