from database.db import db
from datetime import datetime


class Order(db.Model):
    __tablename__ = "orders"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    total_price = db.Column(db.Numeric(10, 2), nullable=False)
    original_total = db.Column(db.Numeric(10, 2), nullable=True)  # Store original total before coupon
    status = db.Column(db.String(50), nullable=False, default="Pending")
    ordered_at = db.Column(db.DateTime, default=datetime.utcnow)

    items = db.relationship(
        "OrderItem", backref="order", lazy="dynamic", cascade="all, delete-orphan"
    )
    user = db.relationship("User", backref=db.backref("orders", lazy="dynamic"))

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "total_price": float(self.total_price),
            "status": self.status,
            "ordered_at": self.ordered_at.isoformat() if self.ordered_at else None,
            "items": [item.to_dict() for item in self.items.all()],
        }


class OrderItem(db.Model):
    __tablename__ = "order_items"

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"), nullable=False)
    menu_item_id = db.Column(db.Integer, nullable=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    burger_index = db.Column(db.Integer, nullable=True, default=None)  # Track which burger this item belongs to
    burger_name = db.Column(db.String(255), nullable=True, default=None)  # Store pre-defined burger name

    def to_dict(self):
        return {
            "id": self.id,
            "menu_item_id": self.menu_item_id,
            "name": self.name,
            "price": float(self.price),
            "quantity": self.quantity,
            "burger_index": self.burger_index,
            "burger_name": self.burger_name,
        }
