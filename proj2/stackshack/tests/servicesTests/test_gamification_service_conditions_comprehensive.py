"""
Comprehensive tests for _check_daily_condition covering all condition branches.
"""

from decimal import Decimal
from models.order import Order, OrderItem
from models.menu_item import MenuItem
from services.gamification_service import GamificationService
from database.db import db


class TestGamificationServiceConditionsComprehensive:
    """Comprehensive tests for daily condition checking."""

    def test_check_keto_bun(self, app, test_user):
        """Test keto bun condition."""
        with app.app_context():
            bun = MenuItem(
                name="Keto Bun",
                category="bun",
                price=Decimal("2.00"),
                is_available=True,
            )
            db.session.add(bun)
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
                menu_item_id=bun.id,
                name="Keto Bun",
                price=Decimal("2.00"),
                quantity=1,
            )
            db.session.add(item)
            db.session.commit()

            result = GamificationService._check_daily_condition(
                "keto_bun", order.items.all(), order, order.ordered_at, 12, 0
            )
            assert result is True

    def test_check_sesame_bun(self, app, test_user):
        """Test sesame bun condition."""
        with app.app_context():
            bun = MenuItem(
                name="Sesame Bun",
                category="bun",
                price=Decimal("1.50"),
                is_available=True,
            )
            db.session.add(bun)
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
                menu_item_id=bun.id,
                name="Sesame Bun",
                price=Decimal("1.50"),
                quantity=1,
            )
            db.session.add(item)
            db.session.commit()

            result = GamificationService._check_daily_condition(
                "sesame_bun", order.items.all(), order, order.ordered_at, 12, 0
            )
            assert result is True

    def test_check_black_sesame_bun(self, app, test_user):
        """Test black sesame bun condition."""
        with app.app_context():
            bun = MenuItem(
                name="Black Sesame Bun",
                category="bun",
                price=Decimal("2.00"),
                is_available=True,
            )
            db.session.add(bun)
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
                menu_item_id=bun.id,
                name="Black Sesame Bun",
                price=Decimal("2.00"),
                quantity=1,
            )
            db.session.add(item)
            db.session.commit()

            result = GamificationService._check_daily_condition(
                "sesame_bun", order.items.all(), order, order.ordered_at, 12, 0
            )
            assert result is True

    def test_check_veggie_bun(self, app, test_user):
        """Test veggie bun condition."""
        with app.app_context():
            bun = MenuItem(
                name="Beetroot Bun",
                category="bun",
                price=Decimal("2.00"),
                is_available=True,
            )
            db.session.add(bun)
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
                menu_item_id=bun.id,
                name="Beetroot Bun",
                price=Decimal("2.00"),
                quantity=1,
            )
            db.session.add(item)
            db.session.commit()

            result = GamificationService._check_daily_condition(
                "veggie_bun", order.items.all(), order, order.ordered_at, 12, 0
            )
            assert result is True

    def test_check_wheat_bun(self, app, test_user):
        """Test wheat bun condition."""
        with app.app_context():
            bun = MenuItem(
                name="Wheat Bun",
                category="bun",
                price=Decimal("1.50"),
                is_available=True,
            )
            db.session.add(bun)
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
                menu_item_id=bun.id,
                name="Wheat Bun",
                price=Decimal("1.50"),
                quantity=1,
            )
            db.session.add(item)
            db.session.commit()

            result = GamificationService._check_daily_condition(
                "wheat_bun", order.items.all(), order, order.ordered_at, 12, 0
            )
            assert result is True

    def test_check_plain_bun(self, app, test_user):
        """Test plain bun condition."""
        with app.app_context():
            bun = MenuItem(
                name="Plain Bun",
                category="bun",
                price=Decimal("1.00"),
                is_available=True,
            )
            db.session.add(bun)
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
                menu_item_id=bun.id,
                name="Plain Bun",
                price=Decimal("1.00"),
                quantity=1,
            )
            db.session.add(item)
            db.session.commit()

            result = GamificationService._check_daily_condition(
                "plain_bun", order.items.all(), order, order.ordered_at, 12, 0
            )
            assert result is True

    def test_check_two_cheeses(self, app, test_user):
        """Test two cheeses condition."""
        with app.app_context():
            cheese1 = MenuItem(
                name="Cheddar Cheese",
                category="cheese",
                price=Decimal("1.00"),
                is_available=True,
            )
            cheese2 = MenuItem(
                name="Swiss Cheese",
                category="cheese",
                price=Decimal("1.00"),
                is_available=True,
            )
            db.session.add_all([cheese1, cheese2])
            db.session.flush()

            order = Order(
                user_id=test_user,
                total_price=Decimal("10.00"),
                original_total=Decimal("10.00"),
                status="Pending",
            )
            db.session.add(order)
            db.session.flush()

            item1 = OrderItem(
                order_id=order.id,
                menu_item_id=cheese1.id,
                name="Cheddar Cheese",
                price=Decimal("1.00"),
                quantity=1,
            )
            item2 = OrderItem(
                order_id=order.id,
                menu_item_id=cheese2.id,
                name="Swiss Cheese",
                price=Decimal("1.00"),
                quantity=1,
            )
            db.session.add_all([item1, item2])
            db.session.commit()

            result = GamificationService._check_daily_condition(
                "two_cheeses", order.items.all(), order, order.ordered_at, 12, 0
            )
            assert result is True

    def test_check_before_11am(self, app, test_user):
        """Test before 11am condition."""
        with app.app_context():
            order = Order(
                user_id=test_user,
                total_price=Decimal("10.00"),
                original_total=Decimal("10.00"),
                status="Pending",
            )
            db.session.add(order)
            db.session.commit()

            result = GamificationService._check_daily_condition(
                "before_11am", order.items.all(), order, order.ordered_at, 10, 0
            )
            assert result is True

            result2 = GamificationService._check_daily_condition(
                "before_11am", order.items.all(), order, order.ordered_at, 11, 0
            )
            assert result2 is False

    def test_check_between_2_4pm(self, app, test_user):
        """Test between 2-4pm condition."""
        with app.app_context():
            order = Order(
                user_id=test_user,
                total_price=Decimal("10.00"),
                original_total=Decimal("10.00"),
                status="Pending",
            )
            db.session.add(order)
            db.session.commit()

            result = GamificationService._check_daily_condition(
                "between_2_4pm", order.items.all(), order, order.ordered_at, 14, 0
            )
            assert result is True

            result2 = GamificationService._check_daily_condition(
                "between_2_4pm", order.items.all(), order, order.ordered_at, 16, 0
            )
            assert result2 is False

    def test_check_after_8pm(self, app, test_user):
        """Test after 8pm condition."""
        with app.app_context():
            order = Order(
                user_id=test_user,
                total_price=Decimal("10.00"),
                original_total=Decimal("10.00"),
                status="Pending",
            )
            db.session.add(order)
            db.session.commit()

            result = GamificationService._check_daily_condition(
                "after_8pm", order.items.all(), order, order.ordered_at, 20, 0
            )
            assert result is True

            result2 = GamificationService._check_daily_condition(
                "after_8pm", order.items.all(), order, order.ordered_at, 19, 0
            )
            assert result2 is False

    def test_check_lunch_rush(self, app, test_user):
        """Test lunch rush condition."""
        with app.app_context():
            order = Order(
                user_id=test_user,
                total_price=Decimal("10.00"),
                original_total=Decimal("10.00"),
                status="Pending",
            )
            db.session.add(order)
            db.session.commit()

            result = GamificationService._check_daily_condition(
                "lunch_rush", order.items.all(), order, order.ordered_at, 12, 0
            )
            assert result is True

    def test_check_exact_222(self, app, test_user):
        """Test exact 2:22 condition."""
        with app.app_context():
            order = Order(
                user_id=test_user,
                total_price=Decimal("10.00"),
                original_total=Decimal("10.00"),
                status="Pending",
            )
            db.session.add(order)
            db.session.commit()

            result = GamificationService._check_daily_condition(
                "exact_222", order.items.all(), order, order.ordered_at, 14, 22
            )
            assert result is True

            result2 = GamificationService._check_daily_condition(
                "exact_222", order.items.all(), order, order.ordered_at, 14, 23
            )
            assert result2 is False

    def test_check_all_healthy(self, app, test_user):
        """Test all healthy condition."""
        with app.app_context():
            bun = MenuItem(
                name="Keto Bun",
                category="bun",
                price=Decimal("2.00"),
                is_available=True,
                is_healthy_choice=True,
            )
            patty = MenuItem(
                name="Mixed Veg Patty",
                category="patty",
                price=Decimal("3.00"),
                is_available=True,
                is_healthy_choice=True,
            )
            db.session.add_all([bun, patty])
            db.session.flush()

            order = Order(
                user_id=test_user,
                total_price=Decimal("10.00"),
                original_total=Decimal("10.00"),
                status="Pending",
            )
            db.session.add(order)
            db.session.flush()

            item1 = OrderItem(
                order_id=order.id,
                menu_item_id=bun.id,
                name="Keto Bun",
                price=Decimal("2.00"),
                quantity=1,
            )
            item2 = OrderItem(
                order_id=order.id,
                menu_item_id=patty.id,
                name="Mixed Veg Patty",
                price=Decimal("3.00"),
                quantity=1,
            )
            db.session.add_all([item1, item2])
            db.session.commit()

            result = GamificationService._check_daily_condition(
                "all_healthy", order.items.all(), order, order.ordered_at, 12, 0
            )
            assert result is True

    def test_check_all_healthy_false(self, app, test_user):
        """Test all healthy condition with non-healthy item."""
        with app.app_context():
            bun = MenuItem(
                name="Keto Bun",
                category="bun",
                price=Decimal("2.00"),
                is_available=True,
                is_healthy_choice=True,
            )
            patty = MenuItem(
                name="Beef Patty",
                category="patty",
                price=Decimal("3.00"),
                is_available=True,
                is_healthy_choice=False,
            )
            db.session.add_all([bun, patty])
            db.session.flush()

            order = Order(
                user_id=test_user,
                total_price=Decimal("10.00"),
                original_total=Decimal("10.00"),
                status="Pending",
            )
            db.session.add(order)
            db.session.flush()

            item1 = OrderItem(
                order_id=order.id,
                menu_item_id=bun.id,
                name="Keto Bun",
                price=Decimal("2.00"),
                quantity=1,
            )
            item2 = OrderItem(
                order_id=order.id,
                menu_item_id=patty.id,
                name="Beef Patty",
                price=Decimal("3.00"),
                quantity=1,
            )
            db.session.add_all([item1, item2])
            db.session.commit()

            result = GamificationService._check_daily_condition(
                "all_healthy", order.items.all(), order, order.ordered_at, 12, 0
            )
            assert result is False

    def test_check_three_toppings(self, app, test_user):
        """Test three toppings condition."""
        with app.app_context():
            top1 = MenuItem(
                name="Lettuce",
                category="topping",
                price=Decimal("0.50"),
                is_available=True,
            )
            top2 = MenuItem(
                name="Tomato",
                category="topping",
                price=Decimal("0.50"),
                is_available=True,
            )
            top3 = MenuItem(
                name="Onion",
                category="topping",
                price=Decimal("0.50"),
                is_available=True,
            )
            db.session.add_all([top1, top2, top3])
            db.session.flush()

            order = Order(
                user_id=test_user,
                total_price=Decimal("10.00"),
                original_total=Decimal("10.00"),
                status="Pending",
            )
            db.session.add(order)
            db.session.flush()

            item1 = OrderItem(
                order_id=order.id,
                menu_item_id=top1.id,
                name="Lettuce",
                price=Decimal("0.50"),
                quantity=1,
            )
            item2 = OrderItem(
                order_id=order.id,
                menu_item_id=top2.id,
                name="Tomato",
                price=Decimal("0.50"),
                quantity=1,
            )
            item3 = OrderItem(
                order_id=order.id,
                menu_item_id=top3.id,
                name="Onion",
                price=Decimal("0.50"),
                quantity=1,
            )
            db.session.add_all([item1, item2, item3])
            db.session.commit()

            result = GamificationService._check_daily_condition(
                "three_toppings", order.items.all(), order, order.ordered_at, 12, 0
            )
            assert result is True

    def test_check_all_toppings(self, app, test_user):
        """Test all toppings condition."""
        with app.app_context():
            toppings = [
                MenuItem(
                    name="Lettuce",
                    category="topping",
                    price=Decimal("0.50"),
                    is_available=True,
                ),
                MenuItem(
                    name="Tomato",
                    category="topping",
                    price=Decimal("0.50"),
                    is_available=True,
                ),
                MenuItem(
                    name="Onion",
                    category="topping",
                    price=Decimal("0.50"),
                    is_available=True,
                ),
                MenuItem(
                    name="Pickles",
                    category="topping",
                    price=Decimal("0.50"),
                    is_available=True,
                ),
                MenuItem(
                    name="Capsicum",
                    category="topping",
                    price=Decimal("0.50"),
                    is_available=True,
                ),
            ]
            db.session.add_all(toppings)
            db.session.flush()

            order = Order(
                user_id=test_user,
                total_price=Decimal("10.00"),
                original_total=Decimal("10.00"),
                status="Pending",
            )
            db.session.add(order)
            db.session.flush()

            items = [
                OrderItem(
                    order_id=order.id,
                    menu_item_id=t.id,
                    name=t.name,
                    price=t.price,
                    quantity=1,
                )
                for t in toppings
            ]
            db.session.add_all(items)
            db.session.commit()

            result = GamificationService._check_daily_condition(
                "all_toppings", order.items.all(), order, order.ordered_at, 12, 0
            )
            assert result is True

    def test_check_two_sauces(self, app, test_user):
        """Test two sauces condition."""
        with app.app_context():
            sauce1 = MenuItem(
                name="Ketchup",
                category="sauce",
                price=Decimal("0.25"),
                is_available=True,
            )
            sauce2 = MenuItem(
                name="Mayo", category="sauce", price=Decimal("0.25"), is_available=True
            )
            db.session.add_all([sauce1, sauce2])
            db.session.flush()

            order = Order(
                user_id=test_user,
                total_price=Decimal("10.00"),
                original_total=Decimal("10.00"),
                status="Pending",
            )
            db.session.add(order)
            db.session.flush()

            item1 = OrderItem(
                order_id=order.id,
                menu_item_id=sauce1.id,
                name="Ketchup",
                price=Decimal("0.25"),
                quantity=1,
            )
            item2 = OrderItem(
                order_id=order.id,
                menu_item_id=sauce2.id,
                name="Mayo",
                price=Decimal("0.25"),
                quantity=1,
            )
            db.session.add_all([item1, item2])
            db.session.commit()

            result = GamificationService._check_daily_condition(
                "two_sauces", order.items.all(), order, order.ordered_at, 12, 0
            )
            assert result is True

    def test_check_unknown_condition(self, app, test_user):
        """Test unknown condition returns False."""
        with app.app_context():
            order = Order(
                user_id=test_user,
                total_price=Decimal("10.00"),
                original_total=Decimal("10.00"),
                status="Pending",
            )
            db.session.add(order)
            db.session.commit()

            result = GamificationService._check_daily_condition(
                "unknown_condition", order.items.all(), order, order.ordered_at, 12, 0
            )
            assert result is False
