"""
Dummy Payment Gateway Service
Simulates payment processing without connecting to real payment providers
"""
import time
import random
import re
from datetime import datetime
from database.db import db
from models.payment import Transaction, CampusCard


class PaymentGatewayService:
    """
    Core payment gateway simulation service
    """
    
    # Supported wallet providers
    WALLET_PROVIDERS = ["gpay", "apple_pay", "paypal", "samsung_pay"]
    
    # Card types based on first digit
    CARD_TYPES = {
        "4": "visa",
        "5": "mastercard",
        "3": "amex",
        "6": "discover"
    }
    
    def __init__(self, simulation_mode="random_90"):
        """
        Initialize the payment gateway
        
        Args:
            simulation_mode: 'always_success', 'random_90', or 'rule_based'
        """
        self.simulation_mode = simulation_mode
    
    def process_payment(self, payment_request):
        """
        Main payment processing method
        
        Args:
            payment_request (dict): Contains payment details
                - order_id: Order ID
                - user_id: User ID
                - amount: Payment amount
                - payment_method: 'card', 'campus_card', or 'wallet'
                - card_number: (if card) 16 digit number
                - cvv: (if card) 3-4 digits
                - expiry_month: (if card)
                - expiry_year: (if card)
                - campus_card_id: (if campus_card)
                - wallet_provider: (if wallet) 'gpay', 'apple_pay', etc.
        
        Returns:
            dict: Payment response with transaction details
        """
        # Simulate processing delay (1-3 seconds)
        time.sleep(random.uniform(1, 3))
        
        # Validate basic request
        validation_result = self._validate_request(payment_request)
        if not validation_result["valid"]:
            return self._create_failure_response(payment_request, validation_result["reason"])
        
        # Process based on payment method
        payment_method = payment_request["payment_method"]
        
        if payment_method == "card":
            return self._process_card_payment(payment_request)
        elif payment_method == "campus_card":
            return self._process_campus_card_payment(payment_request)
        elif payment_method == "wallet":
            return self._process_wallet_payment(payment_request)
        else:
            return self._create_failure_response(payment_request, "Invalid payment method")
    
    def _validate_request(self, request):
        """Validate basic payment request format"""
        required_fields = ["order_id", "user_id", "amount", "payment_method"]
        
        for field in required_fields:
            if field not in request or request[field] is None:
                return {"valid": False, "reason": f"Missing required field: {field}"}
        
        # Validate amount
        try:
            amount = float(request["amount"])
            if amount <= 0:
                return {"valid": False, "reason": "Amount must be greater than 0"}
        except (ValueError, TypeError):
            return {"valid": False, "reason": "Invalid amount format"}
        
        return {"valid": True}
    
    def _process_card_payment(self, request):
        """Process debit/credit card payment"""
        card_number = request.get("card_number", "")
        expiry_month = request.get("expiry_month")
        expiry_year = request.get("expiry_year")
        cvv = request.get("cvv", "")
        
        # Validate card number format
        if not self._validate_card_number(card_number):
            return self._create_failure_response(request, "Invalid card number format")
        
        # Validate expiry
        if not self._validate_expiry(expiry_month, expiry_year):
            return self._create_failure_response(request, "Card expired or invalid expiry date")
        
        # Validate CVV
        if not self._validate_cvv(cvv):
            return self._create_failure_response(request, "Invalid CVV")
        
        # Determine card type
        card_type = self._get_card_type(card_number)
        masked_card = self._mask_card_number(card_number)
        
        # Simulate payment outcome based on mode
        if self._should_succeed():
            return self._create_success_response(
                request,
                payment_method="card",
                card_type=card_type,
                masked_card=masked_card
            )
        else:
            reasons = [
                "Insufficient funds",
                "Card declined by issuer",
                "Transaction limit exceeded",
                "Security check failed"
            ]
            return self._create_failure_response(request, random.choice(reasons))
    
    def _process_campus_card_payment(self, request):
        """Process campus card payment"""
        from decimal import Decimal
        
        campus_card_id = request.get("campus_card_id")
        amount = Decimal(str(request["amount"]))  # Convert to Decimal to match database type
        
        if not campus_card_id:
            return self._create_failure_response(request, "Campus card ID required")
        
        # Check if campus card exists and is active
        campus_card = CampusCard.query.filter_by(
            id=campus_card_id,
            user_id=request["user_id"]
        ).first()
        
        if not campus_card:
            return self._create_failure_response(request, "Campus card not found")
        
        if not campus_card.is_active:
            return self._create_failure_response(request, "Campus card is disabled")
        
        # Check balance (rule-based)
        if campus_card.balance < amount:
            return self._create_failure_response(
                request,
                f"Insufficient balance. Available: ${campus_card.balance}"
            )
        
        # Deduct from campus card balance
        campus_card.balance -= amount
        db.session.commit()
        
        return self._create_success_response(
            request,
            payment_method="campus_card",
            masked_card=f"****{campus_card.card_number[-4:]}"
        )
    
    def _process_wallet_payment(self, request):
        """Process digital wallet payment"""
        wallet_provider = request.get("wallet_provider", "").lower()
        
        if wallet_provider not in self.WALLET_PROVIDERS:
            return self._create_failure_response(
                request,
                f"Unsupported wallet provider. Supported: {', '.join(self.WALLET_PROVIDERS)}"
            )
        
        # Simulate wallet redirect/approval (already happened in UI)
        if self._should_succeed():
            return self._create_success_response(
                request,
                payment_method="wallet",
                payment_provider=wallet_provider
            )
        else:
            reasons = [
                "Wallet authentication failed",
                "Wallet payment declined",
                "Insufficient wallet balance",
                "Wallet account suspended"
            ]
            return self._create_failure_response(request, random.choice(reasons))
    
    def _validate_card_number(self, card_number):
        """Validate card number format (16 digits)"""
        card_number = str(card_number).replace(" ", "").replace("-", "")
        return bool(re.match(r"^\d{16}$", card_number))
    
    def _validate_expiry(self, month, year):
        """Validate card expiry date"""
        try:
            month = int(month)
            year = int(year)
            
            if month < 1 or month > 12:
                return False
            
            # Convert 2-digit year to 4-digit
            if year < 100:
                year += 2000
            
            # Card is valid through the END of the expiry month
            # So check if we're still in or before the expiry month
            current_date = datetime.now()
            current_year = current_date.year
            current_month = current_date.month
            
            # Card is valid if expiry year is after current year
            # OR if expiry year matches and expiry month is >= current month
            if year > current_year:
                return True
            elif year == current_year and month >= current_month:
                return True
            else:
                return False
        except (ValueError, TypeError):
            return False
    
    def _validate_cvv(self, cvv):
        """Validate CVV format (3-4 digits)"""
        return bool(re.match(r"^\d{3,4}$", str(cvv)))
    
    def _get_card_type(self, card_number):
        """Determine card type from card number"""
        first_digit = str(card_number)[0]
        return self.CARD_TYPES.get(first_digit, "unknown")
    
    def _mask_card_number(self, card_number):
        """Mask card number (show only last 4 digits)"""
        card_number = str(card_number).replace(" ", "").replace("-", "")
        return f"****{card_number[-4:]}"
    
    def _should_succeed(self):
        """Determine if payment should succeed based on simulation mode"""
        if self.simulation_mode == "always_success":
            return True
        elif self.simulation_mode == "random_90":
            return random.random() < 0.9  # 90% success rate
        else:  # rule_based handled in individual methods
            return True
    
    def _create_success_response(self, request, payment_method, 
                                 card_type=None, masked_card=None, payment_provider=None):
        """Create a successful payment response"""
        return {
            "success": True,
            "transaction_id": Transaction.generate_transaction_id(),
            "status": "success",
            "order_id": request["order_id"],
            "user_id": request["user_id"],
            "amount": float(request["amount"]),
            "payment_method": payment_method,
            "payment_provider": payment_provider,
            "card_type": card_type,
            "masked_card": masked_card,
            "timestamp": datetime.utcnow().isoformat(),
            "message": "Payment processed successfully"
        }
    
    def _create_failure_response(self, request, reason):
        """Create a failed payment response"""
        return {
            "success": False,
            "transaction_id": Transaction.generate_transaction_id(),
            "status": "failed",
            "order_id": request.get("order_id"),
            "user_id": request.get("user_id"),
            "amount": float(request.get("amount", 0)),
            "payment_method": request.get("payment_method"),
            "failure_reason": reason,
            "timestamp": datetime.utcnow().isoformat(),
            "message": f"Payment failed: {reason}"
        }

