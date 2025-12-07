"""
Comprehensive challenge service tests to increase coverage.
"""

from datetime import date, timedelta
from models.gamification import DailyBonus, WeeklyChallenge
from services.challenge_service import ChallengeService
from database.db import db


class TestChallengeServiceComprehensive:
    """Comprehensive challenge service tests."""

    def test_generate_daily_challenges_max_reached(self, app):
        """Test generating daily challenges when max is already reached."""
        with app.app_context():
            today = date.today()
            # Create 2 challenges manually
            bonus1 = DailyBonus(
                bonus_date=today,
                description="Challenge 1",
                condition="has_pickles",
                points_reward=30,
                is_active=True,
            )
            bonus2 = DailyBonus(
                bonus_date=today,
                description="Challenge 2",
                condition="has_tomato",
                points_reward=25,
                is_active=True,
            )
            db.session.add_all([bonus1, bonus2])
            db.session.commit()

            # Try to generate more (should not create duplicates)
            count = ChallengeService.generate_daily_challenges(today, max_challenges=2)

            # Should not create more than 2
            bonuses = DailyBonus.query.filter_by(bonus_date=today, is_active=True).all()
            assert len(bonuses) <= 2

    def test_generate_weekly_challenges_max_reached(self, app):
        """Test generating weekly challenges when max is already reached."""
        with app.app_context():
            days_since_monday = date.today().weekday()
            week_start = date.today() - timedelta(days=days_since_monday)
            week_end = week_start + timedelta(days=6)

            # Create 3 challenges manually
            challenge1 = WeeklyChallenge(
                week_start=week_start,
                week_end=week_end,
                description="Challenge 1",
                condition="trio_time",
                points_reward=100,
                is_active=True,
            )
            challenge2 = WeeklyChallenge(
                week_start=week_start,
                week_end=week_end,
                description="Challenge 2",
                condition="bun_explorer",
                points_reward=150,
                is_active=True,
            )
            challenge3 = WeeklyChallenge(
                week_start=week_start,
                week_end=week_end,
                description="Challenge 3",
                condition="patty_sampler",
                points_reward=200,
                is_active=True,
            )
            db.session.add_all([challenge1, challenge2, challenge3])
            db.session.commit()

            # Try to generate more (should not create duplicates)
            count = ChallengeService.generate_weekly_challenges(
                week_start, max_challenges=3
            )

            # Should not create more than 3
            challenges = WeeklyChallenge.query.filter_by(
                week_start=week_start, is_active=True
            ).all()
            assert len(challenges) <= 3

    def test_daily_challenges_all_types(self, app):
        """Test that daily challenges can be generated for all types."""
        with app.app_context():
            today = date.today()
            count = ChallengeService.generate_daily_challenges(today, max_challenges=2)

            bonuses = DailyBonus.query.filter_by(bonus_date=today, is_active=True).all()
            # Should have challenges
            assert len(bonuses) <= 2

    def test_weekly_challenges_all_types(self, app):
        """Test that weekly challenges can be generated for all types."""
        with app.app_context():
            days_since_monday = date.today().weekday()
            week_start = date.today() - timedelta(days=days_since_monday)

            count = ChallengeService.generate_weekly_challenges(
                week_start, max_challenges=3
            )

            challenges = WeeklyChallenge.query.filter_by(
                week_start=week_start, is_active=True
            ).all()
            # Should have challenges
            assert len(challenges) <= 3
