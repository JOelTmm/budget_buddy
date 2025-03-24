import customtkinter as ctk
from customtkinter import CTk, CTkFrame, CTkLabel, CTkButton, CTkEntry, CTkComboBox, CTkScrollableFrame
import tkinter as tk
from appV2 import app, db, register_user, login_user, create_account, add_transaction, get_transactions, get_balance, list_accounts, token_required
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from decimal import Decimal
import random

class BankingApp(CTk):
    def __init__(self):
        super().__init__()
        self.title("Revolut")
        self.geometry("600x700")
        self.configure(fg_color="#0A1F44")  # Bleu foncé Revolut
        self.token = None
        self.accounts = []
        with app.app_context():
            db.create_all()
        self.init_ui()

    def init_ui(self):
        # Écran de login
        self.login_frame = CTkFrame(self, corner_radius=10, fg_color="#142C6B")
        self.login_frame.pack(pady=50, padx=20, fill="both", expand=True)

        ctk.CTkLabel(self.login_frame, text="Revolut", font=("Helvetica", 30, "bold"), text_color="#FFFFFF").pack(pady=30)
        
        self.email_entry = CTkEntry(self.login_frame, placeholder_text="Email", width=300, corner_radius=8, fg_color="#1E3A8A", text_color="#FFFFFF", placeholder_text_color="#B0C4DE")
        self.email_entry.pack(pady=10)
        
        self.password_entry = CTkEntry(self.login_frame, placeholder_text="Mot de passe", show="*", width=300, corner_radius=8, fg_color="#1E3A8A", text_color="#FFFFFF", placeholder_text_color="#B0C4DE")
        self.password_entry.pack(pady=10)
        
        login_button = CTkButton(self.login_frame, text="Se connecter", command=self.login, corner_radius=25, fg_color="#FFFFFF", text_color="#0A1F44", hover_color="#E0E0E0", font=("Helvetica", 14, "bold"))
        login_button.pack(pady=20)

        # Interface principale
        self.main_frame = CTkFrame(self, corner_radius=0, fg_color="#0A1F44")
        self.main_frame.pack(pady=0, padx=0, fill="both", expand=True)
        self.main_frame.pack_forget()

        # En-tête avec solde
        header_frame = CTkFrame(self.main_frame, corner_radius=0, fg_color="#142C6B")
        header_frame.pack(fill="x")
        self.balance_label = CTkLabel(header_frame, text="0.00 €", font=("Helvetica", 36, "bold"), text_color="#00C853")
        self.balance_label.pack(pady=20)
        ctk.CTkLabel(header_frame, text="Solde total", font=("Helvetica", 14), text_color="#FFFFFF").pack()

        # Liste des transactions
        self.transaction_frame = CTkScrollableFrame(self.main_frame, width=560, height=400, corner_radius=0, fg_color="#0A1F44")
        self.transaction_frame.pack(pady=10, padx=20)

        # Filtres et boutons
        action_frame = CTkFrame(self.main_frame, corner_radius=0, fg_color="#0A1F44")
        action_frame.pack(fill="x", pady=10)
        
        self.filter_combo = CTkComboBox(action_frame, values=["Tous", "Loisir", "Voyage", "Abonnement", "Revenu", "Autre"], command=self.filter_transactions, fg_color="#1E3A8A", text_color="#FFFFFF", width=150)
        self.filter_combo.pack(side="left", padx=20)
        
        add_button = CTkButton(action_frame, text="+ Transaction", command=self.open_transaction_window, corner_radius=25, fg_color="#FFFFFF", text_color="#0A1F44", hover_color="#E0E0E0", font=("Helvetica", 14, "bold"))
        add_button.pack(side="right", padx=20)
        
        graph_button = CTkButton(action_frame, text="Graphique", command=self.show_graph, corner_radius=25, fg_color="#FFFFFF", text_color="#0A1F44", hover_color="#E0E0E0", font=("Helvetica", 14, "bold"))
        graph_button.pack(side="right", padx=10)

    def login(self):
        email = self.email_entry.get()
        password = self.password_entry.get()
        with app.app_context():
            result, status = login_user(email, password)
        if status == 200:
            self.token = result['token']
            self.login_frame.pack_forget()
            self.main_frame.pack(pady=0, padx=0, fill="both", expand=True)
            self.load_accounts()
            self.update_balance()
            self.load_transactions()
            self.fade_in(self.main_frame)
        else:
            tk.messagebox.showerror("Erreur", result['error'])

    def load_accounts(self):
        with app.app_context():
            result, status = list_accounts(self.token)
            if status == 200:
                self.accounts = result['accounts']

    def update_balance(self):
        total_balance = sum(acc['balance'] for acc in self.accounts)
        self.balance_label.configure(text=f"{total_balance:.2f} €")

    def load_transactions(self, category_filter="Tous"):
        for widget in self.transaction_frame.winfo_children():
            widget.destroy()
        if not self.accounts:
            return
        with app.app_context():
            row = 0
            for account in self.accounts:
                result, status = get_transactions(self.token, account['id'])
                if status == 200:
                    for transaction in result:
                        if category_filter == "Tous" or category_filter == transaction['category']:
                            frame = CTkFrame(self.transaction_frame, corner_radius=10, fg_color="#142C6B")
                            frame.grid(row=row, column=0, sticky="ew", padx=5, pady=5)
                            
                            desc_label = CTkLabel(frame, text=transaction['description'], font=("Helvetica", 14), text_color="#FFFFFF")
                            desc_label.pack(side="left", padx=10)
                            
                            amount_str = f"{transaction['amount']:+.2f}" if transaction['type'] in ['deposit', 'transfer'] else f"-{transaction['amount']:.2f}"
                            amount_label = CTkLabel(frame, text=amount_str + " €", font=("Helvetica", 14, "bold"), text_color="#00C853" if transaction['type'] == 'deposit' else "#FF5252")
                            amount_label.pack(side="right", padx=10)
                            
                            date_label = CTkLabel(frame, text=transaction['date'].split('T')[0], font=("Helvetica", 12), text_color="#B0BEC5")
                            date_label.pack(side="right", padx=10)
                            row += 1

    def filter_transactions(self, category):
        self.load_transactions(category)

    def open_transaction_window(self):
        self.transaction_window = ctk.CTkToplevel(self)
        self.transaction_window.title("Nouvelle transaction")
        self.transaction_window.geometry("350x400")
        self.transaction_window.configure(fg_color="#0A1F44")
        self.transaction_window.attributes('-topmost', True)

        # Animation d'ouverture (fade-in)
        self.transaction_window.attributes("-alpha", 0)
        self.fade_in(self.transaction_window)

        frame = CTkFrame(self.transaction_window, corner_radius=10, fg_color="#142C6B")
        frame.pack(pady=20, padx=20, fill="both", expand=True)

        ctk.CTkLabel(frame, text="Ajouter une transaction", font=("Helvetica", 18, "bold"), text_color="#FFFFFF").pack(pady=10)

        self.account_combo = CTkComboBox(frame, values=[f"{i}. {acc['name']}" for i, acc in enumerate(self.accounts, 1)], fg_color="#1E3A8A", text_color="#FFFFFF")
        self.account_combo.pack(pady=10)

        self.transaction_type = CTkComboBox(frame, values=["Dépôt", "Retrait", "Transfert"], fg_color="#1E3A8A", text_color="#FFFFFF")
        self.transaction_type.pack(pady=10)

        self.description_entry = CTkEntry(frame, placeholder_text="Description", width=250, corner_radius=8, fg_color="#1E3A8A", text_color="#FFFFFF")
        self.description_entry.pack(pady=10)

        self.amount_entry = CTkEntry(frame, placeholder_text="Montant", width=250, corner_radius=8, fg_color="#1E3A8A", text_color="#FFFFFF")
        self.amount_entry.pack(pady=10)

        self.category_combo = CTkComboBox(frame, values=["Loisir", "Voyage", "Abonnement", "Revenu", "Autre"], fg_color="#1E3A8A", text_color="#FFFFFF")
        self.category_combo.pack(pady=10)

        self.dest_account_combo = CTkComboBox(frame, values=["Aucun"] + [f"{i}. {acc['name']}" for i, acc in enumerate(self.accounts, 1)], fg_color="#1E3A8A", text_color="#FFFFFF")
        self.dest_account_combo.pack(pady=10)

        save_button = CTkButton(frame, text="Confirmer", command=self.add_transaction, corner_radius=25, fg_color="#FFFFFF", text_color="#0A1F44", hover_color="#E0E0E0")
        save_button.pack(pady=20)

    def add_transaction(self):
        account_idx = self.account_combo.get().split('.')[0]
        account_id = self.accounts[int(account_idx) - 1]['id']
        transaction_type = self.transaction_type.get().lower()
        description = self.description_entry.get()
        amount = self.amount_entry.get()
        category = self.category_combo.get()
        dest_idx = self.dest_account_combo.get()
        dest_account_id = None if dest_idx == "Aucun" else self.accounts[int(dest_idx.split('.')[0]) - 1]['id']

        if not description or not amount:
            tk.messagebox.showerror("Erreur", "Veuillez remplir tous les champs.")
            return

        try:
            float(amount)
        except ValueError:
            tk.messagebox.showerror("Erreur", "Le montant doit être un nombre valide.")
            return

        with app.app_context():
            result, status = add_transaction(
                self.token, account_id, f"TX{random.randint(1000, 9999)}", description, amount, transaction_type, category, dest_account_id
            )
            if status == 201:
                self.load_accounts()
                self.update_balance()
                self.load_transactions()
                self.fade_out(self.transaction_window)
            else:
                tk.messagebox.showerror("Erreur", result['error'])

    def show_graph(self):
        categories = {}
        with app.app_context():
            for account in self.accounts:
                result, status = get_transactions(self.token, account['id'])
                if status == 200:
                    for t in result:
                        amount = t['amount']
                        if t['type'] == 'withdrawal' or (t['type'] == 'transfer' and t['account_id'] == account['id']):
                            amount = -amount
                        categories[t['category']] = categories.get(t['category'], 0) + amount

        fig, ax = plt.subplots(figsize=(8, 5))
        ax.bar(categories.keys(), categories.values(), color='#00C853')
        ax.set_title("Dépenses et revenus", color='#FFFFFF', fontsize=14)
        ax.set_ylabel("Montant (€)", color='#FFFFFF', fontsize=12)
        ax.set_xlabel("Catégories", color='#FFFFFF', fontsize=12)
        ax.tick_params(axis='x', colors='#FFFFFF')
        ax.tick_params(axis='y', colors='#FFFFFF')
        ax.set_facecolor('#142C6B')
        fig.set_facecolor('#0A1F44')

        graph_window = ctk.CTkToplevel(self)
        graph_window.title("Graphique")
        graph_window.geometry("600x400")
        graph_window.configure(fg_color="#0A1F44")
        self.fade_in(graph_window)

        canvas = FigureCanvasTkAgg(fig, master=graph_window)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def fade_in(self, widget):
        widget.attributes("-alpha", 0)
        for i in range(0, 11):
            widget.attributes("-alpha", i / 10)
            widget.update()
            widget.after(50)

    def fade_out(self, widget):
        for i in range(10, -1, -1):
            widget.attributes("-alpha", i / 10)
            widget.update()
            widget.after(50)
        widget.destroy()

if __name__ == "__main__":
    app_gui = BankingApp()
    app_gui.mainloop()