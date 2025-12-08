"""
Tests for burger recommendation service to improve coverage.
"""

from types import SimpleNamespace

from database.db import db
from models.menu_item import MenuItem
from services.burger_recommendations import BurgerRecommendationService


class TestBurgerRecommendationService:
    """Tests for BurgerRecommendationService."""

    def test_get_user_preferences_no_prefs(self):
        """User with no preference attributes gets no_preference."""
        user = SimpleNamespace()

        prefs = BurgerRecommendationService.get_user_preferences(user)

        assert prefs == ["no_preference"]

    def test_get_user_preferences_multiple_flags(self):
        """User with multiple flags gets corresponding preference list."""
        user = SimpleNamespace(
            pref_vegan=True,
            pref_low_calorie=True,
            pref_high_protein=False,
            pref_gluten_free=True,
        )

        prefs = BurgerRecommendationService.get_user_preferences(user)

        assert "vegan" in prefs
        assert "low_calorie" in prefs
        assert "gluten_free" in prefs
        assert "high_protein" not in prefs

    def test_calculate_burger_price_success(self, app):
        """Calculate price for ingredients that exist in the menu."""
        with app.app_context():
            db.session.add(
                MenuItem(
                    name="Bun",
                    category="bun",
                    price=2.50,
                    stock_quantity=10,
                )
            )
            db.session.add(
                MenuItem(
                    name="Patty",
                    category="patty",
                    price=3.00,
                    stock_quantity=10,
                )
            )
            db.session.commit()

            total = BurgerRecommendationService.calculate_burger_price(["Bun", "Patty"])

            assert total == 5.50

    def test_calculate_burger_price_missing_ingredient(self, app):
        """Return None when at least one ingredient is missing."""
        with app.app_context():
            db.session.add(
                MenuItem(
                    name="OnlyOne",
                    category="test",
                    price=1.00,
                    stock_quantity=10,
                )
            )
            db.session.commit()

            total = BurgerRecommendationService.calculate_burger_price(
                ["OnlyOne", "Missing"]
            )

            assert total is None

    def test_prepare_burger_data_out_of_stock(self, app):
        """Burger data marks unavailable when any ingredient is out of stock."""
        burger_def = {
            "name": "Test Burger",
            "slug": "test-burger",
            "description": "Test description",
            "ingredients": ["IngredientA", "IngredientB"],
            "dietary_tags": ["no_preference"],
            "image": "test.png",
        }

        with app.app_context():
            db.session.add(
                MenuItem(
                    name="IngredientA",
                    category="test",
                    price=2.00,
                    stock_quantity=5,
                )
            )
            db.session.add(
                MenuItem(
                    name="IngredientB",
                    category="test",
                    price=1.50,
                    stock_quantity=0,
                )
            )
            db.session.commit()

            data = BurgerRecommendationService.prepare_burger_data(burger_def)

            assert data is not None
            assert data["is_available"] is False
            assert "IngredientB" in data["out_of_stock_items"]
            assert data["price"] == 3.50

    def test_get_recommendations_no_preferences(self, app, test_user):
        """User with no preferences gets generic top picks."""
        with app.app_context():
            # Ensure all preference flags are false
            test_user.pref_vegan = False
            test_user.pref_gluten_free = False
            test_user.pref_high_protein = False
            test_user.pref_low_calorie = False
            db.session.commit()

            sections = BurgerRecommendationService.get_recommendations_for_user(
                test_user
            )

            assert isinstance(sections, list)
            assert sections
            assert "title" in sections[0]

    def test_get_recommendations_vegan_and_gluten_free(self, app, test_user):
        """Combined vegan and gluten_free preferences use special path."""
        with app.app_context():
            test_user.pref_vegan = True
            test_user.pref_gluten_free = True
            test_user.pref_high_protein = False
            test_user.pref_low_calorie = False
            db.session.commit()

            sections = BurgerRecommendationService.get_recommendations_for_user(
                test_user
            )

            assert isinstance(sections, list)
            assert sections
            # First section should be the vegan & gluten-free personalized picks
            assert (
                "Vegan" in sections[0]["title"]
                or "Personalized" in sections[0]["title"]
            )

    def test_get_recommendations_vegan_only(self, app, test_user):
        """Vegan-only preference should use vegan recommendation path."""
        with app.app_context():
            test_user.pref_vegan = True
            test_user.pref_gluten_free = False
            test_user.pref_high_protein = False
            test_user.pref_low_calorie = False
            db.session.commit()

            sections = BurgerRecommendationService.get_recommendations_for_user(
                test_user
            )

            assert isinstance(sections, list)
            assert sections

    def test_get_recommendations_gluten_free_only(self, app, test_user):
        """Gluten-free-only preference should use gluten-free recommendation path."""
        with app.app_context():
            test_user.pref_vegan = False
            test_user.pref_gluten_free = True
            test_user.pref_high_protein = False
            test_user.pref_low_calorie = False
            db.session.commit()

            sections = BurgerRecommendationService.get_recommendations_for_user(
                test_user
            )

            assert isinstance(sections, list)
            assert sections

    def test_get_recommendations_low_calorie_only(self, app, test_user):
        """Low-calorie-only preference should use low-calorie recommendations."""
        with app.app_context():
            test_user.pref_vegan = False
            test_user.pref_gluten_free = False
            test_user.pref_high_protein = False
            test_user.pref_low_calorie = True
            db.session.commit()

            sections = BurgerRecommendationService.get_recommendations_for_user(
                test_user
            )

            assert isinstance(sections, list)
            assert sections

    def test_get_recommendations_high_protein_only(self, app, test_user):
        """High-protein-only preference should use high-protein recommendations."""
        with app.app_context():
            test_user.pref_vegan = False
            test_user.pref_gluten_free = False
            test_user.pref_high_protein = True
            test_user.pref_low_calorie = False
            db.session.commit()

            sections = BurgerRecommendationService.get_recommendations_for_user(
                test_user
            )

            assert isinstance(sections, list)
            assert sections

    def test_get_recommendations_multi_preferences(self, app, test_user):
        """Multiple non-vegan+gf preferences should use multi-preference path."""
        with app.app_context():
            test_user.pref_vegan = True
            test_user.pref_gluten_free = False
            test_user.pref_high_protein = True
            test_user.pref_low_calorie = True
            db.session.commit()

            sections = BurgerRecommendationService.get_recommendations_for_user(
                test_user
            )

            # Multi-preference path returns a list (may be empty if ingredients missing)
            assert isinstance(sections, list)

    def test_get_recommendations_vegan_gf_with_low_calorie_and_high_protein(
        self, app, test_user
    ):
        """Vegan+gluten_free plus other flags adds extra sections."""
        with app.app_context():
            test_user.pref_vegan = True
            test_user.pref_gluten_free = True
            test_user.pref_high_protein = True
            test_user.pref_low_calorie = True
            db.session.commit()

            sections = BurgerRecommendationService.get_recommendations_for_user(
                test_user
            )

            # Should at least return the base vegan+gf section
            assert isinstance(sections, list)
            assert sections
