from . import db

class Transaction(db.Model):
    __tablename__ = 'transaction'
    id = db.Column(db.Integer, primary_key=True)
    reference = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text)
    amount = db.Column(db.Numeric(15, 2), nullable=False)
    transaction_date = db.Column(db.DateTime, default=db.func.current_timestamp())
    transaction_type = db.Column(db.Enum('withdrawal', 'deposit', 'transfer'), nullable=False)
    account_id = db.Column(db.Integer, db.ForeignKey('account.id'), nullable=False)
    category = db.Column(db.String(50))
    destination_account_id = db.Column(db.Integer, db.ForeignKey('account.id'), nullable=True)