class Config:
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://root:admin@localhost/finance'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'admin'