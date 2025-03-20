from flask import Flask, request, jsonify
from Config import Config
from models import db
from models.user import User
from models.account import Account
from models.transaction import Transaction
from models.banker import Banker  # Import ajouté pour résoudre l'erreur Pylance
from flask_bcrypt import Bcrypt
import jwt
import re
from datetime import datetime, timedelta
from functools import wraps
from decimal import Decimal

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
bcrypt = Bcrypt(app)

# Middleware pour vérifier le token JWT
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        print(f"Received: {token}")
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        try:
            token = token.split(" ")[1]
            print(f"Parsed token: {token}")
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            print(f"Decoded: {data}")
            current_id = data.get('user_id') or data.get('banker_id')
            role = data['role']
        except Exception as e:
            print(f"Token error: {str(e)}")
            return jsonify({'error': 'Invalid token'}), 401
        return f(current_id, role, *args, **kwargs)
    return decorated

# Validation du mot de passe
def validate_password(password):
    pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*])[A-Za-z\d!@#$%^&*]{10,}$"
    return re.match(pattern, password) is not None

# Routes pour User
@app.route('/api/user/register', methods=['POST'])
def register_user():
    data = request.get_json()
    if not validate_password(data['password']):
        return jsonify({'error': 'Password must be at least 10 characters with 1 uppercase, 1 lowercase, 1 digit, and 1 special character'}), 400
    hashed_pwd = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    user = User(
        last_name=data['last_name'],
        first_name=data['first_name'],
        email=data['email'],
        password=hashed_pwd
    )
    db.session.add(user)
    db.session.commit()
    return jsonify({'message': 'User created', 'id': user.id}), 201

@app.route('/api/user/login', methods=['POST'])
def login_user():
    data = request.get_json()
    user = User.query.filter_by(email=data['email']).first()
    if user and bcrypt.check_password_hash(user.password, data['password']):
        token = jwt.encode({'user_id': user.id, 'role': 'user', 'exp': datetime.utcnow() + timedelta(hours=24)}, app.config['Pipes606&'], algorithm='HS256')
        return jsonify({'token': token})
    return jsonify({'error': 'Invalid credentials'}), 401

# Routes pour Banker
@app.route('/api/banker/register', methods=['POST'])
def register_banker():
    data = request.get_json()
    if not validate_password(data['password']):
        return jsonify({'error': 'Password must be at least 10 characters with 1 uppercase, 1 lowercase, 1 digit, and 1 special character'}), 400
    hashed_pwd = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    banker = Banker(
        last_name=data['last_name'],
        first_name=data['first_name'],
        email=data['email'],
        password=hashed_pwd
    )
    db.session.add(banker)
    db.session.commit()
    return jsonify({'message': 'Banker created', 'id': banker.id}), 201

@app.route('/api/banker/login', methods=['POST'])
def login_banker():
    data = request.get_json()
    banker = Banker.query.filter_by(email=data['email']).first()
    if banker and bcrypt.check_password_hash(banker.password, data['password']):
        token = jwt.encode({'banker_id': banker.id, 'role': 'banker', 'exp': datetime.utcnow() + timedelta(hours=24)}, app.config['Pipes606&'], algorithm='HS256')
        return jsonify({'token': token})
    return jsonify({'error': 'Invalid credentials'}), 401

# Route pour créer un compte
@app.route('/api/account/create', methods=['POST'])
@token_required
def create_account(current_id, role):
    if role != 'user':
        return jsonify({'error': 'Only users can create accounts'}), 403
    data = request.get_json()
    account = Account(
        user_id=current_id,
        balance=Decimal('0.00'),
        account_name=data.get('account_name', 'Default Account')
    )
    db.session.add(account)
    db.session.commit()
    return jsonify({'message': 'Account created', 'id': account.id}), 201

# Route pour ajouter une transaction
@app.route('/api/transaction', methods=['POST'])
@token_required
def add_transaction(current_id, role):
    data = request.get_json()
    account = db.session.get(Account, data['account_id'])
    if not account or (role == 'user' and account.user_id != current_id):
        return jsonify({'error': 'Account not found or unauthorized'}), 404
    
    transaction_type = data['type']
    amount = Decimal(str(data['amount']))
    
    # Vérifications préalables sans modifier la base
    if transaction_type == 'deposit':
        new_balance = account.balance + amount
    elif transaction_type == 'withdrawal':
        if account.balance < amount:
            return jsonify({'error': 'Insufficient balance'}), 400
        new_balance = account.balance - amount
    elif transaction_type == 'transfer':
        dest_account = db.session.get(Account, data['destination_account_id'])
        if not dest_account:
            return jsonify({'error': 'Destination account not found'}), 404
        if account.balance < amount:
            return jsonify({'error': 'Insufficient balance'}), 400
        new_balance = account.balance - amount
        dest_account_new_balance = dest_account.balance + amount
    else:
        return jsonify({'error': 'Invalid transaction type'}), 400

    # Appliquer les modifications seulement si toutes les vérifications passent
    if transaction_type == 'deposit' or transaction_type == 'withdrawal':
        account.balance = new_balance
    elif transaction_type == 'transfer':
        account.balance = new_balance
        dest_account.balance = dest_account_new_balance

    # Créer la transaction
    transaction = Transaction(
        reference=data['reference'],
        description=data.get('description'),
        amount=amount,
        transaction_type=transaction_type,
        account_id=account.id,
        category=data.get('category'),
        destination_account_id=data.get('destination_account_id') if transaction_type == 'transfer' else None
    )
    
    # Ajouter et valider les changements
    db.session.add(transaction)
    db.session.commit()
    
    return jsonify({
        'message': f'{transaction_type.capitalize()} successful',
        'balance': float(account.balance)
    }), 201

# Route pour récupérer l'historique des transactions
@app.route('/api/transactions', methods=['GET'])
@token_required
def transaction_history(current_id, role):
    account_id = request.args.get('account_id')
    if not account_id:
        return jsonify({'error': 'account_id is required'}), 400
    
    if role == 'user':
        account = db.session.get(Account, account_id)
        if not account or account.user_id != current_id:
            return jsonify({'error': 'Account not found or unauthorized'}), 404
    
    # Construire la requête
    query = Transaction.query.filter_by(account_id=account_id) if role == 'user' else Transaction.query

    # Appliquer les filtres
    if 'type' in request.args:
        query = query.filter_by(transaction_type=request.args['type'])
    if 'category' in request.args:
        query = query.filter_by(category=request.args['category'])
    if 'start_date' in request.args:
        query = query.filter(Transaction.transaction_date >= request.args['start_date'])
    if 'end_date' in request.args:
        query = query.filter(Transaction.transaction_date <= request.args['end_date'])
    if 'sort' in request.args:
        query = query.order_by(Transaction.amount.asc() if request.args['sort'] == 'asc' else Transaction.amount.desc())

    # Récupérer les transactions
    transactions = query.all()
    
    # Formater la réponse
    return jsonify([{
        'id': t.id,
        'reference': t.reference,
        'description': t.description,
        'amount': float(t.amount),
        'date': t.transaction_date.isoformat(),
        'type': t.transaction_type,
        'category': t.category,
        'destination_account_id': t.destination_account_id if t.transaction_type == 'transfer' else None
    } for t in transactions]), 200

# Route pour le tableau de bord

@app.route('/api/dashboard', methods=['GET'])
@token_required
def dashboard(current_id, role):
    # Récupérer les comptes
    accounts = Account.query.filter_by(user_id=current_id).all() if role == 'user' else Account.query.all()
    if not accounts:
        return jsonify({'error': 'No accounts found'}), 404

    # Paramètre période (optionnel, défaut : dernier mois)
    period = request.args.get('period', 'month')
    if period == 'week':
        start_date = datetime.now() - timedelta(days=7)
    elif period == 'month':
        start_date = datetime.now().replace(day=1)
    else:
        start_date = datetime.now() - timedelta(days=30)  # Défaut

    # Calculs
    total_balance = sum(float(acc.balance) for acc in accounts)
    
    # Récapitulatif des transactions par type
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
    
    # Alertes spécifiques
    alerts = [
        f"Low balance in {acc.account_name} ({float(acc.balance)})" 
        for acc in accounts if float(acc.balance) < 100
    ] or ['All good!']

    return jsonify({
        'total_balance': total_balance,
        'period': period,
        'summary': {
            'deposits': float(deposits),
            'withdrawals': float(withdrawals),
            'transfers_out': float(transfers_out)
        },
        'accounts': [{'id': acc.id, 'name': acc.account_name, 'balance': float(acc.balance)} for acc in accounts],
        'alerts': alerts
    })

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='127.0.0.1', port=5000)