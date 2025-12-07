"""
Test cases for challenge service.
"""

from datetime import date, timedelta
from models.gamification import DailyBonus, WeeklyChallenge
from services.challenge_service import ChallengeService


class TestChallengeService:
    """Test cases for ChallengeService."""

    def test_generate_daily_challenges_idempotent(self, app):
        """Test that generating challenges multiple times doesn't create duplicates."""
        with app.app_context():
            today = date.today()
            ChallengeService.generate_daily_challenges(today, max_challenges=2)
            len(DailyBonus.query.filter_by(bonus_date=today, is_active=True).all())

            ChallengeService.generate_daily_challenges(today, max_challenges=2)
            count2 = len(
                DailyBonus.query.filter_by(bonus_date=today, is_active=True).all()
            )

            # Should not create more than max_challenges
            assert count2 <= 2

    def test_generate_weekly_challenges_idempotent(self, app):
        """Test that generating weekly challenges multiple times doesn't create duplicates."""
        with app.app_context():
            days_since_monday = date.today().weekday()
            week_start = date.today() - timedelta(days=days_since_monday)

            ChallengeService.generate_weekly_challenges(week_start, max_challenges=3)
            len(
                WeeklyChallenge.query.filter_by(
                    week_start=week_start, is_active=True
                ).all()
            )

            ChallengeService.generate_weekly_challenges(week_start, max_challenges=3)
            count2 = len(
                WeeklyChallenge.query.filter_by(
                    week_start=week_start, is_active=True
                ).all()
            )

            # Should not create more than max_challenges
            assert count2 <= 3
