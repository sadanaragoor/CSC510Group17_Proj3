from database.db import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


class User(UserMixin, db.Model):
    """
    User model class representing a user in the Stack Shack application.
    Inherits from UserMixin for Flask-Login integration.
    """

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), nullable=False, default="customer")
    pref_vegan = db.Column(db.Boolean, default=False)
    pref_gluten_free = db.Column(db.Boolean, default=False)
    pref_high_protein = db.Column(db.Boolean, default=False)
    pref_low_calorie = db.Column(db.Boolean, default=False)

    def set_password(self, password):
        """
        Hashes the plaintext password and stores it in the password column.

        Args:
            password (str): The plaintext password.
        """
        self.password = generate_password_hash(password)

    def check_password(self, password):
        """
        Compares a plaintext password against the stored hash.

        Args:
            password (str): The plaintext password to check.

        Returns:
            bool: True if the password matches the hash, False otherwise.
        """
        return check_password_hash(self.password, password)

    @staticmethod
    def get_by_username(username):
        """
        Retrieves a User object by their username.

        Args:
            username (str): The username to search for.

        Returns:
            User or None: The User object if found, otherwise None.
        """
        return User.query.filter_by(username=username).first()
