from . import db  # Importe db depuis models/__init__.py

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    last_name = db.Column(db.String(50), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    creation_date = db.Column(db.DateTime, default=db.func.current_timestamp())
    accounts = db.relationship('Account', backref='user', lazy=True)