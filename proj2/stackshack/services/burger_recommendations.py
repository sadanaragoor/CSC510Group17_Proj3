"""
Burger Recommendation Service

Handles logic for selecting and preparing personalized burger recommendations
based on user dietary preferences.
"""

from data_burgers import PREDEFINED_BURGERS
from models.menu_item import MenuItem


class BurgerRecommendationService:
    """Service for getting personalized burger recommendations"""

    @staticmethod
    def get_user_preferences(user):
        """
        Extract user dietary preferences.

        Returns list of preference strings like ["vegan", "low_calorie"]
        or ["no_preference"] if none selected.
        """
        # Check if user has preference attributes
        preferences = []

        if hasattr(user, "pref_vegan") and user.pref_vegan:
            preferences.append("vegan")

        if hasattr(user, "pref_low_calorie") and user.pref_low_calorie:
            preferences.append("low_calorie")

        if hasattr(user, "pref_high_protein") and user.pref_high_protein:
            preferences.append("high_protein")

        if hasattr(user, "pref_gluten_free") and user.pref_gluten_free:
            preferences.append("gluten_free")

        # If no preferences selected, return no_preference
        if not preferences:
            preferences = ["no_preference"]

        return preferences

    @staticmethod
    def calculate_burger_price(ingredients):
        """
        Calculate total price of burger from ingredient list.

        Args:
            ingredients: List of ingredient names

        Returns:
            float: Total price, or None if any ingredient not found
        """
        total_price = 0.0

        for ingredient_name in ingredients:
            menu_item = MenuItem.query.filter_by(name=ingredient_name).first()
            if not menu_item:
                # Ingredient not found in database
                return None
            total_price += float(menu_item.price)

        return total_price

    @staticmethod
    def prepare_burger_data(burger_definition):
        """
        Prepare burger data with calculated price, stock availability, and all display info.

        Args:
            burger_definition: Dict with burger config

        Returns:
            Dict with burger data ready for template, or None if price calculation fails
        """
        price = BurgerRecommendationService.calculate_burger_price(
            burger_definition["ingredients"]
        )

        if price is None:
            # Skip burgers with missing ingredients
            return None

        # Check stock availability for all ingredients
        out_of_stock_items = []
        is_available = True

        for ingredient_name in burger_definition["ingredients"]:
            menu_item = MenuItem.query.filter_by(name=ingredient_name).first()
            if menu_item and menu_item.stock_quantity <= 0:
                out_of_stock_items.append(ingredient_name)
                is_available = False

        return {
            "name": burger_definition["name"],
            "slug": burger_definition["slug"],
            "description": burger_definition["description"],
            "ingredients": burger_definition["ingredients"],
            "dietary_tags": burger_definition["dietary_tags"],
            "image": burger_definition["image"],
            "price": price,
            "is_available": is_available,
            "out_of_stock_items": out_of_stock_items,
        }

    @staticmethod
    def get_recommendations_for_user(user):
        """
        Get personalized burger recommendations based on user preferences.

        Returns:
            Dict with structure:
            {
                'title': str (section title),
                'burgers': list of burger dicts
            }
        """
        preferences = BurgerRecommendationService.get_user_preferences(user)

        # Special case: Vegan + Gluten-Free combination
        if "vegan" in preferences and "gluten_free" in preferences:
            return BurgerRecommendationService._get_vegan_gf_recommendations(
                preferences
            )

        # Single preference cases
        if preferences == ["no_preference"]:
            return BurgerRecommendationService._get_no_preference_recommendations()

        if preferences == ["vegan"]:
            return BurgerRecommendationService._get_vegan_recommendations()

        if preferences == ["gluten_free"]:
            return BurgerRecommendationService._get_gluten_free_recommendations()

        if preferences == ["low_calorie"]:
            return BurgerRecommendationService._get_low_calorie_recommendations()

        if preferences == ["high_protein"]:
            return BurgerRecommendationService._get_high_protein_recommendations()

        # Multiple preferences (not vegan+gf combo)
        return BurgerRecommendationService._get_multi_preference_recommendations(
            preferences
        )

    @staticmethod
    def _get_vegan_gf_recommendations(all_preferences):
        """
        Get recommendations for users with both vegan AND gluten_free preferences.

        If they also have low_calorie, show both vegan+gf AND low_calorie sections.
        """
        sections = []

        # Always show vegan + gluten-free burgers
        vegan_gf_burgers = []
        for burger in PREDEFINED_BURGERS:
            if (
                "vegan" in burger["dietary_tags"]
                and "gluten_free" in burger["dietary_tags"]
            ):
                burger_data = BurgerRecommendationService.prepare_burger_data(burger)
                if burger_data:
                    vegan_gf_burgers.append(burger_data)

        sections.append(
            {
                "title": "Personalized Top Picks For You",
                "subtitle": "Vegan & Gluten-Free",
                "burgers": vegan_gf_burgers,
            }
        )

        # If they also have low_calorie, add low-calorie section
        if "low_calorie" in all_preferences:
            low_cal_burgers = []
            for burger in PREDEFINED_BURGERS:
                if burger["dietary_tags"] == ["low_calorie"]:
                    burger_data = BurgerRecommendationService.prepare_burger_data(
                        burger
                    )
                    if burger_data:
                        low_cal_burgers.append(burger_data)

            if low_cal_burgers:
                sections.append(
                    {
                        "title": "Low-Calorie Options",
                        "subtitle": "Light & Healthy",
                        "burgers": low_cal_burgers,
                    }
                )

        # If they also have high_protein, add high-protein section
        if "high_protein" in all_preferences:
            hp_burgers = []
            for burger in PREDEFINED_BURGERS:
                if burger["dietary_tags"] == ["high_protein"]:
                    burger_data = BurgerRecommendationService.prepare_burger_data(
                        burger
                    )
                    if burger_data:
                        hp_burgers.append(burger_data)

            if hp_burgers:
                sections.append(
                    {
                        "title": "High-Protein Options",
                        "subtitle": "Power-Packed",
                        "burgers": hp_burgers,
                    }
                )

        return sections

    @staticmethod
    def _get_no_preference_recommendations():
        """Get top picks for users with no dietary preferences"""
        burgers = []
        for burger in PREDEFINED_BURGERS:
            if burger["dietary_tags"] == ["no_preference"]:
                burger_data = BurgerRecommendationService.prepare_burger_data(burger)
                if burger_data:
                    burgers.append(burger_data)

        return [
            {
                "title": "Top Picks For You",
                "subtitle": "Crowd Favorites",
                "burgers": burgers,
            }
        ]

    @staticmethod
    def _get_vegan_recommendations():
        """Get recommendations for vegan-only users"""
        burgers = []
        for burger in PREDEFINED_BURGERS:
            if burger["dietary_tags"] == ["vegan"]:
                burger_data = BurgerRecommendationService.prepare_burger_data(burger)
                if burger_data:
                    burgers.append(burger_data)

        return [
            {
                "title": "Personalized Top Picks For You",
                "subtitle": "100% Plant-Based",
                "burgers": burgers,
            }
        ]

    @staticmethod
    def _get_gluten_free_recommendations():
        """Get recommendations for gluten-free-only users"""
        burgers = []
        for burger in PREDEFINED_BURGERS:
            if burger["dietary_tags"] == ["gluten_free"]:
                burger_data = BurgerRecommendationService.prepare_burger_data(burger)
                if burger_data:
                    burgers.append(burger_data)

        return [
            {
                "title": "Personalized Top Picks For You",
                "subtitle": "Gluten-Free Delights",
                "burgers": burgers,
            }
        ]

    @staticmethod
    def _get_low_calorie_recommendations():
        """Get recommendations for low-calorie users"""
        burgers = []
        for burger in PREDEFINED_BURGERS:
            if burger["dietary_tags"] == ["low_calorie"]:
                burger_data = BurgerRecommendationService.prepare_burger_data(burger)
                if burger_data:
                    burgers.append(burger_data)

        return [
            {
                "title": "Personalized Top Picks For You",
                "subtitle": "Light & Healthy",
                "burgers": burgers,
            }
        ]

    @staticmethod
    def _get_high_protein_recommendations():
        """Get recommendations for high-protein users"""
        burgers = []
        for burger in PREDEFINED_BURGERS:
            if burger["dietary_tags"] == ["high_protein"]:
                burger_data = BurgerRecommendationService.prepare_burger_data(burger)
                if burger_data:
                    burgers.append(burger_data)

        return [
            {
                "title": "Personalized Top Picks For You",
                "subtitle": "Power-Packed Protein",
                "burgers": burgers,
            }
        ]

    @staticmethod
    def _get_multi_preference_recommendations(preferences):
        """
        Get recommendations for users with multiple preferences (excluding vegan+gf combo).
        Shows a section for each preference.
        """
        sections = []

        preference_config = {
            "vegan": {
                "title": "Vegan Options",
                "subtitle": "100% Plant-Based",
                "tags": ["vegan"],
            },
            "gluten_free": {
                "title": "Gluten-Free Options",
                "subtitle": "Allergen-Friendly",
                "tags": ["gluten_free"],
            },
            "low_calorie": {
                "title": "Low-Calorie Options",
                "subtitle": "Light & Healthy",
                "tags": ["low_calorie"],
            },
            "high_protein": {
                "title": "High-Protein Options",
                "subtitle": "Power-Packed",
                "tags": ["high_protein"],
            },
        }

        for pref in preferences:
            if pref in preference_config:
                config = preference_config[pref]
                burgers = []

                for burger in PREDEFINED_BURGERS:
                    if burger["dietary_tags"] == config["tags"]:
                        burger_data = BurgerRecommendationService.prepare_burger_data(
                            burger
                        )
                        if burger_data:
                            burgers.append(burger_data)

                if burgers:
                    sections.append(
                        {
                            "title": config["title"],
                            "subtitle": config["subtitle"],
                            "burgers": burgers,
                        }
                    )

        return sections
