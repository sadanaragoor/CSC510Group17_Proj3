"""
Gamification models for points, badges, tiers, and achievements.
"""
from database.db import db
from datetime import datetime, date
from sqlalchemy import func


class PointsTransaction(db.Model):
    """Tracks all points earned and redeemed by users"""
    __tablename__ = "points_transactions"
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    points = db.Column(db.Integer, nullable=False)  # Positive for earned, negative for redeemed
    event_type = db.Column(db.String(100), nullable=False)  # e.g., 'purchase', 'review', 'streak', etc.
    description = db.Column(db.String(255), nullable=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship("User", backref=db.backref("points_transactions", lazy="dynamic"))
    order = db.relationship("Order", backref=db.backref("points_transactions", lazy="dynamic"))
    
    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "points": self.points,
            "event_type": self.event_type,
            "description": self.description,
            "order_id": self.order_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Badge(db.Model):
    """Defines available badges"""
    __tablename__ = "badges"
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    badge_type = db.Column(db.String(50), nullable=False)  # 'ingredient', 'behavioral', 'achievement'
    icon = db.Column(db.String(255), nullable=True)  # Icon name or emoji
    rarity = db.Column(db.String(20), default="common")  # common, rare, epic, legendary
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "slug": self.slug,
            "description": self.description,
            "badge_type": self.badge_type,
            "icon": self.icon,
            "rarity": self.rarity,
        }


class UserBadge(db.Model):
    """Tracks badges earned by users"""
    __tablename__ = "user_badges"
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    badge_id = db.Column(db.Integer, db.ForeignKey("badges.id"), nullable=False)
    earned_at = db.Column(db.DateTime, default=datetime.utcnow)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"), nullable=True)  # Order that triggered badge
    
    user = db.relationship("User", backref=db.backref("user_badges", lazy="dynamic"))
    badge = db.relationship("Badge", backref=db.backref("user_badges", lazy="dynamic"))
    order = db.relationship("Order", backref=db.backref("user_badges", lazy="dynamic"))
    
    __table_args__ = (db.UniqueConstraint('user_id', 'badge_id', name='unique_user_badge'),)
    
    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "badge_id": self.badge_id,
            "badge": self.badge.to_dict() if self.badge else None,
            "earned_at": self.earned_at.isoformat() if self.earned_at else None,
            "order_id": self.order_id,
        }


class DailyBonus(db.Model):
    """Tracks daily bonus challenges - allows up to 2 per day"""
    __tablename__ = "daily_bonuses"
    
    id = db.Column(db.Integer, primary_key=True)
    bonus_date = db.Column(db.Date, nullable=False)  # Removed unique=True to allow multiple per day
    description = db.Column(db.String(255), nullable=False)
    condition = db.Column(db.String(255), nullable=False)  # e.g., "order with pickles"
    points_reward = db.Column(db.Integer, nullable=False, default=30)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            "id": self.id,
            "bonus_date": self.bonus_date.isoformat() if self.bonus_date else None,
            "description": self.description,
            "condition": self.condition,
            "points_reward": self.points_reward,
            "is_active": self.is_active,
        }


class WeeklyChallenge(db.Model):
    """Tracks weekly challenges"""
    __tablename__ = "weekly_challenges"
    
    id = db.Column(db.Integer, primary_key=True)
    week_start = db.Column(db.Date, nullable=False)
    week_end = db.Column(db.Date, nullable=False)
    description = db.Column(db.String(255), nullable=False)
    condition = db.Column(db.String(255), nullable=False)  # e.g., "try 3 different patties"
    points_reward = db.Column(db.Integer, nullable=False, default=150)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            "id": self.id,
            "week_start": self.week_start.isoformat() if self.week_start else None,
            "week_end": self.week_end.isoformat() if self.week_end else None,
            "description": self.description,
            "condition": self.condition,
            "points_reward": self.points_reward,
            "is_active": self.is_active,
        }


class UserChallengeProgress(db.Model):
    """Tracks user progress on challenges"""
    __tablename__ = "user_challenge_progress"
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    challenge_id = db.Column(db.Integer, db.ForeignKey("weekly_challenges.id"), nullable=True)
    daily_bonus_id = db.Column(db.Integer, db.ForeignKey("daily_bonuses.id"), nullable=True)
    progress = db.Column(db.Integer, default=0)
    target = db.Column(db.Integer, nullable=False)
    completed = db.Column(db.Boolean, default=False)
    completed_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship("User", backref=db.backref("challenge_progress", lazy="dynamic"))
    challenge = db.relationship("WeeklyChallenge", backref=db.backref("user_progress", lazy="dynamic"))
    daily_bonus = db.relationship("DailyBonus", backref=db.backref("user_progress", lazy="dynamic"))
    
    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "challenge_id": self.challenge_id,
            "daily_bonus_id": self.daily_bonus_id,
            "progress": self.progress,
            "target": self.target,
            "completed": self.completed,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }


class PunchCard(db.Model):
    """Tracks punch card progress (every 10th burger gets 2x points)"""
    __tablename__ = "punch_cards"
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, unique=True)
    punches = db.Column(db.Integer, default=0)
    last_punch_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = db.relationship("User", backref=db.backref("punch_card", uselist=False))
    
    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "punches": self.punches,
            "last_punch_at": self.last_punch_at.isoformat() if self.last_punch_at else None,
        }


class Redemption(db.Model):
    """Tracks reward redemptions"""
    __tablename__ = "redemptions"
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    reward_type = db.Column(db.String(100), nullable=False)  # e.g., 'free_topping', 'skip_queue', etc.
    points_cost = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(255), nullable=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"), nullable=True)
    redeemed_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship("User", backref=db.backref("redemptions", lazy="dynamic"))
    order = db.relationship("Order", backref=db.backref("redemptions", lazy="dynamic"))
    
    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "reward_type": self.reward_type,
            "points_cost": self.points_cost,
            "description": self.description,
            "order_id": self.order_id,
            "redeemed_at": self.redeemed_at.isoformat() if self.redeemed_at else None,
        }


class Coupon(db.Model):
    """Tracks coupon codes generated from reward redemptions"""
    __tablename__ = "coupons"
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    redemption_id = db.Column(db.Integer, db.ForeignKey("redemptions.id"), nullable=False)
    coupon_code = db.Column(db.String(50), unique=True, nullable=False)  # e.g., SHACK-4F92AD
    reward_type = db.Column(db.String(100), nullable=False)  # Same as redemption reward_type
    is_used = db.Column(db.Boolean, default=False)
    used_at = db.Column(db.DateTime, nullable=True)
    used_order_id = db.Column(db.Integer, db.ForeignKey("orders.id"), nullable=True)
    expiry_date = db.Column(db.Date, nullable=False)  # Coupon expiry date
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship("User", backref=db.backref("coupons", lazy="dynamic"))
    redemption = db.relationship("Redemption", backref=db.backref("coupon", uselist=False))
    used_order = db.relationship("Order", foreign_keys=[used_order_id], backref=db.backref("applied_coupons", lazy="dynamic"))
    
    def is_valid(self):
        """Check if coupon is valid (not expired, not used)"""
        from datetime import date
        return not self.is_used and self.expiry_date >= date.today()
    
    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "redemption_id": self.redemption_id,
            "coupon_code": self.coupon_code,
            "reward_type": self.reward_type,
            "is_used": self.is_used,
            "used_at": self.used_at.isoformat() if self.used_at else None,
            "used_order_id": self.used_order_id,
            "expiry_date": self.expiry_date.isoformat() if self.expiry_date else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "is_valid": self.is_valid(),
        }

