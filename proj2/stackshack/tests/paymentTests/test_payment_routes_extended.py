"""
Extended payment route tests to increase coverage.
"""

from decimal import Decimal
from unittest.mock import patch, MagicMock
from models.order import Order
from models.payment import Transaction, CampusCard
from database.db import db


class TestPaymentRoutesExtended:
    """Extended payment route tests."""

    def login(self, client, username="testuser", password="testpassword123"):
        """Helper method to login."""
        return client.post(
            "/auth/login",
            data={"username": username, "password": password},
            follow_redirects=True,
        )

    def test_process_payment_card(self, client, app, test_user, sample_order):
        """Test processing card payment."""
        with app.app_context():
            order = db.session.get(Order, sample_order)
            order.total_price = Decimal("15.00")
            order.original_total = Decimal("15.00")
            db.session.commit()

        self.login(client)

        with patch(
            "controllers.payment_controller.PaymentGatewayService"
        ) as mock_gateway:
            mock_gateway_instance = MagicMock()
            mock_gateway.return_value = mock_gateway_instance
            mock_gateway_instance.process_payment.return_value = {
                "success": True,
                "transaction_id": "TXN-123",
                "payment_method": "card",
                "status": "success",
            }

            response = client.post(
                "/payment/process",
                data={
                    "order_id": sample_order,
                    "payment_method": "card",
                    "amount": "15.00",
                    "card_number": "4111111111111111",
                    "cvv": "123",
                    "expiry_month": "12",
                    "expiry_year": "2025",
                },
                follow_redirects=True,
            )

            assert response.status_code == 200

    def test_process_payment_campus_card(self, client, app, campus_user, sample_order):
        """Test processing campus card payment."""
        with app.app_context():
            order = db.session.get(Order, sample_order)
            order.user_id = campus_user
            order.total_price = Decimal("15.00")
            db.session.commit()

            campus_card = CampusCard(
                user_id=campus_user, card_number="1234567890", balance=Decimal("100.00")
            )
            db.session.add(campus_card)
            db.session.commit()

        self.login(client, username="student", password="testpassword123")

        with patch(
            "controllers.payment_controller.PaymentGatewayService"
        ) as mock_gateway:
            mock_gateway_instance = MagicMock()
            mock_gateway.return_value = mock_gateway_instance
            mock_gateway_instance.process_payment.return_value = {
                "success": True,
                "transaction_id": "TXN-123",
                "payment_method": "campus_card",
                "status": "success",
            }

            response = client.post(
                "/payment/process",
                data={
                    "order_id": sample_order,
                    "payment_method": "campus_card",
                    "amount": "15.00",
                    "campus_card_id": "1",
                },
                follow_redirects=True,
            )

            assert response.status_code == 200

    def test_process_payment_wallet(self, client, app, test_user, sample_order):
        """Test processing wallet payment."""
        with app.app_context():
            order = db.session.get(Order, sample_order)
            order.total_price = Decimal("15.00")
            db.session.commit()

        self.login(client)

        with patch(
            "controllers.payment_controller.PaymentGatewayService"
        ) as mock_gateway:
            mock_gateway_instance = MagicMock()
            mock_gateway.return_value = mock_gateway_instance
            mock_gateway_instance.process_payment.return_value = {
                "success": True,
                "transaction_id": "TXN-123",
                "payment_method": "wallet",
                "status": "success",
            }

            response = client.post(
                "/payment/process",
                data={
                    "order_id": sample_order,
                    "payment_method": "wallet",
                    "amount": "15.00",
                    "wallet_provider": "paypal",
                },
                follow_redirects=True,
            )

            assert response.status_code == 200

    def test_process_payment_missing_data(self, client, app, test_user):
        """Test processing payment with missing data."""
        self.login(client)
        response = client.post("/payment/process", data={}, follow_redirects=True)

        assert response.status_code == 200

    def test_payment_history(self, client, app, test_user):
        """Test viewing payment history."""
        self.login(client)
        response = client.get("/payment/history")

        assert response.status_code == 200
