from . import db


class Banker(db.Model):
    """Represents a banker entity in the database."""

    __tablename__ = 'banker'

    id = db.Column(db.Integer, primary_key=True)  # Unique identifier for the banker
    last_name = db.Column(db.String(50), nullable=False)  # Banker's last name
    first_name = db.Column(db.String(50), nullable=False)  # Banker's first name
    email = db.Column(db.String(100), unique=True, nullable=False)  # Unique email for authentication
    password = db.Column(db.String(255), nullable=False)  # Hashed password for security
