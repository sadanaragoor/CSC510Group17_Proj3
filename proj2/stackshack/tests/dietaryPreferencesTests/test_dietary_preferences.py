"""
Test cases for dietary preferences functionality.
"""
from models.user import User
from models.menu_item import MenuItem
from database.db import db


class TestDietaryPreferences:
    """Test cases for user dietary preferences."""
    
    def test_user_vegan_preference(self, app, vegan_user):
        """Test user with vegan preference."""
        with app.app_context():
            user = db.session.get(User, vegan_user)
            assert user.pref_vegan is True
            assert user.pref_gluten_free is False
    
    def test_user_gluten_free_preference(self, app, gluten_free_user):
        """Test user with gluten-free preference."""
        with app.app_context():
            user = db.session.get(User, gluten_free_user)
            assert user.pref_gluten_free is True
    
    def test_user_high_protein_preference(self, app, high_protein_user):
        """Test user with high protein preference."""
        with app.app_context():
            user = db.session.get(User, high_protein_user)
            assert user.pref_high_protein is True
    
    def test_user_low_calorie_preference(self, app, low_calorie_user):
        """Test user with low calorie preference."""
        with app.app_context():
            user = db.session.get(User, low_calorie_user)
            assert user.pref_low_calorie is True
    
    def test_update_dietary_preferences(self, app, vegan_user):
        """Test updating dietary preferences."""
        with app.app_context():
            user = db.session.get(User, vegan_user)
            user.pref_gluten_free = True
            user.pref_high_protein = True
            db.session.commit()
            
            updated_user = db.session.get(User, vegan_user)
            assert updated_user.pref_vegan is True
            assert updated_user.pref_gluten_free is True
            assert updated_user.pref_high_protein is True
    
    def test_filter_menu_items_by_preferences(self, app, vegan_user, sample_menu_items):
        """Test filtering menu items based on preferences."""
        with app.app_context():
            # This would typically be done in a service, but testing the concept
            user = db.session.get(User, vegan_user)
            
            # Get all items
            all_items = MenuItem.query.all()
            
            # Filter logic would check item attributes against preferences
            # For example, vegan users shouldn't see meat patties
            if user.pref_vegan:
                # In real implementation, this would filter out non-vegan items
                vegan_items = [item for item in all_items if "veggie" in item.name.lower() or "vegan" in item.name.lower()]
                assert len(vegan_items) > 0
    
    def test_multiple_preferences(self, app):
        """Test user with multiple dietary preferences."""
        with app.app_context():
            user = User(
                username="multipref",
                email="multipref@test.com",
                pref_vegan=True,
                pref_gluten_free=True,
                pref_high_protein=True,
                pref_low_calorie=True
            )
            user.set_password("testpass")
            db.session.add(user)
            db.session.commit()
            
            assert user.pref_vegan is True
            assert user.pref_gluten_free is True
            assert user.pref_high_protein is True
            assert user.pref_low_calorie is True
    
    def test_no_preferences(self, app):
        """Test user with no dietary preferences."""
        with app.app_context():
            user = User(username="nopref", email="nopref@test.com")
            user.set_password("testpass")
            db.session.add(user)
            db.session.commit()
            
            assert user.pref_vegan is False
            assert user.pref_gluten_free is False
            assert user.pref_high_protein is False
            assert user.pref_low_calorie is False

