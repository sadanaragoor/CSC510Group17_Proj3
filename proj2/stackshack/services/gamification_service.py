"""
Gamification Service - Handles points, badges, tiers, and rewards.
"""

from models.gamification import (
    PointsTransaction,
    Badge,
    UserBadge,
    DailyBonus,
    WeeklyChallenge,
    UserChallengeProgress,
    Redemption,
    Coupon,
)
from models.user import User
from models.order import Order
from models.menu_item import MenuItem
from datetime import date
from database.db import db
from datetime import datetime, timedelta
from sqlalchemy import func
import secrets
import pytz
import string


class GamificationService:
    """Service for managing gamification features"""

    # Point multipliers by tier
    TIER_MULTIPLIERS = {"Bronze": 1.0, "Silver": 1.2, "Gold": 1.5}

    # Reward costs
    REWARD_COSTS = {
        "free_topping": 100,
        "free_premium_sauce": 125,
        "free_patty_upgrade": 250,
        "three_dollar_off": 300,
        "skip_queue": 300,
        "five_dollar_off": 500,
    }

    @staticmethod
    def get_user_points(user_id):
        """
        Get current total points for a user.
        Always recalculates from transactions to ensure accuracy.
        """
        user = db.session.get(User, user_id)
        if not user:
            return 0

        # Always recalculate from transactions to ensure accuracy
        # This sums all points transactions (positive for earned, negative for redeemed)
        total = (
            db.session.query(func.sum(PointsTransaction.points))
            .filter_by(user_id=user_id)
            .scalar()
        )

        # Handle None result (no transactions yet)
        if total is None:
            total = 0

        # Update cached value
        if user.total_points != total:
            user.total_points = total
            db.session.commit()

        return int(total)

    @staticmethod
    def earn_points(
        event_type,
        user_id,
        points,
        description=None,
        order_id=None,
        apply_multiplier=True,
    ):
        """
        Earn points for a user.

        Args:
            event_type: Type of event (e.g., 'purchase', 'review', 'streak', etc.)
            user_id: User ID
            points: Base points to earn
            description: Optional description
            order_id: Optional order ID
            apply_multiplier: Whether to apply tier multiplier

        Returns:
            tuple: (success, message, points_earned)
        """
        user = db.session.get(User, user_id)
        if not user:
            return False, "User not found", 0

        # Apply tier multiplier if applicable
        if apply_multiplier and event_type == "purchase":
            multiplier = GamificationService.TIER_MULTIPLIERS.get(user.tier, 1.0)
            points = int(points * multiplier)

        # Create transaction
        transaction = PointsTransaction(
            user_id=user_id,
            points=points,
            event_type=event_type,
            description=description,
            order_id=order_id,
        )
        db.session.add(transaction)

        # Update cached total
        user.total_points = (user.total_points or 0) + points
        db.session.commit()

        return True, f"Earned {points} points!", points

    @staticmethod
    def generate_coupon_code():
        """Generate a unique coupon code in format SHACK-XXXXXX"""
        while True:
            # Generate 6 random alphanumeric characters
            random_part = "".join(
                secrets.choice(string.ascii_uppercase + string.digits) for _ in range(6)
            )
            coupon_code = f"SHACK-{random_part}"

            # Check if code already exists
            existing = Coupon.query.filter_by(coupon_code=coupon_code).first()
            if not existing:
                return coupon_code

    @staticmethod
    def redeem_reward(reward_type, user_id, order_id=None):
        """
        Redeem a reward using points and generate a coupon code.

        Args:
            reward_type: Type of reward to redeem
            user_id: User ID
            order_id: Optional order ID if redemption is for a specific order

        Returns:
            tuple: (success, message, coupon_code)
        """
        if reward_type not in GamificationService.REWARD_COSTS:
            return False, "Invalid reward type", None

        cost = GamificationService.REWARD_COSTS[reward_type]
        current_points = GamificationService.get_user_points(user_id)

        if current_points < cost:
            return (
                False,
                f"Insufficient points. Need {cost}, have {current_points}",
                None,
            )

        user = db.session.get(User, user_id)
        if not user:
            return False, "User not found", None

        # Create redemption record
        redemption = Redemption(
            user_id=user_id,
            reward_type=reward_type,
            points_cost=cost,
            description=f"Redeemed {reward_type}",
            order_id=order_id,
        )
        db.session.add(redemption)
        db.session.flush()  # Get redemption ID

        # Generate unique coupon code
        coupon_code = GamificationService.generate_coupon_code()

        # Create coupon (expires in 90 days)
        expiry_date = date.today() + timedelta(days=90)
        coupon = Coupon(
            user_id=user_id,
            redemption_id=redemption.id,
            coupon_code=coupon_code,
            reward_type=reward_type,
            expiry_date=expiry_date,
        )
        db.session.add(coupon)

        # Deduct points
        transaction = PointsTransaction(
            user_id=user_id,
            points=-cost,
            event_type="redemption",
            description=f"Redeemed {reward_type}",
            order_id=order_id,
        )
        db.session.add(transaction)

        # Update cached total
        user.total_points = (user.total_points or 0) - cost
        db.session.commit()

        return (
            True,
            f"Successfully redeemed {reward_type}! Your coupon code is: {coupon_code}",
            coupon_code,
        )

    @staticmethod
    def validate_coupon(coupon_code, user_id, order_id=None):
        """
        Validate a coupon code for a user.

        Args:
            coupon_code: The coupon code to validate
            user_id: User ID
            order_id: Optional order ID to check if coupon is already applied

        Returns:
            tuple: (success, message, coupon_dict)
        """
        coupon = Coupon.query.filter_by(coupon_code=coupon_code.upper()).first()

        if not coupon:
            return False, "Invalid coupon code", None

        if coupon.user_id != user_id:
            return False, "This coupon does not belong to you", None

        if coupon.is_used:
            return False, "This coupon has already been used", None

        if not coupon.is_valid():
            return False, "This coupon has expired", None

        # Check if coupon is already applied to this order
        if order_id and coupon.used_order_id == order_id:
            return False, "This coupon is already applied to this order", None

        return True, "Coupon is valid", coupon.to_dict()

    @staticmethod
    def apply_coupon(coupon_code, user_id, order):
        """
        Apply a coupon to an order and calculate discount.

        Args:
            coupon_code: The coupon code
            user_id: User ID
            order: Order object

        Returns:
            tuple: (success, message, discount_amount, coupon_dict)
        """
        success, message, coupon_dict = GamificationService.validate_coupon(
            coupon_code, user_id, order.id
        )

        if not success:
            return False, message, 0, None

        coupon = Coupon.query.filter_by(coupon_code=coupon_code.upper()).first()

        reward_type = coupon.reward_type

        # Calculate discount based on reward type
        discount_amount = 0.0
        discount_description = ""

        if reward_type == "free_topping":
            # Remove topping costs from order
            order_items = order.items.all()
            for item in order_items:
                if item.menu_item_id:
                    menu_item = db.session.get(MenuItem, item.menu_item_id)
                    if menu_item and menu_item.category.lower() == "topping":
                        discount_amount += float(item.price) * item.quantity
            discount_description = "Free topping applied"

        elif reward_type == "free_premium_sauce":
            # Remove all sauce costs from the order
            order_items = order.items.all()
            sauces_found = []
            for item in order_items:
                if item.menu_item_id:
                    menu_item = db.session.get(MenuItem, item.menu_item_id)
                    if menu_item and menu_item.category.lower() == "sauce":
                        # Remove cost of all sauces (premium or regular)
                        item_discount = float(item.price) * item.quantity
                        discount_amount += item_discount
                        sauces_found.append(f"{item.name} (${item.price:.2f})")

            if sauces_found:
                discount_description = (
                    f"Free premium sauce applied - Removed: {', '.join(sauces_found)}"
                )
            else:
                discount_description = "Free premium sauce applied (no sauces in order)"

        elif reward_type == "three_dollar_off":
            # Subtract $3 from total
            discount_amount = min(3.0, float(order.total_price))
            discount_description = "$3 discount applied"

        elif reward_type == "free_patty_upgrade":
            # Remove patty upgrade cost (difference between premium and regular patty)
            # For simplicity, we'll apply a fixed discount or remove patty cost
            order_items = order.items.all()
            for item in order_items:
                if item.menu_item_id:
                    menu_item = db.session.get(MenuItem, item.menu_item_id)
                    if menu_item and menu_item.category.lower() == "patty":
                        discount_amount += float(item.price) * item.quantity
            discount_description = "Free patty upgrade applied"

        elif reward_type == "skip_queue":
            # Mark order as priority but no price change
            order.status = "Priority"
            discount_amount = 0.0
            discount_description = "Priority queue applied"

        elif reward_type == "five_dollar_off":
            # Subtract $5 from total
            discount_amount = min(5.0, float(order.total_price))
            discount_description = "$5 discount applied"

        # Store the order ID this coupon is being applied to (but don't mark as used yet)
        # This prevents applying the same coupon multiple times to the same order
        coupon.used_order_id = order.id
        db.session.commit()

        return True, discount_description, discount_amount, coupon.to_dict()

    @staticmethod
    def check_and_grant_badges(user_id, order):
        """
        Check if user qualifies for any badges based on order and grant them.

        Args:
            user_id: User ID
            order: Order object

        Returns:
            list: List of newly earned badges
        """
        newly_earned = []
        user = db.session.get(User, user_id)
        if not user:
            return newly_earned

        # Get order items
        order_items = order.items.all()
        [item.name.lower() for item in order_items]
        categories = set()
        for item in order_items:
            if item.menu_item_id:
                menu_item = db.session.get(MenuItem, item.menu_item_id)
                if menu_item:
                    categories.add(menu_item.category.lower())

        # Get user's order history for behavioral badges
        all_orders = Order.query.filter_by(user_id=user_id).all()
        order_count = len(all_orders)

        # Check ingredient explorer badges
        badges_to_check = [
            ("sauce_collector", "Sauce Collector", "Tried all sauces", "ingredient"),
            (
                "veggie_champion",
                "Veggie Champion",
                "Ordered 4+ vegetables",
                "ingredient",
            ),
            (
                "carnivore_king",
                "Carnivore King",
                "Tried all patty options",
                "ingredient",
            ),
            ("brave_soul", "Brave Soul", "Ordered spiciest ingredients", "ingredient"),
            (
                "classic_lover",
                "Classic Lover",
                "Ordered same burger 5+ times",
                "behavioral",
            ),
        ]

        for slug, name, desc, badge_type in badges_to_check:
            badge = Badge.query.filter_by(slug=slug).first()
            if not badge:
                # Create badge if it doesn't exist
                badge = Badge(
                    name=name,
                    slug=slug,
                    description=desc,
                    badge_type=badge_type,
                    icon="🏆",
                )
                db.session.add(badge)
                db.session.flush()

            # Check if user already has this badge
            existing = UserBadge.query.filter_by(
                user_id=user_id, badge_id=badge.id
            ).first()
            if existing:
                continue

            # Check badge conditions
            earned = False
            if slug == "sauce_collector":
                # Check if user has tried all sauces
                all_sauces = MenuItem.query.filter_by(
                    category="sauce", is_available=True
                ).all()
                user_sauces = set()
                for o in all_orders:
                    for item in o.items.all():
                        if item.menu_item_id:
                            mi = db.session.get(MenuItem, item.menu_item_id)
                            if mi and mi.category.lower() == "sauce":
                                user_sauces.add(mi.name.lower())
                if len(user_sauces) >= len(all_sauces) and len(all_sauces) > 0:
                    earned = True

            elif slug == "veggie_champion":
                # Check if ordered 4+ vegetables (toppings)
                veggie_count = sum(
                    1
                    for item in order_items
                    if any(
                        veg in item.name.lower()
                        for veg in ["lettuce", "tomato", "onion", "pickles", "capsicum"]
                    )
                )
                if veggie_count >= 4:
                    earned = True

            elif slug == "carnivore_king":
                # Check if tried all patty types
                all_patties = MenuItem.query.filter_by(
                    category="patty", is_available=True
                ).all()
                user_patties = set()
                for o in all_orders:
                    for item in o.items.all():
                        if item.menu_item_id:
                            mi = db.session.get(MenuItem, item.menu_item_id)
                            if mi and mi.category.lower() == "patty":
                                user_patties.add(mi.name.lower())
                if len(user_patties) >= len(all_patties) and len(all_patties) > 0:
                    earned = True

            elif slug == "brave_soul":
                # Check for spiciest ingredients (heuristic: look for spicy keywords)
                spicy_keywords = ["spicy", "hot", "jalapeno", "pepper", "chili"]
                has_spicy = any(
                    any(keyword in item.name.lower() for keyword in spicy_keywords)
                    for item in order_items
                )
                if has_spicy:
                    earned = True

            elif slug == "classic_lover":
                # Check if same burger ordered 5+ times
                burger_name = (
                    order.items.first().burger_name if order.items.first() else None
                )
                if burger_name:
                    same_burger_count = sum(
                        1
                        for o in all_orders
                        if o.items.first()
                        and o.items.first().burger_name == burger_name
                    )
                    if same_burger_count >= 5:
                        earned = True

            if earned:
                user_badge = UserBadge(
                    user_id=user_id, badge_id=badge.id, order_id=order.id
                )
                db.session.add(user_badge)
                newly_earned.append(badge)

                # Award points for earning badge
                badge_points_map = {
                    "sauce_collector": 50,
                    "veggie_champion": 75,
                    "carnivore_king": 100,
                    "brave_soul": 50,
                    "classic_lover": 60,
                }
                points_reward = badge_points_map.get(slug, 0)
                if points_reward > 0:
                    GamificationService.earn_points(
                        "badge_earned",
                        user_id,
                        points_reward,
                        f"Badge earned: {name}",
                        order.id,
                        apply_multiplier=False,
                    )

        # Check behavioral badges
        behavioral_badges = [
            (
                "lunch_rush_warrior",
                "Lunch Rush Warrior",
                "10 orders between 12-1 PM",
                12,
                13,
            ),
            ("early_bird", "Early Bird", "5 orders before 11 AM", 0, 11),
            ("late_night_snacker", "Late Night Snacker", "5 orders after 8 PM", 20, 24),
            ("stackshack_regular", "StackShack Regular", "20 total orders", None, None),
            ("century_club", "Century Club", "100 total orders", None, None),
            (
                "mystery_box_master",
                "Mystery Box Master",
                "5 surprise box orders",
                None,
                None,
            ),
        ]

        for slug, name, desc, hour_start, hour_end in behavioral_badges:
            badge = Badge.query.filter_by(slug=slug).first()
            if not badge:
                badge = Badge(
                    name=name,
                    slug=slug,
                    description=desc,
                    badge_type="behavioral",
                    icon="⭐",
                )
                db.session.add(badge)
                db.session.flush()

            existing = UserBadge.query.filter_by(
                user_id=user_id, badge_id=badge.id
            ).first()
            if existing:
                continue

            earned = False
            # Convert UTC to local time for time-based badge checks
            # Using US/Eastern timezone - adjust to your server's timezone
            local_tz = pytz.timezone("US/Eastern")

            if slug == "lunch_rush_warrior":
                lunch_orders = []
                for o in all_orders:
                    if o.ordered_at:
                        # Convert UTC to local time
                        if o.ordered_at.tzinfo is None:
                            # Assume UTC if timezone-naive
                            utc_time = pytz.utc.localize(o.ordered_at)
                        else:
                            utc_time = o.ordered_at.astimezone(pytz.utc)
                        local_time = utc_time.astimezone(local_tz)
                        if 12 <= local_time.hour < 13:
                            lunch_orders.append(o)
                if len(lunch_orders) >= 10:
                    earned = True
            elif slug == "early_bird":
                early_orders = []
                for o in all_orders:
                    if o.ordered_at:
                        # Convert UTC to local time
                        if o.ordered_at.tzinfo is None:
                            utc_time = pytz.utc.localize(o.ordered_at)
                        else:
                            utc_time = o.ordered_at.astimezone(pytz.utc)
                        local_time = utc_time.astimezone(local_tz)
                        if local_time.hour < 11:
                            early_orders.append(o)
                if len(early_orders) >= 5:
                    earned = True
            elif slug == "late_night_snacker":
                late_orders = []
                for o in all_orders:
                    if o.ordered_at:
                        # Convert UTC to local time
                        if o.ordered_at.tzinfo is None:
                            utc_time = pytz.utc.localize(o.ordered_at)
                        else:
                            utc_time = o.ordered_at.astimezone(pytz.utc)
                        local_time = utc_time.astimezone(local_tz)
                        if local_time.hour >= 20:  # 8 PM local time
                            late_orders.append(o)
                if len(late_orders) >= 5:
                    earned = True
            elif slug == "stackshack_regular":
                if order_count >= 20:
                    earned = True
            elif slug == "century_club":
                if order_count >= 100:
                    earned = True
            elif slug == "mystery_box_master":
                # Check for surprise box orders (orders with "surprise" in burger name)
                surprise_orders = [
                    o
                    for o in all_orders
                    if any(
                        item.burger_name and "surprise" in item.burger_name.lower()
                        for item in o.items.all()
                    )
                ]
                if len(surprise_orders) >= 5:
                    earned = True

            if earned:
                user_badge = UserBadge(
                    user_id=user_id, badge_id=badge.id, order_id=order.id
                )
                db.session.add(user_badge)
                newly_earned.append(badge)

                # Award points for earning badge
                badge_points_map = {
                    "lunch_rush_warrior": 100,
                    "early_bird": 75,
                    "late_night_snacker": 75,
                    "stackshack_regular": 150,
                    "century_club": 500,
                    "mystery_box_master": 80,
                }
                points_reward = badge_points_map.get(slug, 0)
                if points_reward > 0:
                    GamificationService.earn_points(
                        "badge_earned",
                        user_id,
                        points_reward,
                        f"Badge earned: {name}",
                        order.id,
                        apply_multiplier=False,
                    )

        db.session.commit()
        return newly_earned

    @staticmethod
    def update_user_tier(user_id):
        """
        Update user tier based on total points.

        Returns:
            tuple: (success, message, new_tier)
        """
        user = db.session.get(User, user_id)
        if not user:
            return False, "User not found", None

        total_points = GamificationService.get_user_points(user_id)
        old_tier = user.tier

        if total_points >= 1501:
            new_tier = "Gold"
        elif total_points >= 501:
            new_tier = "Silver"
        else:
            new_tier = "Bronze"

        if new_tier != old_tier:
            user.tier = new_tier
            db.session.commit()
            return True, f"Upgraded to {new_tier} tier!", new_tier

        return True, f"Current tier: {new_tier}", new_tier

    @staticmethod
    def process_order_points(order):
        """
        Process points for an order with all bonuses.

        Returns:
            tuple: (total_points_earned, breakdown)
        """
        user_id = order.user_id
        # Use original total before coupon discount for points calculation
        order_total = float(
            order.original_total if order.original_total else order.total_price
        )

        breakdown = {}

        # Base points: 10 points per $1 (before tier multiplier)
        base_points = int(order_total * 10)

        # Apply tier multiplier to base points
        user = db.session.get(User, user_id)
        multiplier = GamificationService.TIER_MULTIPLIERS.get(
            user.tier or "Bronze", 1.0
        )
        final_base_points = int(base_points * multiplier)
        breakdown["base"] = final_base_points

        # Track total points earned (only base purchase points)
        total_points_earned = final_base_points

        # Record base purchase points
        GamificationService.earn_points(
            "purchase",
            user_id,
            final_base_points,
            f"Purchase: ${order_total:.2f}",
            order.id,
            apply_multiplier=False,
        )

        db.session.commit()

        return total_points_earned, breakdown

    @staticmethod
    def check_daily_bonus(user_id, order):
        """Check and award ALL daily bonuses for today if conditions are met (max 2 per day)."""
        from services.challenge_service import ChallengeService

        today = date.today()

        # Generate daily challenges if they don't exist
        ChallengeService.generate_daily_challenges(today, max_challenges=2)

        # Get all daily bonuses for today
        daily_bonuses = DailyBonus.query.filter_by(
            bonus_date=today, is_active=True
        ).all()

        if not daily_bonuses:
            return False, None

        completed_bonuses = []
        order_items = order.items.all()

        # Get order time in local timezone for time-based challenges
        local_tz = pytz.timezone("US/Eastern")
        if order.ordered_at:
            if order.ordered_at.tzinfo is None:
                order_time = pytz.utc.localize(order.ordered_at).astimezone(local_tz)
            else:
                order_time = order.ordered_at.astimezone(local_tz)
            order_hour = order_time.hour
            order_minute = order_time.minute
        else:
            order_time = None
            order_hour = None
            order_minute = None

        for daily_bonus in daily_bonuses:
            # Check if user already completed this bonus today
            progress = UserChallengeProgress.query.filter_by(
                user_id=user_id, daily_bonus_id=daily_bonus.id, completed=True
            ).first()

            if progress:
                continue  # Skip already completed bonuses

            # Check condition
            condition_met = GamificationService._check_daily_condition(
                daily_bonus.condition,
                order_items,
                order,
                order_time,
                order_hour,
                order_minute,
            )

            if condition_met:
                progress = UserChallengeProgress.query.filter_by(
                    user_id=user_id, daily_bonus_id=daily_bonus.id
                ).first()

                if not progress:
                    progress = UserChallengeProgress(
                        user_id=user_id,
                        daily_bonus_id=daily_bonus.id,
                        progress=1,
                        target=1,
                        completed=True,
                        completed_at=datetime.utcnow(),
                    )
                    db.session.add(progress)
                else:
                    progress.completed = True
                    progress.completed_at = datetime.utcnow()

                # Award points
                GamificationService.earn_points(
                    "daily_bonus",
                    user_id,
                    daily_bonus.points_reward,
                    daily_bonus.description,
                    order.id,
                    apply_multiplier=False,
                )
                completed_bonuses.append(daily_bonus)

        if completed_bonuses:
            db.session.commit()
            return True, (
                completed_bonuses[0]
                if len(completed_bonuses) == 1
                else completed_bonuses
            )

        return False, None

    @staticmethod
    def _check_daily_condition(
        condition, order_items, order, order_time, order_hour, order_minute
    ):
        """Check if a daily challenge condition is met"""
        condition.lower()
        order_item_names = [item.name.lower() for item in order_items]

        # Get menu items for category checking
        menu_items_by_category = {}
        for item in order_items:
            if item.menu_item_id:
                mi = db.session.get(MenuItem, item.menu_item_id)
                if mi:
                    cat = mi.category.lower()
                    if cat not in menu_items_by_category:
                        menu_items_by_category[cat] = []
                    menu_items_by_category[cat].append(mi.name.lower())

        # Bun conditions
        if condition == "keto_bun":
            return any("keto" in name for name in order_item_names)
        elif condition == "sesame_bun":
            return any(
                "sesame" in name or "black sesame" in name for name in order_item_names
            )
        elif condition == "veggie_bun":
            return any(
                "beetroot" in name or "carrot" in name for name in order_item_names
            )
        elif condition == "wheat_bun":
            return any(
                "wheat" in name or "honeywheat" in name for name in order_item_names
            )
        elif condition == "plain_bun":
            return any("plain" in name and "bun" in name for name in order_item_names)

        # Cheese conditions
        elif condition == "any_cheese":
            return "cheese" in menu_items_by_category.get("cheese", [])
        elif condition == "cheddar_cheese":
            return any("cheddar" in name for name in order_item_names)
        elif condition == "swiss_cheese":
            return any("swiss" in name for name in order_item_names)
        elif condition == "two_cheeses":
            cheeses = menu_items_by_category.get("cheese", [])
            return len(set(cheeses)) >= 2
        elif condition == "parmesan_cheese":
            return any("parmesan" in name for name in order_item_names)

        # Patty conditions
        elif condition == "beef_patty":
            patties = menu_items_by_category.get("patty", [])
            return any("beef" in name or "low-calorie beef" in name for name in patties)
        elif condition == "chicken_patty":
            return any("chicken" in name for name in order_item_names)
        elif condition == "veg_patty":
            patties = menu_items_by_category.get("patty", [])
            return any("veg" in name or "mixed veg" in name for name in patties)
        elif condition == "pork_patty":
            return any("pork" in name for name in order_item_names)
        elif condition == "healthy_patty":
            patties = menu_items_by_category.get("patty", [])
            return any(
                "low-calorie beef" in name or "mixed veg" in name for name in patties
            )

        # Sauce conditions
        elif condition == "green_sauce":
            return any("green" in name and "sauce" in name for name in order_item_names)
        elif condition == "mayo":
            return any("mayo" in name for name in order_item_names)
        elif condition == "mustard":
            return any("mustard" in name for name in order_item_names)
        elif condition == "tomato_sauce":
            return any(
                "tomato" in name and "sauce" in name for name in order_item_names
            )
        elif condition == "two_sauces":
            sauces = menu_items_by_category.get("sauce", [])
            return len(set(sauces)) >= 2
        elif condition == "all_sauces":
            sauces = menu_items_by_category.get("sauce", [])
            return len(set(sauces)) >= 4  # Assuming 4 sauces total

        # Topping conditions
        elif condition == "pickles":
            return any("pickle" in name for name in order_item_names)
        elif condition == "tomato":
            return any(
                "tomato" in name and "sauce" not in name for name in order_item_names
            )
        elif condition == "lettuce":
            return any("lettuce" in name for name in order_item_names)
        elif condition == "onion":
            return any("onion" in name for name in order_item_names)
        elif condition == "capsicum":
            return any("capsicum" in name for name in order_item_names)
        elif condition == "three_toppings":
            toppings = menu_items_by_category.get("topping", [])
            return len(set(toppings)) >= 3
        elif condition == "all_toppings":
            toppings = menu_items_by_category.get("topping", [])
            return len(set(toppings)) >= 5  # Assuming 5 toppings total

        # Behavioral/Time conditions
        elif condition == "before_11am" and order_hour is not None:
            return order_hour < 11
        elif condition == "between_2_4pm" and order_hour is not None:
            return 14 <= order_hour < 16
        elif condition == "after_8pm" and order_hour is not None:
            return order_hour >= 20
        elif condition == "lunch_rush" and order_hour is not None:
            return order_hour == 12
        elif (
            condition == "exact_222"
            and order_hour is not None
            and order_minute is not None
        ):
            return order_hour == 14 and order_minute == 22
        elif condition == "surprise_burger":
            # Check if order was from surprise box (would need to track this)
            return False  # Placeholder
        elif condition == "all_healthy":
            # Check if all items are healthy
            for item in order_items:
                if item.menu_item_id:
                    mi = db.session.get(MenuItem, item.menu_item_id)
                    if mi and not mi.is_healthy_choice:
                        return False
            return True

        return False

    @staticmethod
    def check_weekly_challenge(user_id, order):
        """Check and update ALL weekly challenge progress (max 3 per week)."""
        from services.challenge_service import ChallengeService

        today = date.today()
        days_since_monday = today.weekday()
        week_start = today - timedelta(days=days_since_monday)
        week_end = week_start + timedelta(days=6)

        # Generate weekly challenges if they don't exist
        ChallengeService.generate_weekly_challenges(week_start, max_challenges=3)

        # Find all current week's challenges
        challenges = WeeklyChallenge.query.filter(
            WeeklyChallenge.week_start <= today,
            WeeklyChallenge.week_end >= today,
            WeeklyChallenge.is_active,
        ).all()

        if not challenges:
            return False, None

        completed_challenges = []

        for challenge in challenges:
            # Get or create progress
            progress = UserChallengeProgress.query.filter_by(
                user_id=user_id, challenge_id=challenge.id
            ).first()

            # Get target from challenge definition
            challenge_def = ChallengeService.WEEKLY_CHALLENGES.get(
                next(
                    (
                        k
                        for k, v in ChallengeService.WEEKLY_CHALLENGES.items()
                        if v["condition"] == challenge.condition
                    ),
                    None,
                )
            )
            target = challenge_def["target"] if challenge_def else 3

            if not progress:
                progress = UserChallengeProgress(
                    user_id=user_id,
                    challenge_id=challenge.id,
                    progress=0,
                    target=target,
                )
                db.session.add(progress)

            # Skip if already completed
            if progress.completed:
                continue

            # Update progress based on condition
            progress_updated = GamificationService._update_weekly_progress(
                challenge, progress, order, user_id, week_start, week_end
            )

            if (
                progress_updated
                and progress.progress >= progress.target
                and not progress.completed
            ):
                progress.completed = True
                progress.completed_at = datetime.utcnow()
                # Award points
                GamificationService.earn_points(
                    "weekly_challenge",
                    user_id,
                    challenge.points_reward,
                    challenge.description,
                    order.id,
                    apply_multiplier=False,
                )
                completed_challenges.append(challenge)

        if completed_challenges:
            db.session.commit()
            return True, (
                completed_challenges[0]
                if len(completed_challenges) == 1
                else completed_challenges
            )

        db.session.commit()
        return True, None

    @staticmethod
    def _update_weekly_progress(
        challenge, progress, order, user_id, week_start, week_end
    ):
        """Update weekly challenge progress based on condition"""
        condition = challenge.condition
        order_items = order.items.all()

        # Get menu items by category
        menu_items_by_category = {}
        for item in order_items:
            if item.menu_item_id:
                mi = db.session.get(MenuItem, item.menu_item_id)
                if mi:
                    cat = mi.category.lower()
                    if cat not in menu_items_by_category:
                        menu_items_by_category[cat] = set()
                    menu_items_by_category[cat].add(mi.name.lower())

        # Simple progress updates - most challenges increment by 1 per qualifying order
        # More complex challenges would need additional logic
        if (
            condition.startswith("three_")
            or condition.startswith("four_")
            or condition.startswith("five_")
        ):
            # Most challenges: increment if condition met in this order
            progress.progress += 1
            return True
        elif "all_" in condition:
            # "All" challenges: check if all items of that type are present
            if "buns" in condition:
                buns = menu_items_by_category.get("bun", set())
                if len(buns) >= 3:
                    progress.progress += 1
                    return True
            # Similar for other "all" conditions
            progress.progress += 1
            return True
        else:
            # Default: increment progress
            progress.progress += 1
            return True

    @staticmethod
    def get_monthly_leaderboard(month=None, year=None, limit=5):
        """Get monthly leaderboard of top point earners."""
        if not month or not year:
            now = datetime.utcnow()
            month = now.month
            year = now.year

        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, month + 1, 1)

        # Get top point earners for the month
        top_earners = (
            db.session.query(
                User.id,
                User.username,
                func.sum(PointsTransaction.points).label("total_points"),
            )
            .join(PointsTransaction, User.id == PointsTransaction.user_id)
            .filter(
                PointsTransaction.created_at >= start_date,
                PointsTransaction.created_at < end_date,
                PointsTransaction.points > 0,
            )
            .group_by(User.id, User.username)
            .order_by(func.sum(PointsTransaction.points).desc())
            .limit(limit)
            .all()
        )

        return [
            {
                "user_id": user_id,
                "username": username,
                "points": int(total_points) if total_points else 0,
                "rank": idx + 1,
            }
            for idx, (user_id, username, total_points) in enumerate(top_earners)
        ]
