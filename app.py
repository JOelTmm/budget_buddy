from flask import Flask, request, jsonify
from Config import Config
from models import db
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from models.user import User
from models.banker import Banker
from models.account import Account
from models.transaction import Transaction

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

# Connexion utilisateur
@app.route('/api/user/login', methods=['POST'])
def login_user():
    data = request.get_json()
    user = User.query.filter_by(email=data['email']).first()
    if user and bcrypt.check_password_hash(user.password, data['password']):
        token = create_access_token(identity=f"user_{user.id}")
        return jsonify({'token': token})
    return jsonify({'error': 'Invalid credentials'}), 401

# Connexion banquier
@app.route('/api/banker/login', methods=['POST'])
def login_banker():
    data = request.get_json()
    banker = Banker.query.filter_by(email=data['email']).first()
    if banker and bcrypt.check_password_hash(banker.password, data['password']):
        token = create_access_token(identity=f"banker_{banker.id}")
        return jsonify({'token': token})
    return jsonify({'error': 'Invalid credentials'}), 401

# Middleware
def check_user(f):
    @jwt_required()
    def wrapper(*args, **kwargs):
        identity = get_jwt_identity()  # Ex. : "user_1"
        type_, id_ = identity.split('_')
        if type_ != 'user':
            return jsonify({'error': 'User access required'}), 403
        return f(int(id_), *args, **kwargs)
    return wrapper

# Dépôt
@app.route('/api/transaction/deposit', methods=['POST'])
@check_user
def deposit(user_id):
    data = request.get_json()
    account = Account.query.filter_by(id=data['account_id'], user_id=user_id).first()
    if not account:
        return jsonify({'error': 'Account not found'}), 404
    
    transaction = Transaction(
        reference=data['reference'],
        description=data.get('description'),
        amount=data['amount'],
        transaction_type='deposit',
        account_id=account.id,
        category=data.get('category')
    )
    account.balance += data['amount']
    db.session.add(transaction)
    db.session.commit()
    return jsonify({'message': 'Deposit successful', 'new_balance': float(account.balance)}), 201

# Autres routes...

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)