from models.menu_item import MenuItem
from database.db import db
from flask_login import current_user


class MenuController:

    @staticmethod
    def get_all_items():
        """Get all menu items (for management views)."""
        try:
            items = MenuItem.query.order_by(MenuItem.category, MenuItem.name).all()
            return True, "Items retrieved successfully", items
        except Exception as e:
            return False, f"Error: {str(e)}", None

    @staticmethod
    def get_item_by_id(item_id):
        """Get a specific menu item by ID"""
        try:
            item = MenuItem.query.get(item_id)
            if not item:
                return False, "Item not found", None
            return True, "Item retrieved successfully", item
        except Exception as e:
            return False, f"Error: {str(e)}", None

    @staticmethod
    def create_item(
        name,
        category,
        description,
        price,
        calories=None,
        protein=None,
        image_url=None,
        stock_quantity=0,
        low_stock_threshold=10,
    ):
        """Create a new menu item - Admin/Staff only"""
        # Check authorization
        if not current_user.is_authenticated or current_user.role not in [
            "admin",
            "staff",
        ]:
            return False, "Unauthorized: Only admins and staff can create items", None

        # Validation
        if not name or not category or not price:
            return False, "Name, category, and price are required", None

        try:
            item = MenuItem(
                name=name,
                category=category,
                description=description,
                price=price,
                calories=calories,
                protein=protein,
                image_url=image_url,
                stock_quantity=int(stock_quantity) if stock_quantity else 0,
                low_stock_threshold=int(low_stock_threshold)
                if low_stock_threshold
                else 10,
            )
            # Auto-availability based on stock
            item.is_available = item.stock_quantity > 0

            db.session.add(item)
            db.session.commit()
            return True, "Item created successfully", item
        except Exception as e:
            db.session.rollback()
            return False, f"Error: {str(e)}", None

    @staticmethod
    def update_item(
        item_id,
        name=None,
        category=None,
        description=None,
        price=None,
        calories=None,
        protein=None,
        image_url=None,
    ):
        """Update an existing menu item - Admin/Staff only"""
        # Check authorization
        if not current_user.is_authenticated or current_user.role not in [
            "admin",
            "staff",
        ]:
            return False, "Unauthorized: Only admins and staff can update items", None

        try:
            item = MenuItem.query.get(item_id)
            if not item:
                return False, "Item not found", None

            # Update fields if provided
            if name is not None:
                item.name = name
            if category is not None:
                item.category = category
            if description is not None:
                item.description = description
            if price is not None:
                item.price = price
            if calories is not None:
                item.calories = calories
            if protein is not None:
                item.protein = protein
            if image_url is not None:
                item.image_url = image_url

            db.session.commit()
            return True, "Item updated successfully", item
        except Exception as e:
            db.session.rollback()
            return False, f"Error: {str(e)}", None

    @staticmethod
    def delete_item(item_id):
        """Delete a menu item - Admin only"""
        # Check authorization
        if not current_user.is_authenticated or current_user.role != "admin":
            return False, "Unauthorized: Only admins can delete items", None

        try:
            item = MenuItem.query.get(item_id)
            if not item:
                return False, "Item not found", None

            db.session.delete(item)
            db.session.commit()
            return True, "Item deleted successfully", None
        except Exception as e:
            db.session.rollback()
            return False, f"Error: {str(e)}", None

    @staticmethod
    def toggle_availability(item_id):
        """Toggle the availability status of a menu item - Admin/Staff only"""
        # Check authorization
        if not current_user.is_authenticated or current_user.role not in [
            "admin",
            "staff",
        ]:
            return (
                False,
                "Unauthorized: Only admins and staff can toggle availability",
                None,
            )

        try:
            item = MenuItem.query.get(item_id)
            if not item:
                return False, "Item not found", None

            # If currently unavailable and stock is zero, don't allow marking it available
            if not item.is_available and item.stock_quantity <= 0:
                return (
                    False,
                    "Cannot mark available: stock is 0. Please update inventory first.",
                    None,
                )

            item.is_available = not item.is_available
            db.session.commit()
            status = "available" if item.is_available else "unavailable"
            return True, f"Item marked as {status}", item
        except Exception as e:
            db.session.rollback()
            return False, f"Error: {str(e)}", None

    @staticmethod
    def toggle_healthy_choice(item_id):
        """Toggle the healthy choice status of a menu item - Admin/Staff only"""
        # Check authorization
        if not current_user.is_authenticated or current_user.role not in [
            "admin",
            "staff",
        ]:
            return (
                False,
                "Unauthorized: Only admins and staff can toggle healthy choice",
                None,
            )

        try:
            item = MenuItem.query.get(item_id)
            if not item:
                return False, "Item not found", None

            item.is_healthy_choice = not item.is_healthy_choice
            db.session.commit()
            status = (
                "healthy choice" if item.is_healthy_choice else "not a healthy choice"
            )
            return True, f"Item marked as {status}", item
        except Exception as e:
            db.session.rollback()
            return False, f"Error: {str(e)}", None

    @staticmethod
    def get_items_by_category(category):
        """Get all items in a specific category"""
        try:
            items = (
                MenuItem.query.filter_by(category=category)
                .order_by(MenuItem.name)
                .all()
            )
            return True, "Items retrieved successfully", items
        except Exception as e:
            return False, f"Error: {str(e)}", None

    @staticmethod
    def get_available_items():
        """Get only available menu items (for customer view)"""
        try:
            items = (
                MenuItem.query.filter_by(is_available=True)
                .filter(MenuItem.stock_quantity > 0)  # 🔹 only in-stock
                .order_by(MenuItem.category, MenuItem.name)
                .all()
            )
            return True, "Available items retrieved successfully", items
        except Exception as e:
            return False, f"Error: {str(e)}", None

    @staticmethod
    def get_healthy_choices():
        """Get items marked as healthy choices"""
        try:
            items = (
                MenuItem.query.filter_by(is_healthy_choice=True, is_available=True)
                .filter(MenuItem.stock_quantity > 0)  # 🔹 only in-stock
                .order_by(MenuItem.name)
                .all()
            )
            return True, "Healthy choices retrieved successfully", items
        except Exception as e:
            return False, f"Error: {str(e)}", None

    # 🔹 INVENTORY-SPECIFIC METHODS

    @staticmethod
    def get_low_stock_items():
        """Items that are running low (but not completely out-of-stock)."""
        try:
            items = (
                MenuItem.query
                .filter(MenuItem.stock_quantity > 0)
                .filter(MenuItem.stock_quantity <= MenuItem.low_stock_threshold)
                .order_by(MenuItem.stock_quantity.asc())
                .all()
            )
            return True, "Low stock items retrieved successfully", items
        except Exception as e:
            return False, f"Error: {str(e)}", None

    @staticmethod
    def update_stock(item_id, new_stock, new_threshold=None):
        """Update stock quantity (and optionally low-stock threshold)."""
        try:
            item = db.session.get(MenuItem, int(item_id))
            if not item:
                return False, "Item not found", None

            item.stock_quantity = max(0, int(new_stock))
            if new_threshold is not None and new_threshold != "":
                item.low_stock_threshold = max(0, int(new_threshold))

            # Auto-update availability based on stock
            item.is_available = item.stock_quantity > 0

            db.session.commit()
            return True, "Stock updated successfully", item
        except Exception as e:
            db.session.rollback()
            return False, f"Error updating stock: {str(e)}", None
