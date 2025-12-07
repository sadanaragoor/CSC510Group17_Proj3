from database.db import db
from datetime import datetime
import secrets


class Transaction(db.Model):
    """
    Stores all payment transactions (dummy/simulated)
    """
    __tablename__ = "transactions"

    id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.String(50), unique=True, nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    
    # Payment details
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    payment_method = db.Column(db.String(50), nullable=False)  # card, campus_card, wallet
    payment_provider = db.Column(db.String(50), nullable=True)  # gpay, apple_pay, paypal, etc.
    
    # Card details (masked)
    masked_card = db.Column(db.String(20), nullable=True)
    card_type = db.Column(db.String(20), nullable=True)  # visa, mastercard, etc.
    
    # Status
    status = db.Column(db.String(20), nullable=False)  # success, failed, pending
    failure_reason = db.Column(db.String(255), nullable=True)
    
    # Timestamps
    initiated_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    completed_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    order = db.relationship("Order", backref=db.backref("transactions", lazy="dynamic"))
    user = db.relationship("User", backref=db.backref("transactions", lazy="dynamic"))
    receipt = db.relationship("Receipt", uselist=False, back_populates="transaction")

    @staticmethod
    def generate_transaction_id():
        """Generate a unique transaction ID"""
        return f"TXN{secrets.token_hex(8).upper()}"

    def to_dict(self):
        return {
            "id": self.id,
            "transaction_id": self.transaction_id,
            "order_id": self.order_id,
            "user_id": self.user_id,
            "amount": float(self.amount),
            "payment_method": self.payment_method,
            "payment_provider": self.payment_provider,
            "masked_card": self.masked_card,
            "card_type": self.card_type,
            "status": self.status,
            "failure_reason": self.failure_reason,
            "initiated_at": self.initiated_at.isoformat() if self.initiated_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }


class CampusCard(db.Model):
    """
    Dummy campus card table with fake balances
    """
    __tablename__ = "campus_cards"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    card_number = db.Column(db.String(20), unique=True, nullable=False)
    balance = db.Column(db.Numeric(10, 2), nullable=False, default=100.00)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship("User", backref=db.backref("campus_cards", lazy="dynamic"))

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "card_number": self.card_number,
            "balance": float(self.balance),
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Receipt(db.Model):
    """
    Stores receipt information for successful transactions
    """
    __tablename__ = "receipts"

    id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.Integer, db.ForeignKey("transactions.id"), nullable=False, unique=True)
    receipt_number = db.Column(db.String(50), unique=True, nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    
    # Receipt details
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    payment_method = db.Column(db.String(50), nullable=False)
    
    # File storage (optional)
    receipt_html = db.Column(db.Text, nullable=True)
    receipt_url = db.Column(db.String(255), nullable=True)
    
    generated_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    transaction = db.relationship("Transaction", back_populates="receipt")
    order = db.relationship("Order", backref=db.backref("receipts", lazy="dynamic"))
    user = db.relationship("User", backref=db.backref("receipts", lazy="dynamic"))

    @staticmethod
    def generate_receipt_number():
        """Generate a unique receipt number"""
        return f"RCPT{secrets.token_hex(6).upper()}"

    def to_dict(self):
        return {
            "id": self.id,
            "receipt_number": self.receipt_number,
            "transaction_id": self.transaction_id,
            "order_id": self.order_id,
            "user_id": self.user_id,
            "total_amount": float(self.total_amount),
            "payment_method": self.payment_method,
            "receipt_url": self.receipt_url,
            "generated_at": self.generated_at.isoformat() if self.generated_at else None,
        }


class PaymentMethod(db.Model):
    """
    Stores saved payment methods for users (dummy data only)
    """
    __tablename__ = "payment_methods"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    method_type = db.Column(db.String(50), nullable=False)  # card, wallet
    provider = db.Column(db.String(50), nullable=True)  # visa, mastercard, gpay, etc.
    masked_number = db.Column(db.String(20), nullable=True)
    expiry_month = db.Column(db.Integer, nullable=True)
    expiry_year = db.Column(db.Integer, nullable=True)
    is_default = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship("User", backref=db.backref("payment_methods", lazy="dynamic"))

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "method_type": self.method_type,
            "provider": self.provider,
            "masked_number": self.masked_number,
            "expiry_month": self.expiry_month,
            "expiry_year": self.expiry_year,
            "is_default": self.is_default,
            "is_active": self.is_active,
        }

