"""
Challenge Service - Manages daily and weekly challenge generation and checking.
"""

import random
from datetime import date, timedelta
from models.gamification import DailyBonus, WeeklyChallenge
from database.db import db


class ChallengeService:
    """Service for managing challenge generation and validation"""

    # Daily Challenge Definitions
    DAILY_CHALLENGES = {
        # Bun Challenges
        "go_keto": {
            "description": "Go Keto! - Order with keto bun",
            "condition": "keto_bun",
            "points": 40,
            "type": "bun",
            "check_func": "check_keto_bun",
        },
        "sesame_supreme": {
            "description": "Sesame Supreme - Choose sesame or black sesame bun",
            "condition": "sesame_bun",
            "points": 30,
            "type": "bun",
            "check_func": "check_sesame_bun",
        },
        "veggie_bun_day": {
            "description": "Veggie Bun Day - Pick beetroot or carrot bun",
            "condition": "veggie_bun",
            "points": 35,
            "type": "bun",
            "check_func": "check_veggie_bun",
        },
        "wheat_winner": {
            "description": "Wheat Winner - Order with wheat or honeywheat bun",
            "condition": "wheat_bun",
            "points": 25,
            "type": "bun",
            "check_func": "check_wheat_bun",
        },
        "plain_perfect": {
            "description": "Plain & Perfect - Stick with plain bun",
            "condition": "plain_bun",
            "points": 20,
            "type": "bun",
            "check_func": "check_plain_bun",
        },
        # Cheese Challenges
        "say_cheese": {
            "description": "Say Cheese! - Add any cheese to your burger",
            "condition": "any_cheese",
            "points": 25,
            "type": "cheese",
            "check_func": "check_any_cheese",
        },
        "cheddar_champion": {
            "description": "Cheddar Champion - Choose cheddar cheese",
            "condition": "cheddar_cheese",
            "points": 30,
            "type": "cheese",
            "check_func": "check_cheddar_cheese",
        },
        "swiss_surprise": {
            "description": "Swiss Surprise - Go with swiss cheese",
            "condition": "swiss_cheese",
            "points": 25,
            "type": "cheese",
            "check_func": "check_swiss_cheese",
        },
        "double_cheese_day": {
            "description": "Double Cheese Day - Add 2 different cheeses",
            "condition": "two_cheeses",
            "points": 50,
            "type": "cheese",
            "check_func": "check_two_cheeses",
        },
        "parmesan_power": {
            "description": "Parmesan Power - Add parmesan",
            "condition": "parmesan_cheese",
            "points": 25,
            "type": "cheese",
            "check_func": "check_parmesan_cheese",
        },
        # Patty Challenges
        "beef_it_up": {
            "description": "Beef It Up - Order beef or low-calorie beef patty",
            "condition": "beef_patty",
            "points": 35,
            "type": "patty",
            "check_func": "check_beef_patty",
        },
        "chicken_choice": {
            "description": "Chicken Choice - Get crispy chicken patty",
            "condition": "chicken_patty",
            "points": 30,
            "type": "patty",
            "check_func": "check_chicken_patty",
        },
        "go_green": {
            "description": "Go Green - Choose veg or mixed veg patty",
            "condition": "veg_patty",
            "points": 40,
            "type": "patty",
            "check_func": "check_veg_patty",
        },
        "pork_perfection": {
            "description": "Pork Perfection - Order with pork patty",
            "condition": "pork_patty",
            "points": 35,
            "type": "patty",
            "check_func": "check_pork_patty",
        },
        "healthy_protein": {
            "description": "Healthy Protein - Pick low-calorie beef or mixed veg patty",
            "condition": "healthy_patty",
            "points": 45,
            "type": "patty",
            "check_func": "check_healthy_patty",
        },
        # Sauce Challenges
        "mint_fresh": {
            "description": "Mint Fresh - Add green sauce to your burger",
            "condition": "green_sauce",
            "points": 20,
            "type": "sauce",
            "check_func": "check_green_sauce",
        },
        "classic_mayo": {
            "description": "Classic Mayo - Include mayo",
            "condition": "mayo",
            "points": 20,
            "type": "sauce",
            "check_func": "check_mayo",
        },
        "mustard_master": {
            "description": "Mustard Master - Add mustard sauce",
            "condition": "mustard",
            "points": 20,
            "type": "sauce",
            "check_func": "check_mustard",
        },
        "tomato_twist": {
            "description": "Tomato Twist - Choose tomato sauce",
            "condition": "tomato_sauce",
            "points": 20,
            "type": "sauce",
            "check_func": "check_tomato_sauce",
        },
        "sauce_combo": {
            "description": "Sauce Combo - Use 2+ different sauces",
            "condition": "two_sauces",
            "points": 40,
            "type": "sauce",
            "check_func": "check_two_sauces",
        },
        "all_sauces": {
            "description": "All Sauces - Add all 4 sauces",
            "condition": "all_sauces",
            "points": 60,
            "type": "sauce",
            "check_func": "check_all_sauces",
        },
        # Topping Challenges
        "pickle_power": {
            "description": "Pickle Power - Add pickles",
            "condition": "pickles",
            "points": 30,
            "type": "topping",
            "check_func": "check_pickles",
        },
        "tomato_time": {
            "description": "Tomato Time - Include fresh tomato",
            "condition": "tomato",
            "points": 25,
            "type": "topping",
            "check_func": "check_tomato",
        },
        "lettuce_love": {
            "description": "Lettuce Love - Add lettuce",
            "condition": "lettuce",
            "points": 20,
            "type": "topping",
            "check_func": "check_lettuce",
        },
        "onion_obsession": {
            "description": "Onion Obsession - Include onion",
            "condition": "onion",
            "points": 25,
            "type": "topping",
            "check_func": "check_onion",
        },
        "capsicum_crunch": {
            "description": "Capsicum Crunch - Add capsicum",
            "condition": "capsicum",
            "points": 30,
            "type": "topping",
            "check_func": "check_capsicum",
        },
        "veggie_lover": {
            "description": "Veggie Lover - Add 3+ toppings",
            "condition": "three_toppings",
            "points": 50,
            "type": "topping",
            "check_func": "check_three_toppings",
        },
        "full_stack": {
            "description": "Full Stack - Include all 5 toppings",
            "condition": "all_toppings",
            "points": 75,
            "type": "topping",
            "check_func": "check_all_toppings",
        },
        # Behavioral Challenges
        "early_bird_special": {
            "description": "Early Bird Special - Order before 11 AM",
            "condition": "before_11am",
            "points": 50,
            "type": "behavioral",
            "check_func": "check_before_11am",
        },
        "beat_the_rush": {
            "description": "Beat the Rush - Order between 2-4 PM",
            "condition": "between_2_4pm",
            "points": 35,
            "type": "behavioral",
            "check_func": "check_between_2_4pm",
        },
        "late_night_bite": {
            "description": "Late Night Bite - Order after 8 PM",
            "condition": "after_8pm",
            "points": 40,
            "type": "behavioral",
            "check_func": "check_after_8pm",
        },
        "speed_pickup": {
            "description": "Speed Pickup - Collect within 5 minutes of ready",
            "condition": "speed_pickup",
            "points": 30,
            "type": "behavioral",
            "check_func": "check_speed_pickup",
        },
        "mystery_box_monday": {
            "description": "Mystery Box Monday - Order a surprise burger",
            "condition": "surprise_burger",
            "points": 60,
            "type": "behavioral",
            "check_func": "check_surprise_burger",
        },
        "new_creation": {
            "description": "New Creation - Build something you've never ordered before",
            "condition": "new_combination",
            "points": 45,
            "type": "behavioral",
            "check_func": "check_new_combination",
        },
        "healthy_choice_hero": {
            "description": "Healthy Choice Hero - Order a burger with 💚 Healthy ingredients only",
            "condition": "all_healthy",
            "points": 55,
            "type": "behavioral",
            "check_func": "check_all_healthy",
        },
        # Time-Specific
        "lunch_rush_hero": {
            "description": "Lunch Rush Hero - Order between 12-1 PM",
            "condition": "lunch_rush",
            "points": 30,
            "type": "time",
            "check_func": "check_lunch_rush",
        },
        "two_twenty_two": {
            "description": "2:22 Lucky Time - Order at exactly 2:22 PM",
            "condition": "exact_222",
            "points": 100,
            "type": "time",
            "check_func": "check_exact_222",
        },
        "happy_half_hour": {
            "description": "Happy Half-Hour - First 10 orders of any half-hour",
            "condition": "half_hour_first",
            "points": 25,
            "type": "time",
            "check_func": "check_half_hour_first",
        },
    }

    # Weekly Challenge Definitions
    WEEKLY_CHALLENGES = {
        # Bun Adventures
        "bun_explorer": {
            "description": "Bun Explorer - Try 3 different buns this week",
            "condition": "three_different_buns",
            "points": 150,
            "target": 3,
            "type": "bun",
        },
        "healthy_bun_week": {
            "description": "Healthy Bun Week - Order 3 burgers with 💚 healthy buns",
            "condition": "three_healthy_buns",
            "points": 175,
            "target": 3,
            "type": "bun",
        },
        "premium_bun_challenge": {
            "description": "Premium Bun Challenge - Try keto, black sesame, and sesame buns",
            "condition": "premium_buns",
            "points": 200,
            "target": 3,
            "type": "bun",
        },
        # Cheese Quest
        "cheese_connoisseur": {
            "description": "Cheese Connoisseur - Try all 4 cheese types this week",
            "condition": "all_cheeses",
            "points": 175,
            "target": 4,
            "type": "cheese",
        },
        "no_cheese_challenge": {
            "description": "No Cheese Challenge - Order 3 burgers without any cheese",
            "condition": "no_cheese_three",
            "points": 100,
            "target": 3,
            "type": "cheese",
        },
        "cheesy_week": {
            "description": "Cheesy Week - Add cheese to every order (min 3 orders)",
            "condition": "cheese_every_order",
            "points": 125,
            "target": 3,
            "type": "cheese",
        },
        # Patty Party
        "patty_sampler": {
            "description": "Patty Sampler - Try 4 different patties",
            "condition": "four_patties",
            "points": 200,
            "target": 4,
            "type": "patty",
        },
        "meat_lover_week": {
            "description": "Meat Lover Week - Order beef, chicken, and pork patties",
            "condition": "three_meat_patties",
            "points": 150,
            "target": 3,
            "type": "patty",
        },
        "vegetarian_victory": {
            "description": "Vegetarian Victory - Order 3 burgers with veg/mixed veg patties",
            "condition": "three_veg_patties",
            "points": 175,
            "target": 3,
            "type": "patty",
        },
        "healthy_protein_week": {
            "description": "Healthy Protein Week - Use low-calorie beef or mixed veg in 3 orders",
            "condition": "three_healthy_patties",
            "points": 160,
            "target": 3,
            "type": "patty",
        },
        # Sauce Safari
        "sauce_master": {
            "description": "Sauce Master - Use all 4 sauces across multiple orders",
            "condition": "all_four_sauces",
            "points": 150,
            "target": 4,
            "type": "sauce",
        },
        "sauce_mixer": {
            "description": "Sauce Mixer - Try 3 different sauce combinations",
            "condition": "three_sauce_combos",
            "points": 125,
            "target": 3,
            "type": "sauce",
        },
        "green_gang": {
            "description": "Green Gang - Add green sauce to 3 burgers",
            "condition": "green_sauce_three",
            "points": 100,
            "target": 3,
            "type": "sauce",
        },
        # Topping Tour
        "topping_collector": {
            "description": "Topping Collector - Use all 5 toppings this week",
            "condition": "all_five_toppings",
            "points": 200,
            "target": 5,
            "type": "topping",
        },
        "fresh_crunchy": {
            "description": "Fresh & Crunchy - Include lettuce, tomato, and capsicum in one order, 3 times",
            "condition": "fresh_combo_three",
            "points": 175,
            "target": 3,
            "type": "topping",
        },
        "pickle_pro": {
            "description": "Pickle Pro - Add pickles to 4 burgers this week",
            "condition": "pickles_four",
            "points": 125,
            "target": 4,
            "type": "topping",
        },
        "veggie_load": {
            "description": "Veggie Load - Order with 4+ toppings, 3 times",
            "condition": "four_toppings_three",
            "points": 180,
            "target": 3,
            "type": "topping",
        },
        # Frequency Challenges
        "trio_time": {
            "description": "Trio Time - Order 3 times this week",
            "condition": "three_orders",
            "points": 100,
            "target": 3,
            "type": "frequency",
        },
        "daily_dedication": {
            "description": "Daily Dedication - Order 5 different days",
            "condition": "five_days",
            "points": 200,
            "target": 5,
            "type": "frequency",
        },
        "weekend_warrior": {
            "description": "Weekend Warrior - Order both Saturday AND Sunday",
            "condition": "weekend_both",
            "points": 75,
            "target": 2,
            "type": "frequency",
        },
        "weekday_regular": {
            "description": "Weekday Regular - Order 4 weekdays in a row",
            "condition": "four_weekdays",
            "points": 150,
            "target": 4,
            "type": "frequency",
        },
        # Creative & Healthy Challenges
        "healthy_eater": {
            "description": "Healthy Eater - Order 3 burgers with all 💚 ingredients",
            "condition": "all_healthy_three",
            "points": 225,
            "target": 3,
            "type": "healthy",
        },
        "calorie_conscious": {
            "description": "Calorie Conscious - Build 3 burgers under 500 calories",
            "condition": "low_cal_three",
            "points": 150,
            "target": 3,
            "type": "healthy",
        },
        "protein_pursuit": {
            "description": "Protein Pursuit - Order 3 burgers with 30g+ protein",
            "condition": "high_protein_three",
            "points": 175,
            "target": 3,
            "type": "healthy",
        },
        "budget_builder": {
            "description": "Budget Builder - Create 3 burgers under $10 each",
            "condition": "budget_three",
            "points": 100,
            "target": 3,
            "type": "creative",
        },
        "premium_experience": {
            "description": "Premium Experience - Order with keto bun, cheddar cheese, and beef patty 2 times",
            "condition": "premium_combo_two",
            "points": 150,
            "target": 2,
            "type": "creative",
        },
        # Variety & Adventure
        "surprise_me_x3": {
            "description": "Surprise Me x3 - Order 3 mystery boxes",
            "condition": "three_surprises",
            "points": 200,
            "target": 3,
            "type": "variety",
        },
        "never_repeat": {
            "description": "Never Repeat - Order 5 completely different burgers",
            "condition": "five_different",
            "points": 250,
            "target": 5,
            "type": "variety",
        },
        "copycat_challenge": {
            "description": "Copycat Challenge - Try 2 popular customer creations",
            "condition": "two_popular",
            "points": 125,
            "target": 2,
            "type": "variety",
        },
        "opposite_day": {
            "description": "Opposite Day - Order the opposite of your usual burger",
            "condition": "opposite_burger",
            "points": 100,
            "target": 1,
            "type": "variety",
        },
        # Special Bonus Mechanics
        "green_streak": {
            "description": "💚 Green Streak - Order with 3+ healthy ingredients, 3 days in a row",
            "condition": "healthy_streak",
            "points": 150,
            "target": 3,
            "type": "streak",
        },
        "balanced_week": {
            "description": "Balanced Week - Mix healthy and indulgent orders (2 of each)",
            "condition": "balanced_orders",
            "points": 125,
            "target": 4,
            "type": "healthy",
        },
        "favorite_ingredient": {
            "description": "Favorite Ingredient - Order the same topping/sauce 5 times",
            "condition": "same_ingredient_five",
            "points": 75,
            "target": 5,
            "type": "loyalty",
        },
        "classic_combo": {
            "description": "Classic Combo - Order plain bun + beef patty + american cheese 3 times",
            "condition": "classic_combo_three",
            "points": 100,
            "target": 3,
            "type": "loyalty",
        },
        "budget_week": {
            "description": "Budget Week - All orders under $12, minimum 3 orders",
            "condition": "budget_week_three",
            "points": 125,
            "target": 3,
            "type": "price",
        },
        "premium_week": {
            "description": "Premium Week - Spend $18+ per order, 3 times",
            "condition": "premium_week_three",
            "points": 175,
            "target": 3,
            "type": "price",
        },
    }

    @staticmethod
    def generate_daily_challenges(today=None, max_challenges=2):
        """Generate up to 2 random daily challenges for a given date"""
        if today is None:
            today = date.today()

        # Check existing challenges for today
        existing = DailyBonus.query.filter_by(bonus_date=today, is_active=True).all()
        existing_count = len(existing)

        if existing_count >= max_challenges:
            return existing  # Already have max challenges

        # Get available challenge keys
        available_challenges = list(ChallengeService.DAILY_CHALLENGES.keys())

        # Remove challenges that already exist today
        existing_conditions = [db.condition for db in existing]
        existing_conditions_flat = existing_conditions

        # Select random challenges
        challenges_to_create = max_challenges - existing_count
        selected_keys = random.sample(
            available_challenges, min(challenges_to_create, len(available_challenges))
        )

        created = []
        for key in selected_keys:
            challenge_def = ChallengeService.DAILY_CHALLENGES[key]

            # Check if this condition already exists today
            if challenge_def["condition"] in existing_conditions_flat:
                continue

            # Double-check that this condition doesn't already exist (race condition protection)
            existing_with_condition = DailyBonus.query.filter_by(
                bonus_date=today, condition=challenge_def["condition"], is_active=True
            ).first()

            if existing_with_condition:
                existing_conditions_flat.append(challenge_def["condition"])
                continue

            try:
                bonus = DailyBonus(
                    bonus_date=today,
                    description=challenge_def["description"],
                    condition=challenge_def["condition"],
                    points_reward=challenge_def["points"],
                    is_active=True,
                )
                db.session.add(bonus)
                created.append(bonus)
                existing_conditions_flat.append(challenge_def["condition"])
            except Exception as e:
                # Handle any database errors (e.g., unique constraint still exists)
                db.session.rollback()
                print(f"Warning: Could not create daily bonus {key}: {e}")
                continue

        if created:
            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                print(f"Warning: Could not commit daily bonuses: {e}")

        # Return all challenges for today
        return DailyBonus.query.filter_by(bonus_date=today, is_active=True).all()

    @staticmethod
    def generate_weekly_challenges(week_start=None, max_challenges=3):
        """Generate up to 3 random weekly challenges for a given week"""
        if week_start is None:
            today = date.today()
            days_since_monday = today.weekday()
            week_start = today - timedelta(days=days_since_monday)

        week_end = week_start + timedelta(days=6)

        # Check existing challenges for this week
        existing = WeeklyChallenge.query.filter(
            WeeklyChallenge.week_start == week_start,
            WeeklyChallenge.week_end == week_end,
            WeeklyChallenge.is_active,
        ).all()
        existing_count = len(existing)

        if existing_count >= max_challenges:
            return existing  # Already have max challenges

        # Get available challenge keys
        available_challenges = list(ChallengeService.WEEKLY_CHALLENGES.keys())

        # Remove challenges that already exist this week
        existing_conditions = [ch.condition for ch in existing]

        # Select random challenges
        challenges_to_create = max_challenges - existing_count
        selected_keys = random.sample(
            available_challenges, min(challenges_to_create, len(available_challenges))
        )

        created = []
        for key in selected_keys:
            challenge_def = ChallengeService.WEEKLY_CHALLENGES[key]

            # Check if this condition already exists this week
            if challenge_def["condition"] in existing_conditions:
                continue

            # Double-check that this condition doesn't already exist (race condition protection)
            existing_with_condition = WeeklyChallenge.query.filter(
                WeeklyChallenge.week_start == week_start,
                WeeklyChallenge.week_end == week_end,
                WeeklyChallenge.condition == challenge_def["condition"],
                WeeklyChallenge.is_active,
            ).first()

            if existing_with_condition:
                existing_conditions.append(challenge_def["condition"])
                continue

            try:
                challenge = WeeklyChallenge(
                    week_start=week_start,
                    week_end=week_end,
                    description=challenge_def["description"],
                    condition=challenge_def["condition"],
                    points_reward=challenge_def["points"],
                    is_active=True,
                )
                db.session.add(challenge)
                created.append(challenge)
                existing_conditions.append(challenge_def["condition"])
            except Exception as e:
                # Handle any database errors
                db.session.rollback()
                print(f"Warning: Could not create weekly challenge {key}: {e}")
                continue

        if created:
            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                print(f"Warning: Could not commit weekly challenges: {e}")

        # Return all challenges for this week
        return WeeklyChallenge.query.filter(
            WeeklyChallenge.week_start == week_start,
            WeeklyChallenge.week_end == week_end,
            WeeklyChallenge.is_active,
        ).all()
