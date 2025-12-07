"""
Initialize default shifts for the restaurant.
Run this script to create the default shift types.
"""

import sys
import os

# Add the parent directory to the path so we can import from stackshack
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app
from services.shift_service import ShiftService


def init_default_shifts():
    app = create_app("development")
    with app.app_context():
        print("=" * 80)
        print("INITIALIZING DEFAULT SHIFTS")
        print("=" * 80)

        created = ShiftService.initialize_default_shifts()

        if created > 0:
            print(f"\n✅ Created {created} default shift(s)")
        else:
            print("\n✅ Default shifts already exist")

        print("\nDefault shifts:")
        shifts = ShiftService.get_all_shifts()
        for shift in shifts:
            print(
                f"  - {shift.name}: {shift.start_time.strftime('%I:%M %p')} - {shift.end_time.strftime('%I:%M %p')}"
            )

        print("\n" + "=" * 80)
        print("SHIFT INITIALIZATION COMPLETE")
        print("=" * 80)


if __name__ == "__main__":
    init_default_shifts()
