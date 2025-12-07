"""
Comprehensive tests for apply_coupon covering all reward types.
"""

from decimal import Decimal
from datetime import date, timedelta
from models.gamification import Coupon, Redemption
from models.order import Order, OrderItem
from models.menu_item import MenuItem
from services.gamification_service import GamificationService
from database.db import db


class TestGamificationServiceApplyCouponComprehensive:
    """Comprehensive tests for apply_coupon method."""

    def test_apply_coupon_free_topping(self, app, test_user):
        """Test applying free_topping coupon."""
        with app.app_context():
            topping = MenuItem(
                name="Lettuce",
                category="topping",
                price=Decimal("0.50"),
                is_available=True,
            )
            db.session.add(topping)
            db.session.flush()

            order = Order(
                user_id=test_user,
                total_price=Decimal("10.00"),
                original_total=Decimal("10.00"),
                status="Pending",
            )
            db.session.add(order)
            db.session.flush()

            item = OrderItem(
                order_id=order.id,
                menu_item_id=topping.id,
                name="Lettuce",
                price=Decimal("0.50"),
                quantity=2,
            )
            db.session.add(item)
            db.session.flush()

            redemption = Redemption(
                user_id=test_user, reward_type="free_topping", points_cost=100
            )
            db.session.add(redemption)
            db.session.flush()

            coupon = Coupon(
                user_id=test_user,
                redemption_id=redemption.id,
                coupon_code="SHACK-TEST",
                reward_type="free_topping",
                expiry_date=date.today() + timedelta(days=30),
                is_used=False,
            )
            db.session.add(coupon)
            db.session.commit()

            is_valid, message, discount, coupon_dict = GamificationService.apply_coupon(
                "SHACK-TEST", test_user, order
            )

            assert is_valid is True
            assert discount == 1.0  # 2 * 0.50
            assert "Free topping" in message

    def test_apply_coupon_free_premium_sauce(self, app, test_user):
        """Test applying free_premium_sauce coupon."""
        with app.app_context():
            sauce = MenuItem(
                name="Green Sauce",
                category="sauce",
                price=Decimal("0.15"),
                is_available=True,
            )
            db.session.add(sauce)
            db.session.flush()

            order = Order(
                user_id=test_user,
                total_price=Decimal("10.00"),
                original_total=Decimal("10.00"),
                status="Pending",
            )
            db.session.add(order)
            db.session.flush()

            item = OrderItem(
                order_id=order.id,
                menu_item_id=sauce.id,
                name="Green Sauce",
                price=Decimal("0.15"),
                quantity=1,
            )
            db.session.add(item)
            db.session.flush()

            redemption = Redemption(
                user_id=test_user, reward_type="free_premium_sauce", points_cost=125
            )
            db.session.add(redemption)
            db.session.flush()

            coupon = Coupon(
                user_id=test_user,
                redemption_id=redemption.id,
                coupon_code="SHACK-TEST",
                reward_type="free_premium_sauce",
                expiry_date=date.today() + timedelta(days=30),
                is_used=False,
            )
            db.session.add(coupon)
            db.session.commit()

            is_valid, message, discount, coupon_dict = GamificationService.apply_coupon(
                "SHACK-TEST", test_user, order
            )

            assert is_valid is True
            assert discount == 0.15
            assert "Free premium sauce" in message

    def test_apply_coupon_three_dollar_off(self, app, test_user):
        """Test applying three_dollar_off coupon."""
        with app.app_context():
            order = Order(
                user_id=test_user,
                total_price=Decimal("10.00"),
                original_total=Decimal("10.00"),
                status="Pending",
            )
            db.session.add(order)
            db.session.flush()

            redemption = Redemption(
                user_id=test_user, reward_type="three_dollar_off", points_cost=300
            )
            db.session.add(redemption)
            db.session.flush()

            coupon = Coupon(
                user_id=test_user,
                redemption_id=redemption.id,
                coupon_code="SHACK-TEST",
                reward_type="three_dollar_off",
                expiry_date=date.today() + timedelta(days=30),
                is_used=False,
            )
            db.session.add(coupon)
            db.session.commit()

            is_valid, message, discount, coupon_dict = GamificationService.apply_coupon(
                "SHACK-TEST", test_user, order
            )

            assert is_valid is True
            assert discount == 3.0
            assert "$3 discount" in message

    def test_apply_coupon_three_dollar_off_small_order(self, app, test_user):
        """Test three_dollar_off on order smaller than $3."""
        with app.app_context():
            order = Order(
                user_id=test_user,
                total_price=Decimal("2.00"),
                original_total=Decimal("2.00"),
                status="Pending",
            )
            db.session.add(order)
            db.session.flush()

            redemption = Redemption(
                user_id=test_user, reward_type="three_dollar_off", points_cost=300
            )
            db.session.add(redemption)
            db.session.flush()

            coupon = Coupon(
                user_id=test_user,
                redemption_id=redemption.id,
                coupon_code="SHACK-TEST",
                reward_type="three_dollar_off",
                expiry_date=date.today() + timedelta(days=30),
                is_used=False,
            )
            db.session.add(coupon)
            db.session.commit()

            is_valid, message, discount, coupon_dict = GamificationService.apply_coupon(
                "SHACK-TEST", test_user, order
            )

            assert is_valid is True
            assert discount == 2.0  # Should not exceed order total
            assert "$3 discount" in message

    def test_apply_coupon_free_patty_upgrade(self, app, test_user):
        """Test applying free_patty_upgrade coupon."""
        with app.app_context():
            patty = MenuItem(
                name="Beef Patty",
                category="patty",
                price=Decimal("3.50"),
                is_available=True,
            )
            db.session.add(patty)
            db.session.flush()

            order = Order(
                user_id=test_user,
                total_price=Decimal("10.00"),
                original_total=Decimal("10.00"),
                status="Pending",
            )
            db.session.add(order)
            db.session.flush()

            item = OrderItem(
                order_id=order.id,
                menu_item_id=patty.id,
                name="Beef Patty",
                price=Decimal("3.50"),
                quantity=1,
            )
            db.session.add(item)
            db.session.flush()

            redemption = Redemption(
                user_id=test_user, reward_type="free_patty_upgrade", points_cost=250
            )
            db.session.add(redemption)
            db.session.flush()

            coupon = Coupon(
                user_id=test_user,
                redemption_id=redemption.id,
                coupon_code="SHACK-TEST",
                reward_type="free_patty_upgrade",
                expiry_date=date.today() + timedelta(days=30),
                is_used=False,
            )
            db.session.add(coupon)
            db.session.commit()

            is_valid, message, discount, coupon_dict = GamificationService.apply_coupon(
                "SHACK-TEST", test_user, order
            )

            assert is_valid is True
            assert discount == 3.5
            assert "Free patty upgrade" in message

    def test_apply_coupon_skip_queue(self, app, test_user):
        """Test applying skip_queue coupon."""
        with app.app_context():
            order = Order(
                user_id=test_user,
                total_price=Decimal("10.00"),
                original_total=Decimal("10.00"),
                status="Pending",
            )
            db.session.add(order)
            db.session.flush()

            redemption = Redemption(
                user_id=test_user, reward_type="skip_queue", points_cost=300
            )
            db.session.add(redemption)
            db.session.flush()

            coupon = Coupon(
                user_id=test_user,
                redemption_id=redemption.id,
                coupon_code="SHACK-TEST",
                reward_type="skip_queue",
                expiry_date=date.today() + timedelta(days=30),
                is_used=False,
            )
            db.session.add(coupon)
            db.session.commit()

            is_valid, message, discount, coupon_dict = GamificationService.apply_coupon(
                "SHACK-TEST", test_user, order
            )

            assert is_valid is True
            assert discount == 0.0  # No price change
            assert "Priority queue" in message

            db.session.refresh(order)
            assert order.status == "Priority"

    def test_apply_coupon_five_dollar_off(self, app, test_user):
        """Test applying five_dollar_off coupon."""
        with app.app_context():
            order = Order(
                user_id=test_user,
                total_price=Decimal("10.00"),
                original_total=Decimal("10.00"),
                status="Pending",
            )
            db.session.add(order)
            db.session.flush()

            redemption = Redemption(
                user_id=test_user, reward_type="five_dollar_off", points_cost=500
            )
            db.session.add(redemption)
            db.session.flush()

            coupon = Coupon(
                user_id=test_user,
                redemption_id=redemption.id,
                coupon_code="SHACK-TEST",
                reward_type="five_dollar_off",
                expiry_date=date.today() + timedelta(days=30),
                is_used=False,
            )
            db.session.add(coupon)
            db.session.commit()

            is_valid, message, discount, coupon_dict = GamificationService.apply_coupon(
                "SHACK-TEST", test_user, order
            )

            assert is_valid is True
            assert discount == 5.0
            assert "$5 discount" in message

    def test_apply_coupon_five_dollar_off_small_order(self, app, test_user):
        """Test five_dollar_off on order smaller than $5."""
        with app.app_context():
            order = Order(
                user_id=test_user,
                total_price=Decimal("3.00"),
                original_total=Decimal("3.00"),
                status="Pending",
            )
            db.session.add(order)
            db.session.flush()

            redemption = Redemption(
                user_id=test_user, reward_type="five_dollar_off", points_cost=500
            )
            db.session.add(redemption)
            db.session.flush()

            coupon = Coupon(
                user_id=test_user,
                redemption_id=redemption.id,
                coupon_code="SHACK-TEST",
                reward_type="five_dollar_off",
                expiry_date=date.today() + timedelta(days=30),
                is_used=False,
            )
            db.session.add(coupon)
            db.session.commit()

            is_valid, message, discount, coupon_dict = GamificationService.apply_coupon(
                "SHACK-TEST", test_user, order
            )

            assert is_valid is True
            assert discount == 3.0  # Should not exceed order total
            assert "$5 discount" in message

    def test_apply_coupon_no_sauces(self, app, test_user):
        """Test free_premium_sauce coupon when order has no sauces."""
        with app.app_context():
            order = Order(
                user_id=test_user,
                total_price=Decimal("10.00"),
                original_total=Decimal("10.00"),
                status="Pending",
            )
            db.session.add(order)
            db.session.flush()

            redemption = Redemption(
                user_id=test_user, reward_type="free_premium_sauce", points_cost=125
            )
            db.session.add(redemption)
            db.session.flush()

            coupon = Coupon(
                user_id=test_user,
                redemption_id=redemption.id,
                coupon_code="SHACK-TEST",
                reward_type="free_premium_sauce",
                expiry_date=date.today() + timedelta(days=30),
                is_used=False,
            )
            db.session.add(coupon)
            db.session.commit()

            is_valid, message, discount, coupon_dict = GamificationService.apply_coupon(
                "SHACK-TEST", test_user, order
            )

            assert is_valid is True
            assert discount == 0.0
            assert "no sauces in order" in message
