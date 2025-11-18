from database.db import db


class MenuItem(db.Model):
    __tablename__ = "menu_items"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    calories = db.Column(db.Integer)
    protein = db.Column(db.Integer)
    is_available = db.Column(db.Boolean, default=True)
    is_healthy_choice = db.Column(db.Boolean, default=False)
    image_url = db.Column(db.String(255))

    # 🔹 NEW: inventory fields
    stock_quantity = db.Column(db.Integer, nullable=False, default=0)
    low_stock_threshold = db.Column(db.Integer, nullable=False, default=10)

    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(
        db.DateTime,
        default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp(),
    )

    @property
    def is_low_stock(self):
        """True if this item is at or below the low-stock threshold (but not 0)."""
        return 0 < (self.stock_quantity or 0) <= (self.low_stock_threshold or 0)

    def to_dict(self):
        """Convert model to dictionary for easy JSON serialization"""
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "description": self.description,
            "price": float(self.price),
            "calories": self.calories,
            "protein": self.protein,
            "is_available": self.is_available,
            "is_healthy_choice": self.is_healthy_choice,
            "image_url": self.image_url,
            "stock_quantity": self.stock_quantity,
            "low_stock_threshold": self.low_stock_threshold,
            "is_low_stock": self.is_low_stock,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
