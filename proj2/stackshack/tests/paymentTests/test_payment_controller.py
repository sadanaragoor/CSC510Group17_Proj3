"""
Test cases for payment controller.
"""
from decimal import Decimal
from datetime import datetime
from unittest.mock import patch, MagicMock
from models.payment import Transaction
from models.order import Order
from controllers.payment_controller import PaymentController
from database.db import db


class TestPaymentController:
    """Test cases for PaymentController."""
    
    @patch('controllers.payment_controller.PaymentGatewayService')
    
    def test_process_payment_order_not_found(self, app, test_user):
        """Test payment processing with non-existent order."""
        with app.app_context():
            payment_data = {
                "order_id": 99999,
                "user_id": test_user,
                "amount": 15.00
            }
            
            success, message, transaction_data = PaymentController.process_payment(payment_data)
            
            assert success is False
            assert "not found" in message.lower()
    
    def test_process_payment_unauthorized(self, app, test_user, sample_order):
        """Test payment processing with wrong user."""
        with app.app_context():
            payment_data = {
                "order_id": sample_order,
                "user_id": 99999,  # Wrong user
                "amount": 15.00
            }
            
            success, message, transaction_data = PaymentController.process_payment(payment_data)
            
            assert success is False
            assert "unauthorized" in message.lower()
    
    @patch('controllers.payment_controller.PaymentGatewayService')
    def test_process_payment_already_paid(self, mock_gateway, app, test_user, sample_order):
        """Test payment processing for already paid order."""
        with app.app_context():
            # Create existing successful transaction
            transaction = Transaction(
                transaction_id="TXN-EXISTING",
                order_id=sample_order,
                user_id=test_user,
                amount=Decimal("15.00"),
                payment_method="card",
                status="success"
            )
            db.session.add(transaction)
            db.session.commit()
            
            payment_data = {
                "order_id": sample_order,
                "user_id": test_user,
                "amount": 15.00
            }
            
            success, message, transaction_data = PaymentController.process_payment(payment_data)
            
            assert success is False
            assert "already paid" in message.lower()
    
