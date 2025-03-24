import customtkinter as ctk
import mysql.connector

def get_account():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="admin",
        database="finance"
    )

    cursor = conn.cursor()
    cursor.execute("SELECT user_id, account_name, balance FROM account")
    account_data = cursor.fetchall()
    print (account_data)
    conn.close()
    return account_data

# Création de la fenêtre principale
ctk.set_appearance_mode("dark")
root = ctk.CTk()
root.geometry("600x400")
root.title("Historique des Transactions")

account_data = get_account()

user_account = {}
for user_id, account_name, balance in account_data:
    if user_id not in user_account:
        user_account[user_id] = []
    user_account[user_id].append({account_name: balance})

# Titre
title_label = ctk.CTkLabel(root, text=f"{list(user_account[1][2].keys())[0]} {list(user_account[1][2].values())[0]}", font=("Arial", 18, "bold"))
title_label.pack(pady=10)
print(user_account[1][2])

print(list(user_account[1][2].keys())[0])  # Affiche juste le nom du premier compte

print(list(user_account[1][2].values())[0])  # Affiche juste la balance du premier compte*


"""print(user_account[1][2])  # Affiche le premier compte de l'utilisateur 1

print(user_account[1][2].keys())  # Affiche juste le nom du premier compte

print(list(user_account[1][2].values())[0])  # Affiche juste la balance du premier compte

#pour un compte en particulier
for account in user_account[1]:  # Parcourt tous les comptes de user_id = 1
    if "Compte Épargne Jean" in account:
        print(account["Compte Épargne Jean"])  # Affiche le solde
"""
# Création d'un frame
frame = ctk.CTkFrame(root, width=550, height=300)
frame.pack(padx=10, pady=10, fill="both", expand=True)
root.mainloop()
