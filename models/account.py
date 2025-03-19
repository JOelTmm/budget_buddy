from . import db

class Account(db.Model):
    __tablename__ = 'account'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    balance = db.Column(db.Numeric(15, 2), default=0.00)
    account_name = db.Column(db.String(50))
    transactions = db.relationship('Transaction', backref='account', lazy=True, foreign_keys='Transaction.account_id')