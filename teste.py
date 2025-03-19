from sqlalchemy import create_engine, text

# Connexion à MySQL
DATABASE_URL = "mysql+mysqlconnector://root:Pipes606&@localhost/finance"
engine = create_engine(DATABASE_URL)

with engine.connect() as connection:
    result = connection.execute(text("SELECT * FROM account"))
    for row in result:
        print(row)  # Affiche chaque ligne de la table
