"""
Test cases for inventory management.
"""

from models.menu_item import MenuItem
from database.db import db


class TestInventoryManagement:
    """Test cases for inventory management."""

    def test_item_availability(self, app, sample_menu_items):
        """Test checking item availability."""
        with app.app_context():
            item = db.session.get(MenuItem, sample_menu_items[0])
            assert item.is_available is True

            item2 = db.session.get(MenuItem, sample_menu_items[1])
            assert item2.is_available is False

    def test_update_stock_quantity(self, app, sample_menu_items):
        """Test updating stock quantity."""
        with app.app_context():
            item = db.session.get(MenuItem, sample_menu_items[0])
            (item.stock_quantity if hasattr(item, "stock_quantity") else None)

            if hasattr(item, "stock_quantity"):
                item.stock_quantity = 20
                db.session.commit()

                updated_item = db.session.get(MenuItem, sample_menu_items[0])
                assert updated_item.stock_quantity == 20

    def test_item_out_of_stock(self, app, sample_menu_items):
        """Test marking item as out of stock."""
        with app.app_context():
            item = db.session.get(MenuItem, sample_menu_items[0])
            item.is_available = False
            if hasattr(item, "stock_quantity"):
                item.stock_quantity = 0
            db.session.commit()

            updated_item = db.session.get(MenuItem, sample_menu_items[0])
            assert updated_item.is_available is False

    def test_item_back_in_stock(self, app, sample_menu_items):
        """Test marking item as back in stock."""
        with app.app_context():
            item = db.session.get(MenuItem, sample_menu_items[1])
            item.is_available = True
            if hasattr(item, "stock_quantity"):
                item.stock_quantity = 10
            db.session.commit()

            updated_item = db.session.get(MenuItem, sample_menu_items[1])
            assert updated_item.is_available is True

    def test_filter_available_items(self, app, sample_menu_items):
        """Test filtering available items."""
        with app.app_context():
            available_items = MenuItem.query.filter_by(is_available=True).all()
            assert len(available_items) >= 1

            unavailable_items = MenuItem.query.filter_by(is_available=False).all()
            assert len(unavailable_items) >= 1
