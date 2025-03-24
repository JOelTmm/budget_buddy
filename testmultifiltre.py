import customtkinter as ctk
import mysql.connector

class TransactionHistory:
    def __init__(self, root, user):
        self.user = user
        self.transactions = []

        # Connexion MySQL
        self.conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="admin",
            database="finance"
        )
        self.cursor = self.conn.cursor()

        # Interface graphique
        self.frame = ctk.CTkFrame(root)
        self.frame.pack(padx=20, pady=20, fill="both", expand=True)

        # Champs de filtres
        self.date_var = ctk.StringVar()
        self.category_var = ctk.StringVar()
        self.type_var = ctk.StringVar()
        self.min_amount_var = ctk.StringVar()
        self.max_amount_var = ctk.StringVar()
        self.start_date_var = ctk.StringVar()
        self.end_date_var = ctk.StringVar()
        self.sort_var = ctk.StringVar(value="date")

        # Cases à cocher pour activer/désactiver les filtres
        self.date_check = ctk.CTkCheckBox(self.frame, text="Filtrer par date", command=self.toggle_date)
        self.date_check.pack(anchor="w")
        self.date_entry = ctk.CTkEntry(self.frame, textvariable=self.date_var)

        self.category_check = ctk.CTkCheckBox(self.frame, text="Filtrer par catégorie", command=self.toggle_category)
        self.category_check.pack(anchor="w")
        self.category_entry = ctk.CTkEntry(self.frame, textvariable=self.category_var)

        self.type_check = ctk.CTkCheckBox(self.frame, text="Filtrer par type", command=self.toggle_type)
        self.type_check.pack(anchor="w")
        self.type_entry = ctk.CTkEntry(self.frame, textvariable=self.type_var)

        self.amount_check = ctk.CTkCheckBox(self.frame, text="Filtrer par montant", command=self.toggle_amount)
        self.amount_check.pack(anchor="w")
        self.min_amount_entry = ctk.CTkEntry(self.frame, textvariable=self.min_amount_var, placeholder_text="Min")
        self.max_amount_entry = ctk.CTkEntry(self.frame, textvariable=self.max_amount_var, placeholder_text="Max")

        self.date_range_check = ctk.CTkCheckBox(self.frame, text="Filtrer par période", command=self.toggle_date_range)
        self.date_range_check.pack(anchor="w")
        self.start_date_entry = ctk.CTkEntry(self.frame, textvariable=self.start_date_var, placeholder_text="Début")
        self.end_date_entry = ctk.CTkEntry(self.frame, textvariable=self.end_date_var, placeholder_text="Fin")

        self.sort_label = ctk.CTkLabel(self.frame, text="Trier par :")
        self.sort_label.pack(anchor="w")
        self.sort_menu = ctk.CTkOptionMenu(self.frame, variable=self.sort_var, values=["date", "montant croissant", "montant décroissant"])

        # Bouton de recherche
        self.search_button = ctk.CTkButton(self.frame, text="Rechercher", command=self.apply_filters)
        self.search_button.pack(pady=10)

        # Zone d'affichage des résultats (déroulante)
        self.result_frame = ctk.CTkScrollableFrame(self.frame, height=300)
        self.result_frame.pack(padx=10, pady=10, fill="both", expand=True)

        self.hide_entries()

    def hide_entries(self):
        """ Cache tous les champs d'entrée au départ """
        self.date_entry.pack_forget()
        self.category_entry.pack_forget()
        self.type_entry.pack_forget()
        self.min_amount_entry.pack_forget()
        self.max_amount_entry.pack_forget()
        self.start_date_entry.pack_forget()
        self.end_date_entry.pack_forget()
        self.sort_menu.pack_forget()

    def toggle_date(self):
        if self.date_check.get():
            self.date_entry.pack(anchor="w")
        else:
            self.date_entry.pack_forget()

    def toggle_category(self):
        if self.category_check.get():
            self.category_entry.pack(anchor="w")
        else:
            self.category_entry.pack_forget()

    def toggle_type(self):
        if self.type_check.get():
            self.type_entry.pack(anchor="w")
        else:
            self.type_entry.pack_forget()

    def toggle_amount(self):
        if self.amount_check.get():
            self.min_amount_entry.pack(anchor="w")
            self.max_amount_entry.pack(anchor="w")
        else:
            self.min_amount_entry.pack_forget()
            self.max_amount_entry.pack_forget()

    def toggle_date_range(self):
        if self.date_range_check.get():
            self.start_date_entry.pack(anchor="w")
            self.end_date_entry.pack(anchor="w")
        else:
            self.start_date_entry.pack_forget()
            self.end_date_entry.pack_forget()

    def apply_filters(self):
        """ Construit la requête SQL en fonction des filtres activés """
        query = """
        SELECT reference, description, amount, transaction_date, transaction_type, account_id
        FROM transaction
        WHERE (account_id = %s OR destination_account_id = %s)
        """
        params = [self.user, self.user]

        # Filtrer par une date précise (si le filtre par période n'est pas activé)
        if self.date_check.get() and not self.date_range_check.get():
            query += " AND transaction_date LIKE %s"
            params.append(f"%{self.date_var.get()}%")

        # Filtrer par catégorie
        if self.category_check.get():
            query += " AND category = %s"
            params.append(self.category_var.get())

        # Filtrer par type de transaction
        if self.type_check.get():
            query += " AND transaction_type = %s"
            params.append(self.type_var.get())

        # Filtrer par montant
        if self.amount_check.get():
            if self.min_amount_var.get():
                query += " AND amount >= %s"
                params.append(float(self.min_amount_var.get()))
            if self.max_amount_var.get():
                query += " AND amount <= %s"
                params.append(float(self.max_amount_var.get()))

        # Filtrer par plage de dates
        if self.date_range_check.get():
            if self.start_date_var.get() and self.end_date_var.get():
                query += " AND transaction_date BETWEEN %s AND %s"
                params.append(self.start_date_var.get())
                params.append(self.end_date_var.get())

        # Gestion du tri
        if self.sort_var.get() == "montant croissant":
            query += " ORDER BY amount ASC"
        elif self.sort_var.get() == "montant décroissant":
            query += " ORDER BY amount DESC"
        else:
            query += " ORDER BY transaction_date DESC"

        # Exécution de la requête
        self.cursor.execute(query, tuple(params))
        self.transactions = self.cursor.fetchall()

        # Affichage des résultats
        self.display_transactions()

    def display_transactions(self):
        """ Affiche les transactions filtrées dans un cadre déroulant """
        for widget in self.result_frame.winfo_children():
            widget.destroy()

        for ref, desc, amount, date, type, id in self.transactions:
            transactions_text = f"{date} | {ref} | {desc} | {amount}€"
            label = ctk.CTkLabel(self.result_frame, text=transactions_text, font=("Arial", 12))
            label.pack(anchor="w", padx=10, pady=2)

# Lancement de l'application
root = ctk.CTk()
root.geometry("800x600")
root.title("Filtrage des Transactions")
app = TransactionHistory(root, user=1)
root.mainloop()
