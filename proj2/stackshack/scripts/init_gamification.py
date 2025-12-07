"""
Initialize gamification system - Create default badges and sample challenges.
Run this script once to set up the gamification system.
"""

import sys
import os

# Add the parent directory to the path so we can import from stackshack
script_dir = os.path.dirname(os.path.abspath(__file__))
stackshack_dir = os.path.dirname(script_dir)
if stackshack_dir not in sys.path:
    sys.path.insert(0, stackshack_dir)

from database.db import db
from models.gamification import Badge, DailyBonus, WeeklyChallenge
from datetime import date, timedelta
from app import create_app


def init_badges():
    """Create all default badges if they don't exist"""
    badges = [
        # Ingredient Explorer Badges
        {
            "name": "Sauce Collector",
            "slug": "sauce_collector",
            "description": "Tried all sauces",
            "badge_type": "ingredient",
            "icon": "🍯",
            "rarity": "rare",
        },
        {
            "name": "Veggie Champion",
            "slug": "veggie_champion",
            "description": "Ordered 4+ vegetables",
            "badge_type": "ingredient",
            "icon": "🥬",
            "rarity": "common",
        },
        {
            "name": "Carnivore King",
            "slug": "carnivore_king",
            "description": "Tried all patty options",
            "badge_type": "ingredient",
            "icon": "🍖",
            "rarity": "rare",
        },
        {
            "name": "Brave Soul",
            "slug": "brave_soul",
            "description": "Ordered spiciest ingredients",
            "badge_type": "ingredient",
            "icon": "🌶️",
            "rarity": "common",
        },
        {
            "name": "Classic Lover",
            "slug": "classic_lover",
            "description": "Ordered same burger 5+ times",
            "badge_type": "behavioral",
            "icon": "❤️",
            "rarity": "common",
        },
        # Behavioral Badges
        {
            "name": "Lunch Rush Warrior",
            "slug": "lunch_rush_warrior",
            "description": "10 orders between 12-1 PM",
            "badge_type": "behavioral",
            "icon": "🍽️",
            "rarity": "rare",
        },
        {
            "name": "Early Bird",
            "slug": "early_bird",
            "description": "5 orders before 11 AM",
            "badge_type": "behavioral",
            "icon": "🌅",
            "rarity": "common",
        },
        {
            "name": "Late Night Snacker",
            "slug": "late_night_snacker",
            "description": "5 orders after 8 PM",
            "badge_type": "behavioral",
            "icon": "🌙",
            "rarity": "common",
        },
        {
            "name": "StackShack Regular",
            "slug": "stackshack_regular",
            "description": "20 total orders",
            "badge_type": "behavioral",
            "icon": "⭐",
            "rarity": "common",
        },
        {
            "name": "Century Club",
            "slug": "century_club",
            "description": "100 total orders",
            "badge_type": "behavioral",
            "icon": "💯",
            "rarity": "epic",
        },
        {
            "name": "Mystery Box Master",
            "slug": "mystery_box_master",
            "description": "5 surprise box orders",
            "badge_type": "behavioral",
            "icon": "🎁",
            "rarity": "rare",
        },
    ]

    created = 0
    for badge_data in badges:
        existing = Badge.query.filter_by(slug=badge_data["slug"]).first()
        if not existing:
            badge = Badge(**badge_data)
            db.session.add(badge)
            created += 1
            print(f"Created badge: {badge_data['name']}")
        else:
            print(f"Badge already exists: {badge_data['name']}")

    db.session.commit()
    print(f"\n✓ Created {created} new badges")
    return created


def init_sample_daily_bonus():
    """Create a sample daily bonus for today"""
    today = date.today()
    existing = DailyBonus.query.filter_by(bonus_date=today).first()

    if not existing:
        # Sample daily bonus
        bonus = DailyBonus(
            bonus_date=today,
            description="Order with pickles today",
            condition="order with pickles",
            points_reward=30,
            is_active=True,
        )
        db.session.add(bonus)
        db.session.commit()
        print(f"✓ Created daily bonus for {today}")
    else:
        print(f"Daily bonus already exists for {today}")


def init_sample_weekly_challenge():
    """Create a sample weekly challenge for this week"""
    today = date.today()
    # Start of week (Monday)
    days_since_monday = today.weekday()
    week_start = today - timedelta(days=days_since_monday)
    week_end = week_start + timedelta(days=6)

    existing = WeeklyChallenge.query.filter(
        WeeklyChallenge.week_start == week_start, WeeklyChallenge.week_end == week_end
    ).first()

    if not existing:
        challenge = WeeklyChallenge(
            week_start=week_start,
            week_end=week_end,
            description="Try 3 different patties this week",
            condition="try 3 different patties",
            points_reward=150,
            is_active=True,
        )
        db.session.add(challenge)
        db.session.commit()
        print(f"✓ Created weekly challenge for week {week_start} to {week_end}")
    else:
        print("Weekly challenge already exists for this week")


if __name__ == "__main__":
    app = create_app("development")
    with app.app_context():
        print("Initializing gamification system...\n")
        init_badges()
        print()
        init_sample_daily_bonus()
        print()
        init_sample_weekly_challenge()
        print("\n✓ Gamification system initialized successfully!")
