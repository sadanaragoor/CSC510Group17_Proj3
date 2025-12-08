from flask import Flask, render_template, redirect, url_for
from routes.surprise_routes import surprise_bp
from config import config
from database.db import init_db, login_manager, db
from routes.auth_routes import auth_bp
from routes.menu_routes import menu_bp
from routes.order_routes import order_bp
from routes.status_routes import status_bp
from routes.payment_routes import payment_bp
from routes.profile_routes import profile_bp
from routes.gamification_routes import gamification_bp
from routes.shift_routes import shift_bp
from models.user import User
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


def create_app(config_name="development"):
    """
    Factory function for creating and configuring the Flask application instance.
    ...
    """
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    init_db(app)

    # Import all models to ensure they're registered with SQLAlchemy
    # This ensures db.create_all() will create all tables
    from models.menu_item import MenuItem  # noqa: F401
    from models.order import Order, OrderItem  # noqa: F401
    from models.payment import (  # noqa: F401
        Transaction,
        PaymentMethod,
        CampusCard,
        Receipt,
    )
    from models.gamification import (  # noqa: F401
        PointsTransaction,
        Badge,
        UserBadge,
        DailyBonus,
        WeeklyChallenge,
        UserChallengeProgress,
        PunchCard,
        Redemption,
        Coupon,
    )
    from models.shift import StaffProfile, Shift, ShiftAssignment  # noqa: F401

    app.config["TEMPLATES_AUTO_RELOAD"] = True
    app.jinja_env.auto_reload = True
    app.jinja_env.cache = {}

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(menu_bp, url_prefix="/menu")
    app.register_blueprint(order_bp, url_prefix="/orders")
    app.register_blueprint(status_bp, url_prefix="/status")
    app.register_blueprint(payment_bp, url_prefix="/payment")
    app.register_blueprint(profile_bp, url_prefix="/profile")
    app.register_blueprint(surprise_bp, url_prefix="/surprisebox")
    app.register_blueprint(gamification_bp, url_prefix="/gamification")
    app.register_blueprint(shift_bp, url_prefix="/shifts")

    @app.context_processor
    def inject_current_year():
        return {"current_year": datetime.now().year}

    @app.route("/")
    def home():
        return render_template("home.html")

    @app.route("/menu")
    def menu():
        from flask_login import current_user

        # Redirect to dashboard if logged in, otherwise to home
        if current_user.is_authenticated:
            return redirect(url_for("auth.dashboard"))
        return redirect(url_for("home"))

    return app


if __name__ == "__main__":
    app = create_app("development")
    with app.app_context():
        # This creates all tables from your models if they don't exist
        # (models are imported in create_app)
        db.create_all()
        print("Database tables checked/created.")
    app.run(debug=True, host="0.0.0.0", port=5000)  # nosec B104 B201
