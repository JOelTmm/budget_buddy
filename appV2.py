from flask import Flask
from Config import Config
from models import db
from models.user import User
from models.account import Account
from models.transaction import Transaction
from models.banker import Banker
from flask_bcrypt import Bcrypt
import jwt
from datetime import datetime, timedelta
import re
from decimal import Decimal

# Initialisation de Flask
app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
bcrypt = Bcrypt(app)

# Fonctions utilitaires
def validate_password(password):
    pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*])[A-Za-z\d!@#$%^&*]{10,}$"
    return re.match(pattern, password) is not None

def token_required(func):
    def wrapper(token, *args, **kwargs):
        if not token:
            return {'error': 'Token is missing'}, 401
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_id = data.get('user_id') or data.get('banker_id')
            role = data['role']
        except Exception as e:
            return {'error': f'Invalid token: {str(e)}'}, 401
        return func(current_id, role, *args, **kwargs)
    return wrapper

# Fonctions métier
def register_user(last_name, first_name, email, password):
    if not validate_password(password):
        return {'error': 'Password must be at least 10 characters with 1 uppercase, 1 lowercase, 1 digit, and 1 special character'}, 400
    hashed_pwd = bcrypt.generate_password_hash(password).decode('utf-8')
    user = User(last_name=last_name, first_name=first_name, email=email, password=hashed_pwd)
    db.session.add(user)
    db.session.commit()
    return {'message': 'User created', 'id': user.id}, 201

def login_user(email, password):
    user = db.session.get(User, db.session.query(User.id).filter_by(email=email).scalar())
    if user and bcrypt.check_password_hash(user.password, password):
        token = jwt.encode({'user_id': user.id, 'role': 'user', 'exp': datetime.utcnow() + timedelta(hours=24)}, app.config['SECRET_KEY'], algorithm='HS256')
        return {'token': token}, 200
    return {'error': 'Invalid credentials'}, 401

def create_account(token, account_name):
    result, status = token_required(lambda current_id, role: (
        {'error': 'Only users can create accounts'}, 403) if role != 'user' else (
            create_account_with_id(current_id, account_name)
    ))(token)
    return result, status

def create_account_with_id(current_id, account_name):
    account = Account(user_id=current_id, balance=Decimal('0.00'), account_name=account_name)
    db.session.add(account)
    db.session.commit()
    return {'message': 'Account created', 'id': account.id}, 201

def add_transaction(token, account_id, reference, description, amount, transaction_type, category, destination_account_id=None):
    result, status = token_required(lambda current_id, role: (
        execute_transaction(current_id, role, account_id, reference, description, amount, transaction_type, category, destination_account_id)
    ))(token)
    return result, status

def execute_transaction(current_id, role, account_id, reference, description, amount, transaction_type, category, destination_account_id):
    account = db.session.get(Account, account_id)
    if not account or (role == 'user' and account.user_id != current_id):
        return {'error': 'Account not found or unauthorized'}, 404
    
    amount = Decimal(str(amount))
    if transaction_type == 'deposit':
        new_balance = account.balance + amount
    elif transaction_type == 'withdrawal':
        if account.balance < amount:
            return {'error': 'Insufficient balance'}, 400
        new_balance = account.balance - amount
    elif transaction_type == 'transfer':
        dest_account = db.session.get(Account, destination_account_id)
        if not dest_account:
            return {'error': 'Destination account not found'}, 404
        if account.balance < amount:
            return {'error': 'Insufficient balance'}, 400
        new_balance = account.balance - amount
        dest_account_new_balance = dest_account.balance + amount
    else:
        return {'error': 'Invalid transaction type'}, 400

    if transaction_type == 'deposit' or transaction_type == 'withdrawal':
        account.balance = new_balance
    elif transaction_type == 'transfer':
        account.balance = new_balance
        dest_account.balance = dest_account_new_balance

    transaction = Transaction(
        reference=reference,
        description=description,
        amount=amount,
        transaction_type=transaction_type,
        account_id=account.id,
        category=category,
        destination_account_id=destination_account_id if transaction_type == 'transfer' else None
    )
    db.session.add(transaction)
    db.session.commit()
    return {'message': f'{transaction_type.capitalize()} successful', 'balance': float(account.balance)}, 201

def get_transactions(token, account_id, type_filter=None, category=None, start_date=None, end_date=None, sort=None):
    result, status = token_required(lambda current_id, role: (
        execute_get_transactions(current_id, role, account_id, type_filter, category, start_date, end_date, sort)
    ))(token)
    return result, status

def execute_get_transactions(current_id, role, account_id, type_filter, category, start_date, end_date, sort):
    if not account_id:
        return {'error': 'account_id is required'}, 400
    if role == 'user':
        account = db.session.get(Account, account_id)
        if not account or account.user_id != current_id:
            return {'error': 'Account not found or unauthorized'}, 404
    
    query = Transaction.query.filter_by(account_id=account_id) if role == 'user' else Transaction.query
    if type_filter:
        query = query.filter_by(transaction_type=type_filter)
    if category:
        query = query.filter_by(category=category)
    if start_date:
        query = query.filter(Transaction.transaction_date >= start_date)
    if end_date:
        query = query.filter(Transaction.transaction_date <= end_date)
    if sort:
        query = query.order_by(Transaction.amount.asc() if sort == 'asc' else Transaction.amount.desc())

    transactions = query.all()
    return [{
        'id': t.id,
        'reference': t.reference,
        'description': t.description,
        'amount': float(t.amount),
        'date': t.transaction_date.isoformat(),
        'type': t.transaction_type,
        'category': t.category,
        'destination_account_id': t.destination_account_id if t.transaction_type == 'transfer' else None
    } for t in transactions], 200

def get_dashboard(token, period='month'):
    result, status = token_required(lambda current_id, role: (
        execute_dashboard(current_id, role, period)
    ))(token)
    return result, status

def execute_dashboard(current_id, role, period):
    accounts = Account.query.filter_by(user_id=current_id).all() if role == 'user' else Account.query.all()
    if not accounts:
        return {'error': 'No accounts found'}, 404

    if period == 'week':
        start_date = datetime.now() - timedelta(days=7)
    elif period == 'month':
        start_date = datetime.now().replace(day=1)
    else:
        start_date = datetime.now() - timedelta(days=30)

    total_balance = sum(float(acc.balance) for acc in accounts)
    deposits = db.session.query(db.func.sum(Transaction.amount)).filter(
        Transaction.transaction_type == 'deposit',
        Transaction.account_id.in_([acc.id for acc in accounts]),
        Transaction.transaction_date >= start_date
    ).scalar() or 0.0
    withdrawals = db.session.query(db.func.sum(Transaction.amount)).filter(
        Transaction.transaction_type == 'withdrawal',
        Transaction.account_id.in_([acc.id for acc in accounts]),
        Transaction.transaction_date >= start_date
    ).scalar() or 0.0
    transfers_out = db.session.query(db.func.sum(Transaction.amount)).filter(
        Transaction.transaction_type == 'transfer',
        Transaction.account_id.in_([acc.id for acc in accounts]),
        Transaction.transaction_date >= start_date
    ).scalar() or 0.0
    
    alerts = [f"Low balance in {acc.account_name} ({float(acc.balance)})" for acc in accounts if float(acc.balance) < 100] or ['All good!']

    return {
        'total_balance': total_balance,
        'period': period,
        'summary': {'deposits': float(deposits), 'withdrawals': float(withdrawals), 'transfers_out': float(transfers_out)},
        'accounts': [{'id': acc.id, 'name': acc.account_name, 'balance': float(acc.balance)} for acc in accounts],
        'alerts': alerts
    }, 200

def get_balance(token, account_id):
    result, status = token_required(lambda current_id, role: (
        execute_get_balance(current_id, role, account_id)
    ))(token)
    return result, status

def execute_get_balance(current_id, role, account_id):
    account = db.session.get(Account, account_id)
    if not account or (role == 'user' and account.user_id != current_id):
        return {'error': 'Account not found or unauthorized'}, 404
    return {'account_id': account.id, 'name': account.account_name, 'balance': float(account.balance)}, 200

def list_accounts(token):
    result, status = token_required(lambda current_id, role: (
        {'accounts': [{'id': acc.id, 'name': acc.account_name, 'balance': float(acc.balance)} for acc in Account.query.filter_by(user_id=current_id).all()]}, 200
    ))(token)
    return result, status

# Interface console
def main():
    with app.app_context():
        db.create_all()
        print("Welcome to Budget Buddy Console App!")
        print("Commands: register, login, exit")
        token = None
        
        while True:
            cmd = input("> ").strip()
            if not cmd:
                continue
            parts = cmd.split()
            action = parts[0].lower()

            if action == 'exit':
                print("Goodbye!")
                break
            elif action == 'register':
                last_name = input("Last Name: ")
                first_name = input("First Name: ")
                email = input("Email: ")
                password = input("Password: ")
                result, status = register_user(last_name, first_name, email, password)
                print(f"[{status}] {result}")
            elif action == 'login':
                email = input("Email: ")
                password = input("Password: ")
                result, status = login_user(email, password)
                if status == 200:
                    token = result['token']  # Stocke le token sans l'afficher
                    print("[200] Login successful")
                    logged_in_menu(token)  # Passe au menu connecté
                else:
                    print(f"[{status}] {result}")
            else:
                print("Unknown command. Use: register, login, exit")

def logged_in_menu(token):
    while True:
        print("\nLogged-in Menu:")
        print("1. View Account Balance")
        print("2. Make a Transaction")
        print("3. View Dashboard")
        print("4. Create a New Account")
        print("5. Logout")
        choice = input("Choose an option (1-5): ").strip()

        # Lister les comptes avant chaque action nécessitant un account_id
        accounts_result, status = list_accounts(token)
        if status == 200 and accounts_result['accounts']:
            print("\nYour Accounts:")
            for acc in accounts_result['accounts']:
                print(f"ID: {acc['id']}, Name: {acc['name']}, Balance: {acc['balance']}")
        else:
            print("\nNo accounts found. Create one first!")

        if choice == '1':
            account_id = input("Account ID: ")
            result, status = get_balance(token, account_id)
            print(f"[{status}] {result}")
        elif choice == '2':
            transaction_type = input("Transaction type (deposit/withdrawal/transfer): ").lower()
            account_id = input("Account ID: ")
            reference = input("Reference: ")
            description = input("Description: ")
            amount = input("Amount: ")
            category = input("Category: ")
            dest_account_id = input("Destination Account ID (for transfer, otherwise leave blank): ") or None
            result, status = add_transaction(token, account_id, reference, description, amount, transaction_type, category, dest_account_id)
            print(f"[{status}] {result}")
        elif choice == '3':
            period = input("Period (week/month, default month): ") or 'month'
            result, status = get_dashboard(token, period)
            print(f"[{status}] {result}")
        elif choice == '4':
            account_name = input("Account Name: ")
            result, status = create_account(token, account_name)
            print(f"[{status}] {result}")
        elif choice == '5':
            print("Logged out successfully")
            break
        else:
            print("Invalid choice. Please select 1, 2, 3, 4, or 5.")

if __name__ == '__main__':
    main()