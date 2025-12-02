import random

def generate_surprise_burger(user_preferences, trending_combos, all_ingredients):
    """
    Creates a surprise burger based on:
    - user_preferences: dict {ingredient: score}
    - trending_combos: list of (ingredient1, ingredient2)
    - all_ingredients: list of str
    """

    # Step 1 – Weighted ingredient list
    weighted = []
    for ing in all_ingredients:
        weight = user_preferences.get(ing, 1)
        weighted.extend([ing] * weight)

    # Protect against empty or bad DB data
    if not weighted:
        weighted = all_ingredients

    # Step 2 – Choose 2–3 base ingredients
    base_count = random.choice([2, 3])
    base_choices = random.sample(weighted, k=base_count)

    # Step 3 – Possibly include one trending combination
    trending = random.choice(trending_combos) if trending_combos else []

    # Step 4 – Combine + remove duplicates
    burger = list(set(base_choices + list(trending)))

    return burger
