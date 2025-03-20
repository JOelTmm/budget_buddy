import customtkinter as ctk
import mysql.connector

# Connexion à la base de données
def get_transactions():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="admin",
        database="finance"
    )

    cursor = conn.cursor()
    cursor.execute("SET @user1 = (SELECT id FROM `user` WHERE email = 'jean.dupont@example.com');")
    cursor.execute("SET @user2 = (SELECT id FROM `user` WHERE email = 'sophie.martin@example.com');")
    cursor.execute("SELECT @user1;")
    user = cursor.fetchone()[0]
    print(user)
    cursor.execute(f"SELECT reference, description, amount, transaction_date FROM transaction  WHERE account_id = %s OR destination_account_id = %s ORDER BY transaction_date DESC", (user, user))
    transactions = cursor.fetchall()
    conn.close()
    return transactions

# Création de la fenêtre principale
ctk.set_appearance_mode("dark")
root = ctk.CTk()
root.geometry("600x400")
root.title("Historique des Transactions")

# Titre
title_label = ctk.CTkLabel(root, text="Historique des Transactions", font=("Arial", 18, "bold"))
title_label.pack(pady=10)

# Création d'un frame déroulant
scroll_frame = ctk.CTkScrollableFrame(root, width=550, height=300)
scroll_frame.pack(padx=10, pady=10, fill="both", expand=True)

def display_transactions(scroll_frame):
    # Récupération et affichage des transactions
    transactions = get_transactions()
    for index, (ref, desc, amount, date) in enumerate(transactions):
        transaction_text = f"{date} | {ref} | {desc} | {amount}€"
        label = ctk.CTkLabel(scroll_frame, text=transaction_text, font=("Arial", 12))
        label.pack(anchor="w", padx=10, pady=2)
display_transactions(scroll_frame)

# Lancer l'application
root.mainloop()
