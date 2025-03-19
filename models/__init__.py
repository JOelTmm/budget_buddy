from flask_sqlalchemy import SQLAlchemy

# Initialisation de db
db = SQLAlchemy()

# Importation des modèles (après la définition de db)
from .user import User
from .account import Account
from .transaction import Transaction
from .banker import Banker