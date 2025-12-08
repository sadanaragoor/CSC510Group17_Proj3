"""Comprehensive tests for payment gateway service."""

import pytest
from unittest.mock import patch
from services.payment_gateway import PaymentGatewayService
from models.payment import CampusCard
from database.db import db
from datetime import datetime
from decimal import Decimal


class TestPaymentGatewayService:
    """Test payment gateway service."""

    @pytest.fixture
    def gateway(self):
        """Create payment gateway instance."""
        return PaymentGatewayService(simulation_mode="always_success")

    @pytest.fixture
    def basic_payment_request(self):
        """Create basic payment request."""
        return {
            "order_id": 1,
            "user_id": 1,
            "amount": 10.50,
            "payment_method": "card",
        }

    @pytest.fixture
    def card_payment_request(self, basic_payment_request):
        """Create card payment request."""
        return {
            **basic_payment_request,
            "card_number": "4111111111111111",
            "cvv": "123",
            "expiry_month": 12,
            "expiry_year": 2030,
        }

    @pytest.fixture
    def campus_card(self, app, test_user):
        """Create a campus card for testing."""
        with app.app_context():
            card = CampusCard(
                user_id=test_user.id,
                card_number="1234567890123456",
                balance=Decimal("100.00"),
                is_active=True,
            )
            db.session.add(card)
            db.session.commit()
            yield card
            db.session.delete(card)
            db.session.commit()

    def test_gateway_initialization(self):
        """Test gateway initialization."""
        gateway = PaymentGatewayService(simulation_mode="random_90")
        assert gateway.simulation_mode == "random_90"

    def test_validate_request_success(self, gateway, basic_payment_request):
        """Test request validation success."""
        result = gateway._validate_request(basic_payment_request)
        assert result["valid"] is True

    def test_validate_request_missing_field(self, gateway):
        """Test request validation with missing field."""
        request = {"order_id": 1, "user_id": 1}
        result = gateway._validate_request(request)
        assert result["valid"] is False
        assert "Missing required field" in result["reason"]

    def test_validate_request_invalid_amount_zero(self, gateway):
        """Test request validation with zero amount."""
        request = {
            "order_id": 1,
            "user_id": 1,
            "amount": 0,
            "payment_method": "card",
        }
        result = gateway._validate_request(request)
        assert result["valid"] is False
        assert "greater than 0" in result["reason"]

    def test_validate_request_invalid_amount_negative(self, gateway):
        """Test request validation with negative amount."""
        request = {
            "order_id": 1,
            "user_id": 1,
            "amount": -10,
            "payment_method": "card",
        }
        result = gateway._validate_request(request)
        assert result["valid"] is False

    def test_validate_request_invalid_amount_format(self, gateway):
        """Test request validation with invalid amount format."""
        request = {
            "order_id": 1,
            "user_id": 1,
            "amount": "invalid",
            "payment_method": "card",
        }
        result = gateway._validate_request(request)
        assert result["valid"] is False
        assert "Invalid amount format" in result["reason"]

    def test_validate_card_number_valid(self, gateway):
        """Test valid card number validation."""
        assert gateway._validate_card_number("4111111111111111") is True
        assert gateway._validate_card_number("5555555555554444") is True

    def test_validate_card_number_with_spaces(self, gateway):
        """Test card number validation with spaces."""
        assert gateway._validate_card_number("4111 1111 1111 1111") is True

    def test_validate_card_number_with_dashes(self, gateway):
        """Test card number validation with dashes."""
        assert gateway._validate_card_number("4111-1111-1111-1111") is True

    def test_validate_card_number_invalid_length(self, gateway):
        """Test invalid card number length."""
        assert gateway._validate_card_number("411111111111111") is False
        assert gateway._validate_card_number("41111111111111111") is False

    def test_validate_card_number_invalid_format(self, gateway):
        """Test invalid card number format."""
        assert gateway._validate_card_number("411111111111abcd") is False

    def test_validate_expiry_valid_future(self, gateway):
        """Test valid future expiry date."""
        assert gateway._validate_expiry(12, 2030) is True

    def test_validate_expiry_current_month(self, gateway):
        """Test expiry date in current month."""
        now = datetime.now()
        assert gateway._validate_expiry(now.month, now.year) is True

    def test_validate_expiry_expired(self, gateway):
        """Test expired card."""
        assert gateway._validate_expiry(1, 2020) is False

    def test_validate_expiry_invalid_month(self, gateway):
        """Test invalid month."""
        assert gateway._validate_expiry(13, 2030) is False
        assert gateway._validate_expiry(0, 2030) is False

    def test_validate_expiry_two_digit_year(self, gateway):
        """Test two-digit year conversion."""
        assert gateway._validate_expiry(12, 30) is True

    def test_validate_expiry_invalid_format(self, gateway):
        """Test invalid expiry format."""
        assert gateway._validate_expiry("invalid", 2030) is False
        assert gateway._validate_expiry(12, "invalid") is False

    def test_validate_cvv_valid(self, gateway):
        """Test valid CVV."""
        assert gateway._validate_cvv("123") is True
        assert gateway._validate_cvv("1234") is True

    def test_validate_cvv_invalid(self, gateway):
        """Test invalid CVV."""
        assert gateway._validate_cvv("12") is False
        assert gateway._validate_cvv("12345") is False
        assert gateway._validate_cvv("abc") is False

    def test_get_card_type_visa(self, gateway):
        """Test card type detection for Visa."""
        assert gateway._get_card_type("4111111111111111") == "visa"

    def test_get_card_type_mastercard(self, gateway):
        """Test card type detection for Mastercard."""
        assert gateway._get_card_type("5555555555554444") == "mastercard"

    def test_get_card_type_amex(self, gateway):
        """Test card type detection for Amex."""
        assert gateway._get_card_type("3782822463100005") == "amex"

    def test_get_card_type_discover(self, gateway):
        """Test card type detection for Discover."""
        assert gateway._get_card_type("6011111111111117") == "discover"

    def test_get_card_type_unknown(self, gateway):
        """Test card type detection for unknown."""
        assert gateway._get_card_type("9111111111111111") == "unknown"

    def test_mask_card_number(self, gateway):
        """Test card number masking."""
        assert gateway._mask_card_number("4111111111111111") == "****1111"

    def test_mask_card_number_with_spaces(self, gateway):
        """Test card number masking with spaces."""
        assert gateway._mask_card_number("4111 1111 1111 1111") == "****1111"

    @patch("time.sleep")
    def test_process_card_payment_success(
        self, mock_sleep, gateway, card_payment_request
    ):
        """Test successful card payment."""
        result = gateway.process_payment(card_payment_request)
        assert result["success"] is True
        assert result["payment_method"] == "card"
        assert result["card_type"] == "visa"
        assert result["masked_card"] == "****1111"
        assert "transaction_id" in result

    @patch("time.sleep")
    def test_process_card_payment_invalid_card(self, mock_sleep, gateway):
        """Test card payment with invalid card number."""
        request = {
            "order_id": 1,
            "user_id": 1,
            "amount": 10.50,
            "payment_method": "card",
            "card_number": "4111",
            "cvv": "123",
            "expiry_month": 12,
            "expiry_year": 2030,
        }
        result = gateway.process_payment(request)
        assert result["success"] is False
        assert "Invalid card number" in result["failure_reason"]

    @patch("time.sleep")
    def test_process_card_payment_expired(self, mock_sleep, gateway):
        """Test card payment with expired card."""
        request = {
            "order_id": 1,
            "user_id": 1,
            "amount": 10.50,
            "payment_method": "card",
            "card_number": "4111111111111111",
            "cvv": "123",
            "expiry_month": 1,
            "expiry_year": 2020,
        }
        result = gateway.process_payment(request)
        assert result["success"] is False
        assert "expired" in result["failure_reason"].lower()

    @patch("time.sleep")
    def test_process_card_payment_invalid_cvv(self, mock_sleep, gateway):
        """Test card payment with invalid CVV."""
        request = {
            "order_id": 1,
            "user_id": 1,
            "amount": 10.50,
            "payment_method": "card",
            "card_number": "4111111111111111",
            "cvv": "12",
            "expiry_month": 12,
            "expiry_year": 2030,
        }
        result = gateway.process_payment(request)
        assert result["success"] is False
        assert "Invalid CVV" in result["failure_reason"]

    @patch("time.sleep")
    def test_process_campus_card_payment_success(
        self, mock_sleep, gateway, app, campus_card
    ):
        """Test successful campus card payment."""
        with app.app_context():
            request = {
                "order_id": 1,
                "user_id": campus_card.user_id,
                "amount": 10.50,
                "payment_method": "campus_card",
                "campus_card_id": campus_card.id,
            }
            result = gateway.process_payment(request)
            assert result["success"] is True
            assert result["payment_method"] == "campus_card"
            assert "****" in result["masked_card"]

    @patch("time.sleep")
    def test_process_campus_card_payment_insufficient_balance(
        self, mock_sleep, gateway, app, campus_card
    ):
        """Test campus card payment with insufficient balance."""
        with app.app_context():
            request = {
                "order_id": 1,
                "user_id": campus_card.user_id,
                "amount": 200.00,
                "payment_method": "campus_card",
                "campus_card_id": campus_card.id,
            }
            result = gateway.process_payment(request)
            assert result["success"] is False
            assert "Insufficient balance" in result["failure_reason"]

    @patch("time.sleep")
    def test_process_campus_card_payment_not_found(self, mock_sleep, gateway, app):
        """Test campus card payment with non-existent card."""
        with app.app_context():
            request = {
                "order_id": 1,
                "user_id": 1,
                "amount": 10.50,
                "payment_method": "campus_card",
                "campus_card_id": 99999,
            }
            result = gateway.process_payment(request)
            assert result["success"] is False
            assert "not found" in result["failure_reason"]

    @patch("time.sleep")
    def test_process_campus_card_payment_missing_id(self, mock_sleep, gateway):
        """Test campus card payment without card ID."""
        request = {
            "order_id": 1,
            "user_id": 1,
            "amount": 10.50,
            "payment_method": "campus_card",
        }
        result = gateway.process_payment(request)
        assert result["success"] is False
        assert "Campus card ID required" in result["failure_reason"]

    @patch("time.sleep")
    def test_process_campus_card_payment_inactive(
        self, mock_sleep, gateway, app, campus_card
    ):
        """Test campus card payment with inactive card."""
        with app.app_context():
            campus_card.is_active = False
            db.session.commit()
            request = {
                "order_id": 1,
                "user_id": campus_card.user_id,
                "amount": 10.50,
                "payment_method": "campus_card",
                "campus_card_id": campus_card.id,
            }
            result = gateway.process_payment(request)
            assert result["success"] is False
            assert "disabled" in result["failure_reason"]

    @patch("time.sleep")
    def test_process_wallet_payment_success(self, mock_sleep, gateway):
        """Test successful wallet payment."""
        request = {
            "order_id": 1,
            "user_id": 1,
            "amount": 10.50,
            "payment_method": "wallet",
            "wallet_provider": "gpay",
        }
        result = gateway.process_payment(request)
        assert result["success"] is True
        assert result["payment_method"] == "wallet"
        assert result["payment_provider"] == "gpay"

    @patch("time.sleep")
    def test_process_wallet_payment_all_providers(self, mock_sleep, gateway):
        """Test all wallet providers."""
        for provider in ["gpay", "apple_pay", "paypal", "samsung_pay"]:
            request = {
                "order_id": 1,
                "user_id": 1,
                "amount": 10.50,
                "payment_method": "wallet",
                "wallet_provider": provider,
            }
            result = gateway.process_payment(request)
            assert result["success"] is True
            assert result["payment_provider"] == provider

    @patch("time.sleep")
    def test_process_wallet_payment_invalid_provider(self, mock_sleep, gateway):
        """Test wallet payment with invalid provider."""
        request = {
            "order_id": 1,
            "user_id": 1,
            "amount": 10.50,
            "payment_method": "wallet",
            "wallet_provider": "invalid_wallet",
        }
        result = gateway.process_payment(request)
        assert result["success"] is False
        assert "Unsupported wallet provider" in result["failure_reason"]

    @patch("time.sleep")
    def test_process_payment_invalid_method(self, mock_sleep, gateway):
        """Test payment with invalid payment method."""
        request = {
            "order_id": 1,
            "user_id": 1,
            "amount": 10.50,
            "payment_method": "invalid_method",
        }
        result = gateway.process_payment(request)
        assert result["success"] is False
        assert "Invalid payment method" in result["failure_reason"]

    @patch("time.sleep")
    def test_process_payment_missing_required_fields(self, mock_sleep, gateway):
        """Test payment with missing required fields."""
        request = {"order_id": 1}
        result = gateway.process_payment(request)
        assert result["success"] is False
        assert "Missing required field" in result["failure_reason"]

    def test_should_succeed_always_success_mode(self):
        """Test success determination in always_success mode."""
        gateway = PaymentGatewayService(simulation_mode="always_success")
        assert gateway._should_succeed() is True

    def test_should_succeed_random_90_mode(self):
        """Test success determination in random_90 mode."""
        gateway = PaymentGatewayService(simulation_mode="random_90")
        # Test multiple times to check probability
        results = [gateway._should_succeed() for _ in range(100)]
        success_rate = sum(results) / len(results)
        assert 0.7 < success_rate < 1.0

    @patch("time.sleep")
    def test_random_failure_mode(self, mock_sleep):
        """Test random failure in random_90 mode."""
        gateway = PaymentGatewayService(simulation_mode="random_90")
        request = {
            "order_id": 1,
            "user_id": 1,
            "amount": 10.50,
            "payment_method": "card",
            "card_number": "4111111111111111",
            "cvv": "123",
            "expiry_month": 12,
            "expiry_year": 2030,
        }
        # Run multiple times to potentially hit a failure
        results = [gateway.process_payment(request) for _ in range(20)]
        # At least some should succeed in random mode
        assert any(r["success"] for r in results)

    def test_create_success_response_structure(self, gateway):
        """Test success response structure."""
        request = {"order_id": 1, "user_id": 1, "amount": 10.50}
        response = gateway._create_success_response(
            request,
            payment_method="card",
            card_type="visa",
            masked_card="****1111",
        )
        assert response["success"] is True
        assert response["status"] == "success"
        assert "transaction_id" in response
        assert response["order_id"] == 1
        assert response["user_id"] == 1
        assert response["amount"] == 10.50
        assert response["payment_method"] == "card"
        assert response["card_type"] == "visa"
        assert response["masked_card"] == "****1111"

    def test_create_failure_response_structure(self, gateway):
        """Test failure response structure."""
        request = {"order_id": 1, "user_id": 1, "amount": 10.50}
        response = gateway._create_failure_response(request, "Test failure reason")
        assert response["success"] is False
        assert response["status"] == "failed"
        assert "transaction_id" in response
        assert response["failure_reason"] == "Test failure reason"
        assert "Test failure reason" in response["message"]
