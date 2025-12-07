"""
Comprehensive payment controller tests to increase coverage.
"""
from decimal import Decimal
from unittest.mock import patch, MagicMock
from models.payment import Transaction, CampusCard, Receipt
from models.order import Order
from controllers.payment_controller import PaymentController
from database.db import db


class TestPaymentControllerComprehensive:
    """Comprehensive payment controller tests."""
    
    def test_get_campus_card_exists(self, app, campus_user):
        """Test getting existing campus card."""
        with app.app_context():
            campus_card = CampusCard(
                user_id=campus_user,
                card_number="1234567890",
                balance=Decimal("100.00")
            )
            db.session.add(campus_card)
            db.session.commit()
            
            success, message, card = PaymentController.get_campus_card(campus_user)
            
            assert success is True
            assert card is not None
            assert card["card_number"] == "1234567890"
    
    def test_get_campus_card_not_exists(self, app, campus_user):
        """Test getting non-existent campus card."""
        with app.app_context():
            success, message, card = PaymentController.get_campus_card(campus_user)
            
            assert success is False
            assert card is None
    
    def test_get_user_payment_history(self, app, test_user, sample_order):
        """Test getting user payment history."""
        with app.app_context():
            transaction = Transaction(
                transaction_id="TXN-123",
                order_id=sample_order,
                user_id=test_user,
                amount=Decimal("15.00"),
                payment_method="card",
                status="success"
            )
            db.session.add(transaction)
            db.session.commit()
            
            success, message, transactions = PaymentController.get_user_payment_history(test_user)
            
            assert success is True
            assert len(transactions) > 0
    

