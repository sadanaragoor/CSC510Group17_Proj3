"""
Payment Routes
API endpoints for payment processing
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from controllers.payment_controller import PaymentController
from models.payment import Receipt, Transaction
from models.order import Order

payment_bp = Blueprint("payment", __name__)


@payment_bp.route("/checkout/<int:order_id>", methods=["GET"])
@login_required
def checkout(order_id):
    """
    Display checkout page with payment options
    """
    # Get order details
    order = Order.query.get_or_404(order_id)
    
    # Verify order belongs to current user
    if order.user_id != current_user.id:
        flash("Unauthorized access", "error")
        return redirect(url_for("order.order_history"))
    
    # Check if already paid
    if order.status == "Paid":
        flash("This order has already been paid", "info")
        return redirect(url_for("payment.receipt_view", order_id=order_id))
    
    # Get user's campus card if exists
    success, msg, campus_card = PaymentController.get_campus_card(current_user.id)
    
    return render_template(
        "payment/checkout.html",
        order=order,
        campus_card=campus_card if success else None
    )


@payment_bp.route("/process", methods=["POST"])
@login_required
def process_payment():
    """
    Process payment through dummy gateway
    """
    try:
        # Get form data
        order_id = request.form.get("order_id")
        payment_method = request.form.get("payment_method")
        
        if not order_id or not payment_method:
            flash("Missing payment information", "error")
            return redirect(url_for("order.order_history"))
        
        # Build payment data based on method
        payment_data = {
            "order_id": int(order_id),
            "user_id": current_user.id,
            "amount": request.form.get("amount"),
            "payment_method": payment_method
        }
        
        if payment_method == "card":
            payment_data.update({
                "card_number": request.form.get("card_number"),
                "cvv": request.form.get("cvv"),
                "expiry_month": request.form.get("expiry_month"),
                "expiry_year": request.form.get("expiry_year")
            })
        elif payment_method == "campus_card":
            payment_data.update({
                "campus_card_id": request.form.get("campus_card_id")
            })
        elif payment_method == "wallet":
            payment_data.update({
                "wallet_provider": request.form.get("wallet_provider")
            })
        
        # Process payment
        success, message, transaction = PaymentController.process_payment(payment_data)
        
        if success:
            flash(message, "success")
            return redirect(url_for("payment.payment_success", transaction_id=transaction["id"]))
        else:
            flash(message, "error")
            return redirect(url_for("payment.payment_failed", order_id=order_id))
            
    except Exception as e:
        flash(f"Payment processing error: {str(e)}", "error")
        return redirect(url_for("order.order_history"))


@payment_bp.route("/success/<int:transaction_id>")
@login_required
def payment_success(transaction_id):
    """
    Display payment success page
    """
    transaction = Transaction.query.get_or_404(transaction_id)
    
    # Verify belongs to current user
    if transaction.user_id != current_user.id:
        flash("Unauthorized access", "error")
        return redirect(url_for("order.order_history"))
    
    # Get receipt
    receipt = Receipt.query.filter_by(transaction_id=transaction.id).first()
    
    return render_template(
        "payment/success.html",
        transaction=transaction,
        receipt=receipt
    )


@payment_bp.route("/failed/<int:order_id>")
@login_required
def payment_failed(order_id):
    """
    Display payment failure page
    """
    order = Order.query.get_or_404(order_id)
    
    # Verify belongs to current user
    if order.user_id != current_user.id:
        flash("Unauthorized access", "error")
        return redirect(url_for("order.order_history"))
    
    # Get last failed transaction
    transaction = Transaction.query.filter_by(
        order_id=order_id,
        status="failed"
    ).order_by(Transaction.initiated_at.desc()).first()
    
    return render_template(
        "payment/failed.html",
        order=order,
        transaction=transaction
    )


@payment_bp.route("/history")
@login_required
def payment_history():
    """
    Display user's payment history
    """
    success, msg, transactions = PaymentController.get_user_payment_history(current_user.id)
    
    if not success:
        flash(msg, "error")
        transactions = []
    
    # Get statistics
    stats = PaymentController.get_payment_statistics(user_id=current_user.id)
    
    return render_template(
        "payment/history.html",
        transactions=transactions,
        stats=stats
    )


@payment_bp.route("/receipt/<int:receipt_id>")
@login_required
def view_receipt(receipt_id):
    """
    Display receipt (HTML version)
    """
    receipt = Receipt.query.get_or_404(receipt_id)
    
    # Verify belongs to current user
    if receipt.user_id != current_user.id:
        flash("Unauthorized access", "error")
        return redirect(url_for("payment.payment_history"))
    
    # Return the HTML receipt directly
    if receipt.receipt_html:
        return receipt.receipt_html
    else:
        flash("Receipt not available", "error")
        return redirect(url_for("payment.payment_history"))


@payment_bp.route("/receipt/<int:receipt_id>/download")
@login_required
def download_receipt(receipt_id):
    """
    Download receipt as PDF
    """
    from flask import Response
    import io
    
    receipt = Receipt.query.get_or_404(receipt_id)
    
    # Verify belongs to current user
    if receipt.user_id != current_user.id:
        flash("Unauthorized access", "error")
        return redirect(url_for("payment.payment_history"))
    
    if not receipt.receipt_html:
        flash("Receipt not available", "error")
        return redirect(url_for("payment.payment_history"))
    
    try:
        # Try to use weasyprint for better PDF quality
        try:
            from weasyprint import HTML
            pdf_bytes = HTML(string=receipt.receipt_html).write_pdf()
        except ImportError:
            # Fallback to xhtml2pdf if weasyprint not available
            try:
                from xhtml2pdf import pisa
                pdf_buffer = io.BytesIO()
                pisa_status = pisa.CreatePDF(
                    io.BytesIO(receipt.receipt_html.encode('utf-8')),
                    dest=pdf_buffer
                )
                if pisa_status.err:
                    raise Exception("PDF generation failed")
                pdf_bytes = pdf_buffer.getvalue()
            except ImportError:
                # Final fallback: simple text-based PDF using reportlab
                from reportlab.lib.pagesizes import letter
                from reportlab.pdfgen import canvas
                from reportlab.lib.units import inch
                
                buffer = io.BytesIO()
                p = canvas.Canvas(buffer, pagesize=letter)
                width, height = letter
                
                # Simple receipt layout
                p.setFont("Helvetica-Bold", 20)
                p.drawString(1*inch, height - 1*inch, "Stack Shack")
                p.setFont("Helvetica-Bold", 16)
                p.drawString(1*inch, height - 1.5*inch, "Payment Receipt")
                
                p.setFont("Helvetica", 12)
                y = height - 2*inch
                p.drawString(1*inch, y, f"Receipt Number: {receipt.receipt_number}")
                y -= 0.3*inch
                p.drawString(1*inch, y, f"Order ID: {receipt.order_id}")
                y -= 0.3*inch
                p.drawString(1*inch, y, f"Amount: ${float(receipt.total_amount):.2f}")
                y -= 0.3*inch
                p.drawString(1*inch, y, f"Payment Method: {receipt.payment_method}")
                y -= 0.3*inch
                p.drawString(1*inch, y, f"Date: {receipt.generated_at}")
                
                p.save()
                pdf_bytes = buffer.getvalue()
        
        # Create response with PDF
        response = Response(pdf_bytes, mimetype='application/pdf')
        response.headers['Content-Disposition'] = f'attachment; filename=receipt_{receipt.receipt_number}.pdf'
        return response
        
    except Exception as e:
        flash(f"Error generating PDF: {str(e)}", "error")
        return redirect(url_for("payment.payment_history"))


@payment_bp.route("/receipt/order/<int:order_id>")
@login_required
def receipt_view(order_id):
    """
    View receipt by order ID
    """
    order = Order.query.get_or_404(order_id)
    
    # Verify belongs to current user
    if order.user_id != current_user.id:
        flash("Unauthorized access", "error")
        return redirect(url_for("order.order_history"))
    
    receipt = Receipt.query.filter_by(order_id=order_id).first()
    
    if not receipt:
        flash("No receipt found for this order", "error")
        return redirect(url_for("order.order_history"))
    
    # Return the HTML receipt directly
    if receipt.receipt_html:
        return receipt.receipt_html
    else:
        flash("Receipt not available", "error")
        return redirect(url_for("order.order_history"))


@payment_bp.route("/receipt/order/<int:order_id>/download")
@login_required
def download_receipt_by_order(order_id):
    """
    Download receipt as PDF by order ID
    """
    order = Order.query.get_or_404(order_id)
    
    # Verify belongs to current user
    if order.user_id != current_user.id:
        flash("Unauthorized access", "error")
        return redirect(url_for("order.order_history"))
    
    receipt = Receipt.query.filter_by(order_id=order_id).first()
    
    if not receipt:
        flash("No receipt found for this order", "error")
        return redirect(url_for("order.order_history"))
    
    # Redirect to main download endpoint
    return download_receipt(receipt.id)


# Campus Card Management Routes

@payment_bp.route("/campus-card/create", methods=["POST"])
@login_required
def create_campus_card():
    """
    Create a campus card for the user
    """
    success, msg, campus_card = PaymentController.create_campus_card(current_user.id)
    
    flash(msg, "success" if success else "error")
    return redirect(url_for("payment.campus_card_info"))


@payment_bp.route("/campus-card/info")
@login_required
def campus_card_info():
    """
    Display campus card information
    """
    success, msg, campus_card = PaymentController.get_campus_card(current_user.id)
    
    return render_template(
        "payment/campus_card.html",
        campus_card=campus_card if success else None
    )


@payment_bp.route("/campus-card/add-balance", methods=["GET"])
@login_required
def add_campus_card_balance():
    """
    Show form to add balance to campus card via credit/debit card payment
    """
    success, msg, campus_card = PaymentController.get_campus_card(current_user.id)
    
    if not success:
        flash("Campus card not found", "error")
        return redirect(url_for("payment.campus_card_info"))
    
    return render_template(
        "payment/add_balance.html",
        campus_card=campus_card
    )


@payment_bp.route("/campus-card/process-balance-addition", methods=["POST"])
@login_required
def process_balance_addition():
    """
    Process payment to add balance to campus card
    """
    try:
        # Get form data
        amount = float(request.form.get("amount", 0))
        campus_card_id = request.form.get("campus_card_id")
        card_number = request.form.get("card_number")
        cvv = request.form.get("cvv")
        expiry_month = request.form.get("expiry_month")
        expiry_year = request.form.get("expiry_year")
        
        # Validate amount
        if amount <= 0 or amount > 1000:
            flash("Amount must be between $1 and $1,000", "error")
            return redirect(url_for("payment.add_campus_card_balance"))
        
        # Verify campus card belongs to user
        success, msg, campus_card = PaymentController.get_campus_card(current_user.id)
        if not success or str(campus_card["id"]) != str(campus_card_id):
            flash("Invalid campus card", "error")
            return redirect(url_for("payment.campus_card_info"))
        
        # Process payment through gateway (simulate card payment)
        from services.payment_gateway import PaymentGatewayService
        gateway = PaymentGatewayService(simulation_mode="random_90")
        
        payment_request = {
            "order_id": 0,  # Not tied to an order
            "user_id": current_user.id,
            "amount": amount,
            "payment_method": "card",
            "card_number": card_number,
            "cvv": cvv,
            "expiry_month": expiry_month,
            "expiry_year": expiry_year
        }
        
        payment_response = gateway.process_payment(payment_request)
        
        if payment_response["success"]:
            # Payment successful - now add balance to campus card
            success, msg, updated_card = PaymentController.add_campus_card_balance(
                current_user.id,
                amount
            )
            
            if success:
                flash(f"✅ Successfully added ${amount:.2f} to your campus card!", "success")
            else:
                flash(f"Payment processed but failed to add balance: {msg}", "error")
        else:
            # Payment failed
            flash(f"❌ Payment failed: {payment_response.get('failure_reason', 'Unknown error')}", "error")
            return redirect(url_for("payment.add_campus_card_balance"))
        
    except ValueError:
        flash("Invalid amount entered", "error")
        return redirect(url_for("payment.add_campus_card_balance"))
    except Exception as e:
        flash(f"Error processing payment: {str(e)}", "error")
        return redirect(url_for("payment.add_campus_card_balance"))
    
    return redirect(url_for("payment.campus_card_info"))


# Staff/Admin Dashboard Routes

@payment_bp.route("/admin/dashboard")
@login_required
def admin_dashboard():
    """
    Payment dashboard for staff/admin
    """
    # Check if user is staff/admin
    if current_user.role not in ["staff", "admin"]:
        flash("Unauthorized access", "error")
        return redirect(url_for("home"))
    
    # Get filter period from query params
    filter_period = request.args.get("period", "today")
    
    # Get statistics
    stats = PaymentController.get_payment_statistics(filter_period=filter_period)
    
    # Get recent transactions
    query = Transaction.query.order_by(Transaction.initiated_at.desc())
    
    # Apply time filter
    if filter_period:
        from datetime import datetime, timedelta
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
    
    transactions = query.limit(50).all()
    
    return render_template(
        "payment/admin_dashboard.html",
        stats=stats,
        transactions=transactions,
        filter_period=filter_period
    )


# API Endpoints (JSON)

@payment_bp.route("/api/simulate-wallet", methods=["POST"])
@login_required
def simulate_wallet_redirect():
    """
    Simulate wallet provider redirect/authentication
    """
    data = request.get_json()
    wallet_provider = data.get("wallet_provider")
    
    # Simulate 2 second redirect
    import time
    time.sleep(2)
    
    # Randomly succeed or fail
    import random
    success = random.random() < 0.95
    
    if success:
        return jsonify({
            "success": True,
            "message": f"{wallet_provider.upper()} authentication successful",
            "auth_token": f"WALLET_{wallet_provider.upper()}_{random.randint(1000, 9999)}"
        })
    else:
        return jsonify({
            "success": False,
            "message": "Wallet authentication failed"
        }), 400


@payment_bp.route("/api/simulate-otp", methods=["POST"])
@login_required
def simulate_otp():
    """
    Simulate OTP verification for card payments
    """
    data = request.get_json()
    otp = data.get("otp")
    
    # Simulate 1 second verification
    import time
    time.sleep(1)
    
    # Accept any 6-digit OTP
    if otp and len(str(otp)) == 6:
        return jsonify({
            "success": True,
            "message": "OTP verified successfully"
        })
    else:
        return jsonify({
            "success": False,
            "message": "Invalid OTP"
        }), 400

