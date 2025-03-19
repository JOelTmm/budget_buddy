from flask import Flask
from config import Config
from models import db  # Importe db depuis models/__init__.py

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

@app.route('/')
def hello():
    return "Budget Buddy is running!"

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Crée les tables si elles n'existent pas
    app.run(debug=True)