"""
Validation script for burger definitions.

Checks if all burger ingredients exist in the menu_items database
and reports any missing ingredients or pricing issues.
"""

from app import create_app
from data_burgers import PREDEFINED_BURGERS
from models.menu_item import MenuItem


def validate_burgers():
    """Validate all burger definitions against database."""
    app = create_app("development")
    with app.app_context():
        print("\n" + "=" * 70)
        print("VALIDATING BURGER DEFINITIONS")
        print("=" * 70)

        all_valid = True
        missing_ingredients = set()
        burger_count = len(PREDEFINED_BURGERS)

        print(f"\nTotal burgers defined: {burger_count}")
        print("\nChecking each burger...\n")

        for burger in PREDEFINED_BURGERS:
            print(f"[BURGER] {burger['name']}")
            print(f"   Slug: {burger['slug']}")
            print(f"   Tags: {', '.join(burger['dietary_tags'])}")
            print(f"   Ingredients: {len(burger['ingredients'])}")

            # Check each ingredient
            burger_price = 0.0
            burger_valid = True

            for ingredient_name in burger["ingredients"]:
                menu_item = MenuItem.query.filter_by(name=ingredient_name).first()

                if not menu_item:
                    print(f"   [ERROR] MISSING: '{ingredient_name}'")
                    missing_ingredients.add(ingredient_name)
                    burger_valid = False
                    all_valid = False
                else:
                    price = float(menu_item.price)
                    burger_price += price
                    # print(f"   [OK] {ingredient_name}: ${price:.2f}")

            if burger_valid:
                print(f"   [OK] Total Price: ${burger_price:.2f}")
            else:
                print(f"   [WARNING] Cannot calculate price (missing ingredients)")

            print()

        # Summary
        print("=" * 70)
        print("VALIDATION SUMMARY")
        print("=" * 70)

        if all_valid:
            print("\n[SUCCESS] ALL BURGERS VALID!")
            print(f"   - {burger_count} burgers defined")
            print("   - All ingredients found in database")
            print("   - Prices can be calculated")
        else:
            print(f"\n[FAILED] VALIDATION FAILED!")
            print(f"\n   Missing ingredients ({len(missing_ingredients)}):")
            for ingredient in sorted(missing_ingredients):
                print(f"   - {ingredient}")
            print(
                "\n   Please add these ingredients to your database or update burger definitions."
            )

        print("\n" + "=" * 70)

        # Group burgers by dietary tags
        print("\nBURGERS BY CATEGORY")
        print("=" * 70)

        categories = {}
        for burger in PREDEFINED_BURGERS:
            tags_key = ", ".join(sorted(burger["dietary_tags"]))
            if tags_key not in categories:
                categories[tags_key] = []
            categories[tags_key].append(burger["name"])

        for category, burger_names in sorted(categories.items()):
            print(f"\n{category.upper()} ({len(burger_names)} burgers):")
            for name in burger_names:
                print(f"  - {name}")

        print("\n" + "=" * 70)


if __name__ == "__main__":
    validate_burgers()
