from . import db

class Account(db.Model):
    """
    Represents a bank account associated with a user.
    """
    __tablename__ = 'account'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Foreign key linking to the user
    balance = db.Column(db.Numeric(15, 2), default=0.00)  # Account balance with precision
    account_name = db.Column(db.String(50))  # Name of the account
    
    # Relationship with transactions
    transactions = db.relationship(
        'Transaction', backref='account', lazy=True, foreign_keys='Transaction.account_id'
    )
