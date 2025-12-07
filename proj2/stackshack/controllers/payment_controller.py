"""
Payment Controller
Handles payment processing business logic
"""

from datetime import datetime, timedelta
from flask import session
from database.db import db
from models.payment import Transaction, CampusCard, Receipt
from models.order import Order
from services.payment_gateway import PaymentGatewayService


class PaymentController:
    """
    Controller for payment-related operations
    """

    @staticmethod
    def process_payment(payment_data):
        """
        Process a payment through the dummy gateway

        Args:
            payment_data (dict): Payment information

        Returns:
            tuple: (success, message, transaction_data)
        """
        try:
            # Validate order exists and belongs to user
            order = Order.query.get(payment_data.get("order_id"))
            if not order:
                return False, "Order not found", None

            if order.user_id != payment_data.get("user_id"):
                return False, "Unauthorized", None

            # Check if order already paid
            existing_transaction = Transaction.query.filter_by(
                order_id=order.id, status="success"
            ).first()

            if existing_transaction:
                return False, "Order already paid", None

            # Refresh order from database to get latest total_price (in case coupon was applied)
            db.session.refresh(order)

            # Use the amount from payment_data (which includes coupon discount) or fall back to order.total_price
            payment_amount = float(payment_data.get("amount", order.total_price))

            # Initialize payment gateway
            gateway = PaymentGatewayService(simulation_mode="random_90")

            # Process payment
            payment_response = gateway.process_payment(payment_data)

            # Create transaction record
            transaction = Transaction(
                transaction_id=payment_response["transaction_id"],
                order_id=order.id,
                user_id=order.user_id,
                amount=payment_amount,
                payment_method=payment_response["payment_method"],
                payment_provider=payment_response.get("payment_provider"),
                masked_card=payment_response.get("masked_card"),
                card_type=payment_response.get("card_type"),
                status=payment_response["status"],
                failure_reason=payment_response.get("failure_reason"),
                initiated_at=datetime.utcnow(),
                completed_at=datetime.utcnow() if payment_response["success"] else None,
            )

            db.session.add(transaction)

            # Update order status if payment successful
            if payment_response["success"]:
                order.status = "Paid"

            # Commit transaction first to get the transaction.id
            db.session.commit()

            # Now generate receipt with valid transaction.id
            if payment_response["success"]:
                receipt = PaymentController._generate_receipt(transaction, order)
                db.session.add(receipt)
                db.session.commit()

                # Mark applied coupon as used if one was applied
                try:
                    from models.gamification import Coupon

                    # First, try to get coupon from session
                    coupon_code = session.get("applied_coupons", {}).get(str(order.id))
                    coupon = None

                    if coupon_code:
                        coupon = Coupon.query.filter_by(
                            coupon_code=coupon_code.upper()
                        ).first()

                    # Fallback: Check if any coupon was applied to this order (by used_order_id)
                    if not coupon:
                        coupon = Coupon.query.filter_by(
                            used_order_id=order.id, is_used=False
                        ).first()

                    # Mark coupon as used if found
                    if coupon and not coupon.is_used:
                        coupon.is_used = True
                        coupon.used_at = datetime.utcnow()
                        coupon.used_order_id = order.id
                        db.session.commit()
                        print(
                            f"Marked coupon {coupon.coupon_code} as used for order {order.id}"
                        )

                    # Remove from session
                    if "applied_coupons" in session:
                        session["applied_coupons"].pop(str(order.id), None)
                        session.modified = True
                except Exception as e:
                    print(f"Error marking coupon as used: {str(e)}")
                    import traceback

                    traceback.print_exc()

                # Process gamification: points, badges, challenges
                try:
                    from services.gamification_service import GamificationService

                    # Process order points with all bonuses
                    total_points, breakdown = GamificationService.process_order_points(
                        order
                    )

                    # Check and grant badges
                    GamificationService.check_and_grant_badges(order.user_id, order)

                    # Check daily bonus
                    daily_bonus_success, daily_bonus = (
                        GamificationService.check_daily_bonus(order.user_id, order)
                    )

                    # Check weekly challenge
                    weekly_challenge_success, weekly_challenge = (
                        GamificationService.check_weekly_challenge(order.user_id, order)
                    )

                    # Update user tier
                    GamificationService.update_user_tier(order.user_id)

                except Exception as e:
                    # Log error but don't fail payment
                    print(f"Gamification processing error: {str(e)}")

            return (
                payment_response["success"],
                payment_response["message"],
                transaction.to_dict(),
            )

        except Exception as e:
            db.session.rollback()
            return False, f"Payment processing error: {str(e)}", None

    @staticmethod
    def _generate_receipt(transaction, order):
        """Generate a receipt for successful transaction"""
        receipt = Receipt(
            transaction_id=transaction.id,
            receipt_number=Receipt.generate_receipt_number(),
            order_id=order.id,
            user_id=order.user_id,
            total_amount=transaction.amount,
            payment_method=transaction.payment_method,
            generated_at=datetime.utcnow(),
        )

        # Generate HTML receipt content
        receipt_html = PaymentController._create_receipt_html(transaction, order)
        receipt.receipt_html = receipt_html

        return receipt

    @staticmethod
    def _create_receipt_html(transaction, order):
        """Create HTML content for receipt - Professional receipt format with burger grouping"""
        items_html = ""
        subtotal = 0

        # Group items by burger_index
        all_items = order.items.all()
        burgers = {}
        for item in all_items:
            burger_idx = item.burger_index if item.burger_index is not None else 0
            if burger_idx not in burgers:
                burgers[burger_idx] = []
            burgers[burger_idx].append(item)

        # Generate HTML for each burger group
        custom_counter = 0
        for burger_index in sorted(burgers.keys()):
            burger_items = burgers[burger_index]
            burger_total = 0

            # Get burger name (if available from first item)
            burger_name = (
                burger_items[0].burger_name
                if burger_items and burger_items[0].burger_name
                else None
            )

            # Count custom burgers for proper numbering
            if not burger_name:
                custom_counter += 1
                burger_display_name = f"Custom Burger #{custom_counter}"
            else:
                burger_display_name = burger_name

            # Add burger header if multiple burgers
            if len(burgers) > 1:
                items_html += f"""
                    <tr style="background: #f8f8f8;">
                        <td colspan="3" style="padding: 6px 4px; font-weight: bold; font-size: 10px;">
                            🍔 {burger_display_name}
                        </td>
                    </tr>
                """

            # Add items for this burger
            for item in burger_items:
                item_total = float(item.price) * item.quantity
                burger_total += item_total
                items_html += f"""
                    <tr>
                        <td style="padding-left: {'10px' if len(burgers) > 1 else '0'};">{item.name}</td>
                        <td>x{item.quantity}</td>
                        <td>${item_total:.2f}</td>
                    </tr>
                """

            # Add burger subtotal if multiple burgers
            if len(burgers) > 1:
                items_html += f"""
                    <tr style="border-bottom: 1px solid #ddd;">
                        <td colspan="2" style="text-align: right; padding: 4px; font-size: 9px; font-style: italic;">{burger_display_name} Total:</td>
                        <td style="font-weight: bold;">${burger_total:.2f}</td>
                    </tr>
                """

            subtotal += burger_total

        # Calculate tax and total (if applicable)
        tax_rate = 0.00  # No tax for now, but structure is ready
        tax_amount = subtotal * tax_rate
        total = float(transaction.amount)

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                @page {{
                    margin: 10mm;
                }}
                * {{
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }}
                body {{
                    font-family: 'Courier New', monospace;
                    font-size: 11px;
                    line-height: 1.4;
                    background: #f5f5f5;
                    padding: 15px;
                    color: #000;
                }}
                .receipt {{
                    max-width: 320px;
                    margin: 0 auto;
                    background: white;
                    padding: 15px;
                    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                }}
                .header {{
                    text-align: center;
                    margin-bottom: 12px;
                    padding-bottom: 10px;
                    border-bottom: 2px solid #000;
                }}
                .logo {{
                    font-size: 16px;
                    font-weight: bold;
                    margin-bottom: 3px;
                    letter-spacing: 1px;
                }}
                .tagline {{
                    font-size: 8px;
                    color: #666;
                    margin: 2px 0 6px 0;
                }}
                .contact {{
                    font-size: 8px;
                    line-height: 1.3;
                    color: #666;
                }}
                .divider {{
                    border-top: 1px dashed #999;
                    margin: 10px 0;
                }}
                .section-title {{
                    font-weight: bold;
                    font-size: 10px;
                    margin: 10px 0 6px 0;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                }}
                .info-line {{
                    display: flex;
                    justify-content: space-between;
                    margin: 3px 0;
                    font-size: 9px;
                    line-height: 1.3;
                }}
                .info-label {{
                    color: #666;
                }}
                .info-value {{
                    font-weight: bold;
                    text-align: right;
                }}
                .items-table {{
                    width: 100%;
                    margin: 8px 0;
                    font-size: 9px;
                    border-collapse: collapse;
                }}
                .items-table th {{
                    text-align: left;
                    padding: 4px 0;
                    border-bottom: 1px solid #000;
                    font-weight: bold;
                    font-size: 9px;
                }}
                .items-table td {{
                    padding: 4px 0;
                }}
                .items-table td:nth-child(2) {{
                    text-align: center;
                    padding: 0 5px;
                }}
                .items-table td:nth-child(3) {{
                    text-align: right;
                }}
                .totals {{
                    margin-top: 10px;
                    padding-top: 8px;
                    border-top: 1px solid #000;
                }}
                .total-line {{
                    display: flex;
                    justify-content: space-between;
                    margin: 3px 0;
                    font-size: 10px;
                }}
                .grand-total {{
                    display: flex;
                    justify-content: space-between;
                    margin: 8px 0;
                    padding: 8px 0;
                    font-size: 13px;
                    font-weight: bold;
                    border-top: 2px solid #000;
                    border-bottom: 2px solid #000;
                }}
                .footer {{
                    text-align: center;
                    margin-top: 12px;
                    padding-top: 10px;
                    border-top: 1px dashed #999;
                    font-size: 8px;
                    color: #666;
                    line-height: 1.4;
                }}
                .footer p {{
                    margin: 3px 0;
                }}
                .barcode {{
                    text-align: center;
                    font-size: 18px;
                    margin: 10px 0;
                    letter-spacing: 2px;
                    font-weight: bold;
                }}
                .payment-badge {{
                    display: inline-block;
                    padding: 3px 6px;
                    background: #000;
                    color: white;
                    border-radius: 2px;
                    font-size: 8px;
                    font-weight: bold;
                    margin: 6px 0;
                }}
                @media print {{
                    body {{
                        background: white;
                        padding: 0;
                    }}
                    .receipt {{
                        box-shadow: none;
                    }}
                }}
            </style>
        </head>
        <body>
            <div class="receipt">
                <!-- Header -->
                <div class="header">
                    <div class="logo">🍔 STACK SHACK</div>
                    <div class="tagline">Premium Fast Food Experience</div>
                    <div class="contact">
                        123 University Ave, Campus District<br>
                        Phone: (555) 123-4567<br>
                        www.stackshack.com
                    </div>
                </div>

                <!-- Transaction Info -->
                <div class="divider"></div>
                <div class="section-title">Transaction Details</div>
                <div class="info-line">
                    <span class="info-label">Receipt #:</span>
                    <span class="info-value">{transaction.transaction_id}</span>
                </div>
                <div class="info-line">
                    <span class="info-label">Order #:</span>
                    <span class="info-value">{order.id}</span>
                </div>
                <div class="info-line">
                    <span class="info-label">Date:</span>
                    <span class="info-value">{transaction.completed_at.strftime('%b %d, %Y %I:%M %p') if transaction.completed_at else 'N/A'}</span>
                </div>
                <div class="info-line">
                    <span class="info-label">Payment:</span>
                    <span class="info-value">{transaction.payment_method.replace('_', ' ').title()}</span>
                </div>
                {f'<div class="info-line"><span class="info-label">Card:</span><span class="info-value">{transaction.masked_card}</span></div>' if transaction.masked_card else ''}
                {f'<div class="info-line"><span class="info-label">Provider:</span><span class="info-value">{transaction.payment_provider.replace("_", " ").title()}</span></div>' if transaction.payment_provider else ''}
                <div style="text-align: center;">
                    <span class="payment-badge">✓ PAID</span>
                </div>
                <div class="divider"></div>

                <!-- Items -->
                <div class="section-title">Order Items</div>
                <table class="items-table">
                    <thead>
                        <tr>
                            <th>Item</th>
                            <th>Qty</th>
                            <th>Amount</th>
                        </tr>
                    </thead>
                    <tbody>
                        {items_html}
                    </tbody>
                </table>

                <!-- Totals -->
                <div class="totals">
                    <div class="total-line">
                        <span>Subtotal:</span>
                        <span>${subtotal:.2f}</span>
                    </div>
                    {f'<div class="total-line"><span>Tax ({tax_rate*100:.1f}%):</span><span>${tax_amount:.2f}</span></div>' if tax_rate > 0 else ''}
                    <div class="grand-total">
                        <span>TOTAL PAID:</span>
                        <span>${total:.2f}</span>
                    </div>
                </div>

                <!-- Barcode -->
                <div class="barcode">*{transaction.transaction_id[-8:]}*</div>

                <!-- Footer -->
                <div class="footer">
                    <p style="font-weight: bold;">Thank you for your order!</p>
                    <p>Keep this receipt for your records</p>
                    <p>support@stackshack.com</p>
                    <p style="font-size: 9px; margin-top: 3mm;">
                        Official Payment Receipt<br>
                        {transaction.completed_at.strftime('%Y-%m-%d %H:%M:%S') if transaction.completed_at else 'N/A'}
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        return html

    @staticmethod
    def get_user_payment_history(user_id, limit=None):
        """
        Get payment history for a user

        Args:
            user_id: User ID
            limit: Optional limit for number of transactions

        Returns:
            tuple: (success, message, transactions)
        """
        try:
            query = Transaction.query.filter_by(user_id=user_id).order_by(
                Transaction.initiated_at.desc()
            )

            if limit:
                query = query.limit(limit)

            transactions = query.all()
            return (
                True,
                "Payment history retrieved",
                [t.to_dict() for t in transactions],
            )

        except Exception as e:
            return False, f"Error retrieving payment history: {str(e)}", []

    @staticmethod
    def get_payment_statistics(user_id=None, filter_period=None):
        """
        Get payment statistics

        Args:
            user_id: Optional user ID to filter by
            filter_period: 'today', 'week', 'month', or None

        Returns:
            dict: Statistics about payments
        """
        try:
            query = Transaction.query

            if user_id:
                query = query.filter_by(user_id=user_id)

            # Apply time filter
            if filter_period:
                now = datetime.utcnow()
                if filter_period == "today":
                    start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
                elif filter_period == "week":
                    start_date = now - timedelta(days=7)
                elif filter_period == "month":
                    start_date = now - timedelta(days=30)
                else:
                    start_date = None

                if start_date:
                    query = query.filter(Transaction.initiated_at >= start_date)

            all_transactions = query.all()

            # Calculate statistics
            total_transactions = len(all_transactions)
            successful = len([t for t in all_transactions if t.status == "success"])
            failed = len([t for t in all_transactions if t.status == "failed"])
            pending = len([t for t in all_transactions if t.status == "pending"])

            total_amount = sum(
                float(t.amount) for t in all_transactions if t.status == "success"
            )

            return {
                "total_transactions": total_transactions,
                "successful": successful,
                "failed": failed,
                "pending": pending,
                "success_rate": (
                    (successful / total_transactions * 100)
                    if total_transactions > 0
                    else 0
                ),
                "total_amount": total_amount,
                "period": filter_period or "all_time",
            }

        except Exception as e:
            return {
                "error": str(e),
                "total_transactions": 0,
                "successful": 0,
                "failed": 0,
                "pending": 0,
            }

    @staticmethod
    def get_receipt(receipt_id, user_id):
        """
        Get receipt by ID

        Args:
            receipt_id: Receipt ID
            user_id: User ID for authorization

        Returns:
            tuple: (success, message, receipt)
        """
        try:
            receipt = Receipt.query.filter_by(id=receipt_id, user_id=user_id).first()

            if not receipt:
                return False, "Receipt not found", None

            return True, "Receipt retrieved", receipt.to_dict()

        except Exception as e:
            return False, f"Error retrieving receipt: {str(e)}", None

    @staticmethod
    def create_campus_card(user_id, initial_balance=100.00):
        """
        Create a dummy campus card for a user

        ELIGIBILITY: User must have a .edu email address (student/faculty verification)

        Args:
            user_id: User ID
            initial_balance: Starting balance

        Returns:
            tuple: (success, message, campus_card)
        """
        try:
            from models.user import User

            # Get user to check eligibility
            user = User.query.get(user_id)
            if not user:
                return False, "User not found", None

            # CHECK ELIGIBILITY: Must have .edu email
            if not user.is_eligible_for_campus_card():
                if not user.email:
                    return (
                        False,
                        "Campus cards are only available to students/faculty. Please add a .edu email to your account.",
                        None,
                    )
                else:
                    return (
                        False,
                        f"Campus cards require a .edu email address. Your email ({user.email}) is not eligible.",
                        None,
                    )

            # Check if user already has a campus card
            existing_card = CampusCard.query.filter_by(user_id=user_id).first()
            if existing_card:
                return False, "User already has a campus card", None

            # Generate unique card number
            import random

            card_number = f"CAMPUS{random.randint(100000, 999999)}"

            campus_card = CampusCard(
                user_id=user_id,
                card_number=card_number,
                balance=initial_balance,
                is_active=True,
            )

            db.session.add(campus_card)
            db.session.commit()

            return True, "Campus card created successfully", campus_card.to_dict()

        except Exception as e:
            db.session.rollback()
            return False, f"Error creating campus card: {str(e)}", None

    @staticmethod
    def get_campus_card(user_id):
        """Get user's campus card"""
        try:
            campus_card = CampusCard.query.filter_by(user_id=user_id).first()
            if not campus_card:
                return False, "No campus card found", None

            return True, "Campus card retrieved", campus_card.to_dict()

        except Exception as e:
            return False, f"Error retrieving campus card: {str(e)}", None

    @staticmethod
    def add_campus_card_balance(user_id, amount):
        """Add balance to campus card via payment processor (credit/debit card)"""
        from decimal import Decimal

        try:
            campus_card = CampusCard.query.filter_by(user_id=user_id).first()
            if not campus_card:
                return False, "No campus card found", None

            # Convert amount to Decimal to match database type
            amount_decimal = Decimal(str(amount))
            campus_card.balance += amount_decimal
            db.session.commit()

            return (
                True,
                f"Added ${amount} to campus card via payment processor",
                campus_card.to_dict(),
            )

        except Exception as e:
            db.session.rollback()
            return False, f"Error adding balance: {str(e)}", None
