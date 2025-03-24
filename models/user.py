from . import db  # Import db from models/__init__.py


class User(db.Model):
    """Represents a user in the system."""

    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)  # Unique identifier for the user
    last_name = db.Column(db.String(50), nullable=False)  # User's last name
    first_name = db.Column(db.String(50), nullable=False)  # User's first name
    email = db.Column(db.String(100), unique=True, nullable=False)  # User's unique email address
    password = db.Column(db.String(255), nullable=False)  # Hashed password for authentication
    banker_id = db.Column(db.Integer, db.ForeignKey('banker.id'), nullable=True)  
    # Foreign key linking the user to a banker (if applicable)
