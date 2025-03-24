import customtkinter as ctk
from transactions_history import TransactionHistory

current_user = 1
transactions_history = TransactionHistory()
date = "11:13:43"

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
transactions_history.get_transactions_by_date(current_user, scroll_frame, date)

# Lancer l'application
root.mainloop()
