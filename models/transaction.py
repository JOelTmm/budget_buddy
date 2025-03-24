from . import db


class Transaction(db.Model):
    """Represents a financial transaction in the database."""

    __tablename__ = 'transaction'

    id = db.Column(db.Integer, primary_key=True)  # Unique identifier for the transaction
    reference = db.Column(db.String(50), unique=True, nullable=False)  # Unique transaction reference
    description = db.Column(db.Text)  # Optional description of the transaction
    amount = db.Column(db.Numeric(15, 2), nullable=False)  # Transaction amount
    transaction_date = db.Column(db.DateTime, default=db.func.current_timestamp())  
    # Date and time of the transaction, defaults to current timestamp
    transaction_type = db.Column(
        db.Enum('withdrawal', 'deposit', 'transfer'), nullable=False
    )  # Type of transaction (withdrawal, deposit, or transfer)
    account_id = db.Column(db.Integer, db.ForeignKey('account.id'), nullable=False)  
    # Foreign key linking to the related account
    category = db.Column(db.String(50))  # Optional category for the transaction
    destination_account_id = db.Column(
        db.Integer, db.ForeignKey('account.id'), nullable=True
    )  # Foreign key for destination account in case of transfer
