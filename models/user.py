from . import db  # Importe db depuis models/__init__.py

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    last_name = db.Column(db.String(50), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    banker_id = db.Column(db.Integer, db.ForeignKey('banker.id'), nullable=True)