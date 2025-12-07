"""
Gamification routes for points, badges, tiers, and rewards.
"""

from flask import Blueprint, jsonify, request, render_template, session
from flask_login import login_required, current_user
from datetime import date, datetime, timedelta
from services.gamification_service import GamificationService
from models.gamification import (
    Badge,
    UserBadge,
    DailyBonus,
    WeeklyChallenge,
    Redemption,
    UserChallengeProgress,
)
from models.order import Order
from database.db import db

gamification_bp = Blueprint("gamification", __name__)


@gamification_bp.route("/rewards", methods=["GET"])
@login_required
def rewards_page():
    """Display the rewards and gamification page"""
    # Recalculate points to ensure accuracy
    # This ensures the displayed points match the actual sum of all transactions
    points = GamificationService.get_user_points(current_user.id)
    tier_info = GamificationService.update_user_tier(current_user.id)

    # Get user badges
    user_badges = UserBadge.query.filter_by(user_id=current_user.id).all()

    # Get daily bonuses (up to 2 per day)
    today = date.today()
    from services.challenge_service import ChallengeService

    ChallengeService.generate_daily_challenges(today, max_challenges=2)
    daily_bonuses = DailyBonus.query.filter_by(bonus_date=today, is_active=True).all()
    daily_bonuses_data = []
    for db in daily_bonuses:
        progress = UserChallengeProgress.query.filter_by(
            user_id=current_user.id, daily_bonus_id=db.id, completed=True
        ).first()
        daily_bonuses_data.append(
            {"bonus": db.to_dict(), "completed": progress is not None}
        )

    # Get weekly challenges (up to 3 per week)
    days_since_monday = today.weekday()
    week_start = today - timedelta(days=days_since_monday)
    ChallengeService.generate_weekly_challenges(week_start, max_challenges=3)
    challenges = WeeklyChallenge.query.filter(
        WeeklyChallenge.week_start <= today,
        WeeklyChallenge.week_end >= today,
        WeeklyChallenge.is_active == True,
    ).all()
    challenges_data = []
    for challenge in challenges:
        progress = UserChallengeProgress.query.filter_by(
            user_id=current_user.id, challenge_id=challenge.id
        ).first()
        challenge_progress = None
        if progress:
            challenge_progress = {
                "progress": progress.progress,
                "target": progress.target,
                "completed": progress.completed,
            }
        challenges_data.append(
            {"challenge": challenge.to_dict(), "progress": challenge_progress}
        )

    # Get available rewards
    rewards = GamificationService.REWARD_COSTS

    return render_template(
        "gamification/rewards.html",
        points=points,
        tier=current_user.tier or "Bronze",
        tier_multiplier=GamificationService.TIER_MULTIPLIERS.get(
            current_user.tier or "Bronze", 1.0
        ),
        badges=user_badges,
        daily_bonuses=daily_bonuses_data,
        weekly_challenges=challenges_data,
        rewards=rewards,
    )


@gamification_bp.route("/api/points", methods=["GET"])
@login_required
def get_user_points():
    """Get current user's points"""
    # Always recalculate to ensure accuracy
    points = GamificationService.get_user_points(current_user.id)
    tier_info = GamificationService.update_user_tier(current_user.id)

    return jsonify(
        {
            "points": points,
            "tier": current_user.tier,
            "tier_multiplier": GamificationService.TIER_MULTIPLIERS.get(
                current_user.tier, 1.0
            ),
        }
    )


@gamification_bp.route("/api/points/verify", methods=["GET"])
@login_required
def verify_points():
    """Verify points calculation by showing breakdown"""
    from models.gamification import PointsTransaction

    # Get all transactions
    transactions = PointsTransaction.query.filter_by(user_id=current_user.id).all()

    # Calculate breakdown by event type
    breakdown = {}
    total = 0
    for trans in transactions:
        event_type = trans.event_type
        if event_type not in breakdown:
            breakdown[event_type] = 0
        breakdown[event_type] += trans.points
        total += trans.points

    # Get current calculated total
    calculated_total = GamificationService.get_user_points(current_user.id)

    return jsonify(
        {
            "calculated_total": calculated_total,
            "manual_sum": int(total),
            "breakdown": breakdown,
            "match": calculated_total == int(total),
            "transaction_count": len(transactions),
        }
    )


@gamification_bp.route("/api/points/earn", methods=["POST"])
@login_required
def earn_points():
    """Earn points for an event"""
    data = request.get_json()
    event_type = data.get("event_type")
    points = data.get("points", 0)
    description = data.get("description")
    order_id = data.get("order_id")

    if not event_type:
        return jsonify({"error": "event_type is required"}), 400

    success, message, points_earned = GamificationService.earn_points(
        event_type, current_user.id, points, description, order_id
    )

    if success:
        return jsonify(
            {
                "success": True,
                "message": message,
                "points_earned": points_earned,
                "total_points": GamificationService.get_user_points(current_user.id),
            }
        )
    else:
        return jsonify({"error": message}), 400


@gamification_bp.route("/api/points/redeem", methods=["POST"])
@login_required
def redeem_reward():
    """Redeem a reward using points and generate coupon"""
    data = request.get_json()
    reward_type = data.get("reward_type")
    order_id = data.get("order_id")

    if not reward_type:
        return jsonify({"error": "reward_type is required"}), 400

    success, message, coupon_code = GamificationService.redeem_reward(
        reward_type, current_user.id, order_id
    )

    if success:
        return jsonify(
            {
                "success": True,
                "message": message,
                "coupon_code": coupon_code,
                "total_points": GamificationService.get_user_points(current_user.id),
            }
        )
    else:
        return jsonify({"error": message}), 400


@gamification_bp.route("/api/badges", methods=["GET"])
@login_required
def get_user_badges():
    """Get all badges earned by current user"""
    user_badges = UserBadge.query.filter_by(user_id=current_user.id).all()

    return jsonify({"badges": [ub.to_dict() for ub in user_badges]})


@gamification_bp.route("/api/badges/all", methods=["GET"])
@login_required
def get_all_badges():
    """Get all possible badges in the system"""
    all_badges = Badge.query.all()
    user_badge_ids = {
        ub.badge_id for ub in UserBadge.query.filter_by(user_id=current_user.id).all()
    }

    badges_list = []
    for badge in all_badges:
        badge_dict = badge.to_dict()
        badge_dict["earned"] = badge.id in user_badge_ids
        if badge_dict["earned"]:
            user_badge = UserBadge.query.filter_by(
                user_id=current_user.id, badge_id=badge.id
            ).first()
            badge_dict["earned_at"] = (
                user_badge.earned_at.isoformat()
                if user_badge and user_badge.earned_at
                else None
            )
        badges_list.append(badge_dict)

    return jsonify({"badges": badges_list})


@gamification_bp.route("/api/badges/check", methods=["POST"])
@login_required
def check_badges():
    """Check and grant badges for an order"""
    data = request.get_json()
    order_id = data.get("order_id")

    if not order_id:
        return jsonify({"error": "order_id is required"}), 400

    order = db.session.get(Order, order_id)
    if not order or order.user_id != current_user.id:
        return jsonify({"error": "Order not found"}), 404

    newly_earned = GamificationService.check_and_grant_badges(current_user.id, order)

    return jsonify(
        {
            "newly_earned": [badge.to_dict() for badge in newly_earned],
            "count": len(newly_earned),
        }
    )


@gamification_bp.route("/api/tier", methods=["GET"])
@login_required
def get_user_tier():
    """Get current user's tier and update if needed"""
    success, message, tier = GamificationService.update_user_tier(current_user.id)

    return jsonify(
        {
            "tier": tier,
            "multiplier": GamificationService.TIER_MULTIPLIERS.get(tier, 1.0),
            "points": GamificationService.get_user_points(current_user.id),
            "message": message,
        }
    )


@gamification_bp.route("/api/rewards", methods=["GET"])
@login_required
def get_available_rewards():
    """Get list of available rewards and their costs"""
    return jsonify({"rewards": GamificationService.REWARD_COSTS})


@gamification_bp.route("/api/daily-bonus", methods=["GET"])
@login_required
def get_daily_bonus():
    """Get today's daily bonuses (up to 2)"""
    from services.challenge_service import ChallengeService

    today = date.today()
    ChallengeService.generate_daily_challenges(today, max_challenges=2)
    daily_bonuses = DailyBonus.query.filter_by(bonus_date=today, is_active=True).all()

    if not daily_bonuses:
        return jsonify({"bonuses": []})

    # Check if user completed each
    from models.gamification import UserChallengeProgress

    bonuses_data = []
    for db in daily_bonuses:
        progress = UserChallengeProgress.query.filter_by(
            user_id=current_user.id, daily_bonus_id=db.id, completed=True
        ).first()
        bonuses_data.append({"bonus": db.to_dict(), "completed": progress is not None})

    return jsonify({"bonuses": bonuses_data})


@gamification_bp.route("/api/weekly-challenge", methods=["GET"])
@login_required
def get_weekly_challenge():
    """Get current weekly challenges (up to 3)"""
    from services.challenge_service import ChallengeService

    today = date.today()
    days_since_monday = today.weekday()
    week_start = today - timedelta(days=days_since_monday)
    ChallengeService.generate_weekly_challenges(week_start, max_challenges=3)
    challenges = WeeklyChallenge.query.filter(
        WeeklyChallenge.week_start <= today,
        WeeklyChallenge.week_end >= today,
        WeeklyChallenge.is_active == True,
    ).all()

    if not challenges:
        return jsonify({"challenges": []})

    # Get user progress for each
    from models.gamification import UserChallengeProgress

    challenges_data = []
    for challenge in challenges:
        progress = UserChallengeProgress.query.filter_by(
            user_id=current_user.id, challenge_id=challenge.id
        ).first()

        challenge_dict = challenge.to_dict()
        if progress:
            challenge_dict["progress"] = progress.progress
            challenge_dict["target"] = progress.target
            challenge_dict["completed"] = progress.completed
        else:
            challenge_dict["progress"] = 0
            challenge_dict["target"] = 3  # Default
            challenge_dict["completed"] = False

        challenges_data.append(challenge_dict)

    return jsonify({"challenges": challenges_data})


@gamification_bp.route("/api/leaderboard", methods=["GET"])
@login_required
def get_leaderboard():
    """Get monthly leaderboard"""
    month = request.args.get("month", type=int)
    year = request.args.get("year", type=int)
    limit = request.args.get("limit", 5, type=int)

    leaderboard = GamificationService.get_monthly_leaderboard(month, year, limit)

    return jsonify(
        {
            "leaderboard": leaderboard,
            "month": month or datetime.utcnow().month,
            "year": year or datetime.utcnow().year,
        }
    )


@gamification_bp.route("/api/review", methods=["POST"])
@login_required
def submit_review():
    """Submit a burger review (points removed)"""
    data = request.get_json()
    order_id = data.get("order_id")
    rating = data.get("rating")
    comment = data.get("comment")

    if not order_id or not rating:
        return jsonify({"error": "order_id and rating are required"}), 400

    # Review submission (no points awarded)
    return jsonify(
        {
            "success": True,
            "message": "Review submitted successfully",
            "points_earned": 0,
        }
    )


@gamification_bp.route("/api/qr-scan", methods=["POST"])
@login_required
def scan_qr_pickup():
    """Scan QR code at pickup (points removed)"""
    data = request.get_json()
    order_id = data.get("order_id")

    if not order_id:
        return jsonify({"error": "order_id is required"}), 400

    order = db.session.get(Order, order_id)
    if not order or order.user_id != current_user.id:
        return jsonify({"error": "Order not found"}), 404

    # QR scan (no points awarded)
    return jsonify(
        {"success": True, "message": "QR code scanned successfully", "points_earned": 0}
    )


@gamification_bp.route("/api/coupon/validate", methods=["POST"])
@login_required
def validate_coupon():
    """Validate a coupon code"""
    data = request.get_json()
    coupon_code = data.get("coupon_code")

    if not coupon_code:
        return jsonify({"error": "coupon_code is required"}), 400

    order_id = data.get("order_id")
    success, message, coupon_dict = GamificationService.validate_coupon(
        coupon_code, current_user.id, order_id
    )

    if success:
        return jsonify({"success": True, "message": message, "coupon": coupon_dict})
    else:
        return jsonify({"error": message}), 400


@gamification_bp.route("/api/coupon/apply", methods=["POST"])
@login_required
def apply_coupon():
    """Apply a coupon to an order"""
    data = request.get_json()
    coupon_code = data.get("coupon_code")
    order_id = data.get("order_id")

    if not coupon_code or not order_id:
        return jsonify({"error": "coupon_code and order_id are required"}), 400

    order = db.session.get(Order, order_id)
    if not order or order.user_id != current_user.id:
        return jsonify({"error": "Order not found"}), 404

    # Check if a coupon is already applied to this order
    from models.gamification import Coupon

    existing_coupon = Coupon.query.filter_by(
        used_order_id=order.id, is_used=False
    ).first()
    if existing_coupon:
        return (
            jsonify({"error": "A coupon has already been applied to this order"}),
            400,
        )

    # Store original total BEFORE applying discount (if not already stored)
    if not order.original_total:
        order.original_total = order.total_price

    success, message, discount_amount, coupon_dict = GamificationService.apply_coupon(
        coupon_code, current_user.id, order
    )

    if success:
        # Update order total
        new_total = max(0, float(order.total_price) - discount_amount)
        order.total_price = new_total

        # Store coupon code in session for payment processing
        if "applied_coupons" not in session:
            session["applied_coupons"] = {}
        session["applied_coupons"][str(order.id)] = coupon_code

        # Commit order total update (but don't mark coupon as used yet)
        try:
            db.session.commit()
            return jsonify(
                {
                    "success": True,
                    "message": message,
                    "discount_amount": discount_amount,
                    "new_total": new_total,
                    "coupon": coupon_dict,
                }
            )
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": f"Error applying coupon: {str(e)}"}), 500
    else:
        return jsonify({"success": False, "error": message}), 400


@gamification_bp.route("/api/redemptions", methods=["GET"])
@login_required
def get_redemption_history():
    """Get user's redemption history with coupons"""
    from models.gamification import Coupon

    redemptions = (
        Redemption.query.filter_by(user_id=current_user.id)
        .order_by(Redemption.redeemed_at.desc())
        .all()
    )

    redemption_list = []
    for redemption in redemptions:
        redemption_dict = redemption.to_dict()

        # Get associated coupon and refresh from database to get latest status
        coupon = Coupon.query.filter_by(redemption_id=redemption.id).first()
        if coupon:
            # Refresh the coupon object to get latest is_used status
            db.session.refresh(coupon)
            redemption_dict["coupon"] = coupon.to_dict()
        else:
            redemption_dict["coupon"] = None

        redemption_list.append(redemption_dict)

    return jsonify({"redemptions": redemption_list})
