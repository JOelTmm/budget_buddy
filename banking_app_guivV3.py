import customtkinter as ctk
from customtkinter import CTk, CTkFrame, CTkLabel, CTkButton, CTkEntry, CTkComboBox, CTkScrollableFrame, CTkCheckBox
import tkinter as tk
from appV2 import app, db, register_user, login_user, create_account, add_transaction, get_transactions, list_accounts, get_all_accounts, register_banker
from models.user import User
from models.banker import Banker
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from datetime import datetime
import random
import jwt

class BankingApp(CTk):
    def __init__(self):
        super().__init__()
        self.title("Revolut")
        self.geometry("1000x700")
        self.configure(fg_color="#0A1F44")
        self.token = None
        self.accounts = []
        self.role = None
        self.current_id = None
        self.all_accounts = []
        self.clients = []
        with app.app_context():
            db.create_all()
        self.init_ui()

    def init_ui(self):
        self.welcome_frame = CTkFrame(self, corner_radius=0, fg_color="#0A1F44")
        self.welcome_frame.pack(fill="both", expand=True)
        CTkLabel(self.welcome_frame, text="Welcome to Revolut", font=("Helvetica", 36, "bold"), text_color="#FFFFFF").pack(pady=50)
        CTkButton(self.welcome_frame, text="Login", command=self.show_login_screen, corner_radius=25, fg_color="#FFFFFF", text_color="#0A1F44", hover_color="#E0E0E0", font=("Helvetica", 16, "bold"), width=200).pack(pady=20)
        CTkButton(self.welcome_frame, text="Register as User", command=self.show_register_screen, corner_radius=25, fg_color="#FFFFFF", text_color="#0A1F44", hover_color="#E0E0E0", font=("Helvetica", 16, "bold"), width=200).pack(pady=20)
        CTkButton(self.welcome_frame, text="Register as Banker", command=self.show_banker_register_screen, corner_radius=25, fg_color="#FFFFFF", text_color="#0A1F44", hover_color="#E0E0E0", font=("Helvetica", 16, "bold"), width=200).pack(pady=20)

        self.login_frame = CTkFrame(self, corner_radius=10, fg_color="#142C6B")
        self.login_frame.pack(fill="both", expand=True)
        self.login_frame.pack_forget()
        CTkLabel(self.login_frame, text="Login", font=("Helvetica", 30, "bold"), text_color="#FFFFFF").pack(pady=30)
        self.email_entry = CTkEntry(self.login_frame, placeholder_text="Email", width=300, corner_radius=8, fg_color="#1E3A8A", text_color="#FFFFFF", placeholder_text_color="#B0C4DE")
        self.email_entry.pack(pady=10)
        self.password_entry = CTkEntry(self.login_frame, placeholder_text="Password", show="*", width=300, corner_radius=8, fg_color="#1E3A8A", text_color="#FFFFFF", placeholder_text_color="#B0C4DE")
        self.password_entry.pack(pady=10)
        self.banker_login_checkbox = CTkCheckBox(self.login_frame, text="Login as Banker", fg_color="#FFFFFF", text_color="#FFFFFF", hover_color="#E0E0E0")
        self.banker_login_checkbox.pack(pady=10)
        CTkButton(self.login_frame, text="Login", command=self.login, corner_radius=25, fg_color="#FFFFFF", text_color="#0A1F44", hover_color="#E0E0E0", font=("Helvetica", 14, "bold")).pack(pady=20)
        CTkButton(self.login_frame, text="Back", command=lambda: [self.login_frame.pack_forget(), self.welcome_frame.pack(fill="both", expand=True)], corner_radius=25, fg_color="#FFFFFF", text_color="#0A1F44", hover_color="#E0E0E0", font=("Helvetica", 14, "bold")).pack(pady=10)

        self.register_frame = CTkFrame(self, corner_radius=10, fg_color="#142C6B")
        self.register_frame.pack(fill="both", expand=True)
        self.register_frame.pack_forget()
        CTkLabel(self.register_frame, text="User Registration", font=("Helvetica", 30, "bold"), text_color="#FFFFFF").pack(pady=30)
        self.reg_last_name_entry = CTkEntry(self.register_frame, placeholder_text="Last Name", width=300, corner_radius=8, fg_color="#1E3A8A", text_color="#FFFFFF")
        self.reg_last_name_entry.pack(pady=10)
        self.reg_first_name_entry = CTkEntry(self.register_frame, placeholder_text="First Name", width=300, corner_radius=8, fg_color="#1E3A8A", text_color="#FFFFFF")
        self.reg_first_name_entry.pack(pady=10)
        self.reg_email_entry = CTkEntry(self.register_frame, placeholder_text="Email", width=300, corner_radius=8, fg_color="#1E3A8A", text_color="#FFFFFF")
        self.reg_email_entry.pack(pady=10)
        self.reg_password_entry = CTkEntry(self.register_frame, placeholder_text="Password", show="*", width=300, corner_radius=8, fg_color="#1E3A8A", text_color="#FFFFFF")
        self.reg_password_entry.pack(pady=10)
        CTkButton(self.register_frame, text="Register", command=self.register, corner_radius=25, fg_color="#FFFFFF", text_color="#0A1F44", hover_color="#E0E0E0", font=("Helvetica", 14, "bold")).pack(pady=20)
        CTkButton(self.register_frame, text="Back", command=lambda: [self.register_frame.pack_forget(), self.welcome_frame.pack(fill="both", expand=True)], corner_radius=25, fg_color="#FFFFFF", text_color="#0A1F44", hover_color="#E0E0E0", font=("Helvetica", 14, "bold")).pack(pady=10)

        self.banker_register_frame = CTkFrame(self, corner_radius=10, fg_color="#142C6B")
        self.banker_register_frame.pack(fill="both", expand=True)
        self.banker_register_frame.pack_forget()
        CTkLabel(self.banker_register_frame, text="Banker Registration", font=("Helvetica", 30, "bold"), text_color="#FFFFFF").pack(pady=30)
        self.banker_last_name_entry = CTkEntry(self.banker_register_frame, placeholder_text="Last Name", width=300, corner_radius=8, fg_color="#1E3A8A", text_color="#FFFFFF")
        self.banker_last_name_entry.pack(pady=10)
        self.banker_first_name_entry = CTkEntry(self.banker_register_frame, placeholder_text="First Name", width=300, corner_radius=8, fg_color="#1E3A8A", text_color="#FFFFFF")
        self.banker_first_name_entry.pack(pady=10)
        self.banker_email_entry = CTkEntry(self.banker_register_frame, placeholder_text="Email", width=300, corner_radius=8, fg_color="#1E3A8A", text_color="#FFFFFF")
        self.banker_email_entry.pack(pady=10)
        self.banker_password_entry = CTkEntry(self.banker_register_frame, placeholder_text="Password", show="*", width=300, corner_radius=8, fg_color="#1E3A8A", text_color="#FFFFFF")
        self.banker_password_entry.pack(pady=10)
        CTkButton(self.banker_register_frame, text="Register", command=self.register_banker, corner_radius=25, fg_color="#FFFFFF", text_color="#0A1F44", hover_color="#E0E0E0", font=("Helvetica", 14, "bold")).pack(pady=20)
        CTkButton(self.banker_register_frame, text="Back", command=lambda: [self.banker_register_frame.pack_forget(), self.welcome_frame.pack(fill="both", expand=True)], corner_radius=25, fg_color="#FFFFFF", text_color="#0A1F44", hover_color="#E0E0E0", font=("Helvetica", 14, "bold")).pack(pady=10)

        self.main_frame = CTkFrame(self, corner_radius=0, fg_color="#0A1F44")
        self.main_frame.pack(fill="both", expand=True)
        self.main_frame.pack_forget()
        header_frame = CTkFrame(self.main_frame, corner_radius=0, fg_color="#142C6B")
        header_frame.pack(fill="x")
        CTkLabel(header_frame, text="Revolut", font=("Helvetica", 20, "bold"), text_color="#FFFFFF").pack(side="left", padx=10, pady=10)
        self.balance_label = CTkLabel(header_frame, text="0.00 €", font=("Helvetica", 24, "bold"), text_color="#00C853")
        self.balance_label.pack(side="right", padx=10, pady=10)
        CTkButton(header_frame, text="Logout", command=self.logout, corner_radius=10, fg_color="#FFFFFF", text_color="#0A1F44", width=100).pack(side="right", padx=10, pady=10)
        self.accounts_frame = CTkScrollableFrame(self.main_frame, width=960, height=150, corner_radius=0, fg_color="#0A1F44", orientation="horizontal")
        self.accounts_frame.pack(pady=10, padx=20, fill="x")
        self.transaction_frame = CTkScrollableFrame(self.main_frame, width=960, height=350, corner_radius=0, fg_color="#0A1F44")
        self.transaction_frame.pack(pady=10, padx=20, fill="both", expand=True)

        filter_frame = CTkFrame(self.main_frame, fg_color="#0A1F44")
        filter_frame.pack(fill="x", pady=5)
        self.start_date_filter = CTkEntry(filter_frame, placeholder_text="Start Date (YYYY-MM-DD)", width=150, fg_color="#1E3A8A", text_color="#FFFFFF")
        self.start_date_filter.pack(side="left", padx=5)
        self.end_date_filter = CTkEntry(filter_frame, placeholder_text="End Date (YYYY-MM-DD)", width=150, fg_color="#1E3A8A", text_color="#FFFFFF")
        self.end_date_filter.pack(side="left", padx=5)
        self.category_filter = CTkComboBox(filter_frame, values=["All", "Leisure", "Meal", "Bribe", "Income", "Other"], fg_color="#1E3A8A", text_color="#FFFFFF", width=150)
        self.category_filter.pack(side="left", padx=5)
        self.type_filter = CTkComboBox(filter_frame, values=["All", "deposit", "withdrawal", "transfer"], fg_color="#1E3A8A", text_color="#FFFFFF", width=150)
        self.type_filter.pack(side="left", padx=5)
        self.sort_filter = CTkComboBox(filter_frame, values=["Amount Ascending", "Amount Descending"], fg_color="#1E3A8A", text_color="#FFFFFF", width=150)
        self.sort_filter.pack(side="left", padx=5)
        CTkButton(filter_frame, text="Filter", command=self.filter_transactions, corner_radius=10, fg_color="#FFFFFF", text_color="#0A1F44", width=100).pack(side="left", padx=5)

        action_frame = CTkFrame(self.main_frame, corner_radius=0, fg_color="#142C6B")
        action_frame.pack(side="bottom", fill="x")
        CTkButton(action_frame, text="New Account", command=self.open_account_window, corner_radius=0, fg_color="#FFFFFF", text_color="#0A1F44", width=150).pack(side="left", padx=10, pady=10)
        CTkButton(action_frame, text="New Transaction", command=self.open_transaction_window, corner_radius=0, fg_color="#FFFFFF", text_color="#0A1F44", width=150).pack(side="left", padx=10, pady=10)
        CTkButton(action_frame, text="Overview", command=self.show_overview, corner_radius=0, fg_color="#FFFFFF", text_color="#0A1F44", width=150).pack(side="left", padx=10, pady=10)

        self.admin_frame = CTkFrame(self, corner_radius=0, fg_color="#0A1F44")
        self.admin_frame.pack(fill="both", expand=True)
        self.admin_frame.pack_forget()
        admin_header = CTkFrame(self.admin_frame, corner_radius=0, fg_color="#142C6B")
        admin_header.pack(fill="x")
        CTkLabel(admin_header, text="Client Management - Banker", font=("Helvetica", 20, "bold"), text_color="#FFFFFF").pack(side="left", padx=10, pady=10)
        CTkButton(admin_header, text="Logout", command=self.logout, corner_radius=10, fg_color="#FFFFFF", text_color="#0A1F44", width=100).pack(side="right", padx=10, pady=10)
        CTkButton(admin_header, text="Add Client", command=self.add_client_window, corner_radius=10, fg_color="#FFFFFF", text_color="#0A1F44", width=150).pack(side="right", padx=10, pady=10)
        CTkButton(admin_header, text="View All Transactions", command=self.show_all_transactions, corner_radius=10, fg_color="#FFFFFF", text_color="#0A1F44", width=150).pack(side="right", padx=10, pady=10)
        self.clients_frame = CTkScrollableFrame(self.admin_frame, width=960, height=500, corner_radius=0, fg_color="#0A1F44")
        self.clients_frame.pack(pady=10, padx=20, fill="both", expand=True)
        self.all_transactions_frame = CTkFrame(self.admin_frame, corner_radius=0, fg_color="#0A1F44")
        self.all_transactions_frame.pack(fill="both", expand=True)
        self.all_transactions_frame.pack_forget()

        self.overview_frame = CTkFrame(self, corner_radius=0, fg_color="#0A1F44")
        self.overview_frame.pack(fill="both", expand=True)
        self.overview_frame.pack_forget()

    def show_login_screen(self):
        self.welcome_frame.pack_forget()
        self.login_frame.pack(fill="both", expand=True)

    def show_register_screen(self):
        self.welcome_frame.pack_forget()
        self.register_frame.pack(fill="both", expand=True)

    def show_banker_register_screen(self):
        self.welcome_frame.pack_forget()
        self.banker_register_frame.pack(fill="both", expand=True)

    def register(self):
        last_name = self.reg_last_name_entry.get()
        first_name = self.reg_first_name_entry.get()
        email = self.reg_email_entry.get()
        password = self.reg_password_entry.get()
        if not all([last_name, first_name, email, password]):
            tk.messagebox.showerror("Error", "Please fill in all fields.")
            return
        with app.app_context():
            result, status = register_user(last_name, first_name, email, password)
        if status == 201:
            tk.messagebox.showinfo("Success", "User account created successfully!")
            self.register_frame.pack_forget()
            self.welcome_frame.pack(fill="both", expand=True)
        else:
            tk.messagebox.showerror("Error", result['error'])

    def register_banker(self):
        last_name = self.banker_last_name_entry.get()
        first_name = self.banker_first_name_entry.get()
        email = self.banker_email_entry.get()
        password = self.banker_password_entry.get()
        if not all([last_name, first_name, email, password]):
            tk.messagebox.showerror("Error", "Please fill in all fields.")
            return
        with app.app_context():
            result, status = register_banker(last_name, first_name, email, password)
        if status == 201:
            tk.messagebox.showinfo("Success", "Banker account created successfully!")
            self.banker_register_frame.pack_forget()
            self.welcome_frame.pack(fill="both", expand=True)
        else:
            tk.messagebox.showerror("Error", result['error'])

    def login(self):
        email = self.email_entry.get()
        password = self.password_entry.get()
        is_banker_login = self.banker_login_checkbox.get()
        with app.app_context():
            result, status = login_user(email, password)
            if status == 200:
                self.token = result['token']
                decoded_token = jwt.decode(self.token, app.config['SECRET_KEY'], algorithms=['HS256'])
                self.role = decoded_token['role']
                self.current_id = decoded_token.get('user_id') or decoded_token.get('banker_id')
                if (is_banker_login and self.role != 'banker') or (not is_banker_login and self.role == 'banker'):
                    tk.messagebox.showerror("Error", "Role error: Check the 'Login as Banker' option.")
                    return
                self.login_frame.pack_forget()
                if self.role == 'banker':
                    self.show_admin_frame()
                else:
                    self.show_main_frame()
            else:
                tk.messagebox.showerror("Error", result['error'])

    def logout(self):
        self.token = None
        self.accounts = []
        self.role = None
        self.current_id = None
        self.main_frame.pack_forget()
        self.admin_frame.pack_forget()
        self.overview_frame.pack_forget()
        self.welcome_frame.pack(fill="both", expand=True)

    def show_main_frame(self):
        self.admin_frame.pack_forget()
        self.overview_frame.pack_forget()
        self.main_frame.pack(fill="both", expand=True)
        self.load_accounts()
        self.update_balance()
        self.load_transactions()

    def show_admin_frame(self):
        self.main_frame.pack_forget()
        self.all_transactions_frame.pack_forget()
        self.admin_frame.pack(fill="both", expand=True)
        self.load_clients()

    def load_accounts(self):
        for widget in self.accounts_frame.winfo_children():
            widget.destroy()
        with app.app_context():
            result, status = list_accounts(self.token)
            if status == 200:
                self.accounts = result['accounts']
                for i, account in enumerate(self.accounts):
                    frame = CTkFrame(self.accounts_frame, corner_radius=10, fg_color="#1E3A8A", width=150, height=120)
                    frame.grid(row=0, column=i, padx=10, pady=10)
                    CTkLabel(frame, text=account['name'], font=("Helvetica", 14, "bold"), text_color="#FFFFFF").pack(pady=5)
                    alert_text = " (Overdraft)" if account['balance'] < 0 else " (Low Balance)" if account['balance'] < 100 else ""
                    CTkLabel(frame, text=f"{account['balance']:.2f} €{alert_text}", font=("Helvetica", 18), text_color="#FF5252" if alert_text else "#00C853").pack(pady=5)
            else:
                CTkLabel(self.accounts_frame, text="Error loading accounts.", font=("Helvetica", 14), text_color="#FF5252").pack(pady=10)

    def update_balance(self):
        total_balance = sum(acc['balance'] for acc in self.accounts)
        self.balance_label.configure(text=f"{total_balance:.2f} €")

    def load_transactions(self, start_date=None, end_date=None, category_filter="All", type_filter="All", sort_filter=None):
        for widget in self.transaction_frame.winfo_children():
            widget.destroy()
        if not self.accounts:
            return
        all_transactions = []
        with app.app_context():
            for account in self.accounts:
                result, status = get_transactions(self.token, account['id'], type_filter if type_filter != "All" else None, category_filter if category_filter != "All" else None, start_date, end_date, 'asc' if sort_filter == "Amount Ascending" else 'desc' if sort_filter == "Amount Descending" else None)
                if status == 200:
                    all_transactions.extend(result)

        filtered_transactions = []
        for t in all_transactions:
            date = t['date'].split('T')[0]
            date_match = True
            if start_date and date < start_date:
                date_match = False
            if end_date and date > end_date:
                date_match = False
            category_match = category_filter == "All" or t['category'] == category_filter
            type_match = type_filter == "All" or t['type'] == type_filter
            if date_match and category_match and type_match:
                filtered_transactions.append(t)

        if sort_filter:
            filtered_transactions.sort(key=lambda x: float(x['amount']), reverse=(sort_filter == "Amount Descending"))

        row = 0
        for t in filtered_transactions:
            frame = CTkFrame(self.transaction_frame, corner_radius=10, fg_color="#1E3A8A")
            frame.grid(row=row, column=0, sticky="ew", padx=5, pady=5)
            CTkLabel(frame, text=t['description'], font=("Helvetica", 14), text_color="#FFFFFF").pack(side="left", padx=10)
            amount_str = f"+{t['amount']:.2f}" if t['type'] == 'deposit' else f"-{t['amount']:.2f}"
            CTkLabel(frame, text=amount_str + " €", font=("Helvetica", 14, "bold"), text_color="#00C853" if t['type'] == 'deposit' else "#FF5252").pack(side="right", padx=10)
            CTkLabel(frame, text=t['date'].split('T')[0], font=("Helvetica", 12), text_color="#B0C4DE").pack(side="right", padx=10)
            row += 1

    def filter_transactions(self):
        start_date = self.start_date_filter.get() or None
        end_date = self.end_date_filter.get() or None
        category_filter = self.category_filter.get()
        type_filter = self.type_filter.get()
        sort_filter = self.sort_filter.get()
        self.load_transactions(start_date, end_date, category_filter, type_filter, sort_filter)

    def open_account_window(self):
        self.account_window = ctk.CTkToplevel(self)
        self.account_window.title("New Account")
        self.account_window.geometry("350x200")
        self.account_window.configure(fg_color="#0A1F44")
        self.fade_in(self.account_window)
        frame = CTkFrame(self.account_window, corner_radius=10, fg_color="#142C6B")
        frame.pack(pady=20, padx=20, fill="both", expand=True)
        CTkLabel(frame, text="Add a New Account", font=("Helvetica", 18, "bold"), text_color="#FFFFFF").pack(pady=10)
        self.account_name_entry = CTkEntry(frame, placeholder_text="Account Name", width=250, corner_radius=8, fg_color="#1E3A8A", text_color="#FFFFFF")
        self.account_name_entry.pack(pady=10)
        CTkButton(frame, text="Submit", command=self.add_account, corner_radius=25, fg_color="#FFFFFF", text_color="#0A1F44").pack(pady=20)

    def add_account(self):
        name = self.account_name_entry.get()
        if not name:
            tk.messagebox.showerror("Error", "Please enter an account name.")
            return
        with app.app_context():
            result, status = create_account(self.token, name)
            if status == 201:
                self.load_accounts()
                self.update_balance()
                self.fade_out(self.account_window)
            else:
                tk.messagebox.showerror("Error", result['error'])

    def open_transaction_window(self):
        self.transaction_window = ctk.CTkToplevel(self)
        self.transaction_window.title("New Transaction")
        self.transaction_window.geometry("400x450")
        self.transaction_window.configure(fg_color="#0A1F44")
        self.fade_in(self.transaction_window)
        frame = CTkFrame(self.transaction_window, corner_radius=10, fg_color="#142C6B")
        frame.pack(pady=20, padx=20, fill="both", expand=True)
        CTkLabel(frame, text="Add a Transaction", font=("Helvetica", 18, "bold"), text_color="#FFFFFF").pack(pady=10)
        self.account_combo = CTkComboBox(frame, values=[acc['name'] for acc in self.accounts], fg_color="#1E3A8A", text_color="#FFFFFF")
        self.account_combo.pack(pady=10)
        self.transaction_type = CTkComboBox(frame, values=["deposit", "withdrawal", "transfer"], fg_color="#1E3A8A", text_color="#FFFFFF", command=self.toggle_transaction_fields)
        self.transaction_type.pack(pady=10)
        self.description_entry = CTkEntry(frame, placeholder_text="Description", width=250, corner_radius=8, fg_color="#1E3A8A", text_color="#FFFFFF")
        self.description_entry.pack(pady=10)
        self.amount_entry = CTkEntry(frame, placeholder_text="Amount", width=250, corner_radius=8, fg_color="#1E3A8A", text_color="#FFFFFF")
        self.amount_entry.pack(pady=10)
        self.category_combo = CTkComboBox(frame, values=["Leisure", "Meal", "Bribe", "Income", "Other"], fg_color="#1E3A8A", text_color="#FFFFFF")
        self.category_combo.pack(pady=10)
        self.dest_account_label = CTkLabel(frame, text="Destination Account", font=("Helvetica", 14), text_color="#FFFFFF")
        self.dest_account_combo = CTkComboBox(frame, values=[acc['name'] for acc in self.accounts if acc['name'] != self.account_combo.get()], fg_color="#1E3A8A", text_color="#FFFFFF")
        self.dest_account_label.pack_forget()
        self.dest_account_combo.pack_forget()
        CTkButton(frame, text="Submit", command=self.add_transaction, corner_radius=25, fg_color="#00C853", text_color="#FFFFFF", width=150).pack(pady=20)

    def toggle_transaction_fields(self, choice):
        if choice == "transfer":
            self.dest_account_label.pack(pady=5)
            self.dest_account_combo.pack(pady=10)
            self.dest_account_combo.configure(values=[acc['name'] for acc in self.accounts if acc['name'] != self.account_combo.get()])
        else:
            self.dest_account_label.pack_forget()
            self.dest_account_combo.pack_forget()

    def add_transaction(self):
        account_name = self.account_combo.get()
        account_id = next((acc['id'] for acc in self.accounts if acc['name'] == account_name), None)
        transaction_type = self.transaction_type.get()
        description = self.description_entry.get()
        amount = self.amount_entry.get()
        category = self.category_combo.get()
        dest_name = self.dest_account_combo.get() if transaction_type == "transfer" else None
        dest_account_id = None if not dest_name else next((acc['id'] for acc in self.accounts if acc['name'] == dest_name), None)
        if not all([account_id, description, amount]):
            tk.messagebox.showerror("Error", "Please fill in all mandatory fields.")
            return
        try:
            amount = float(amount)
        except ValueError:
            tk.messagebox.showerror("Error", "Amount must be a valid number.")
            return
        with app.app_context():
            result, status = add_transaction(self.token, account_id, f"TX{random.randint(1000, 9999)}", description, amount, transaction_type, category, dest_account_id)
            if status == 201:
                self.load_accounts()
                self.update_balance()
                self.load_transactions()
                self.fade_out(self.transaction_window)
                if any(acc['balance'] < 0 for acc in self.accounts):
                    tk.messagebox.showwarning("Alert", "One or more accounts are now in overdraft.")
            else:
                tk.messagebox.showerror("Error", result.get('error', 'Unknown error'))

    def show_graph(self):
        categories = {}
        with app.app_context():
            for account in self.accounts:
                result, status = get_transactions(self.token, account['id'])
                if status == 200:
                    for t in result:
                        amount = float(t['amount'])
                        if t['type'] == 'withdrawal' or (t['type'] == 'transfer' and 'destination_account_id' in t and t['destination_account_id'] != account['id']):
                            amount = -amount
                        categories[t['category']] = categories.get(t['category'], 0) + amount

        fig, ax = plt.subplots(figsize=(8, 5))
        ax.bar(categories.keys(), categories.values(), color='#00C853')
        ax.set_title("Expenses and Income", color='#FFFFFF', fontsize=14)
        ax.set_ylabel("Amount (€)", color='#FFFFFF', fontsize=12)
        ax.set_xlabel("Categories", color='#FFFFFF', fontsize=12)
        ax.tick_params(axis='x', colors='#FFFFFF')
        ax.tick_params(axis='y', colors='#FFFFFF')
        ax.set_facecolor('#142C6B')
        fig.set_facecolor('#0A1F44')

        graph_window = ctk.CTkToplevel(self)
        graph_window.title("Chart")
        graph_window.geometry("600x400")
        graph_window.configure(fg_color="#0A1F44")
        self.fade_in(graph_window)

        canvas = FigureCanvasTkAgg(fig, master=graph_window)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def show_overview(self):
        self.main_frame.pack_forget()
        self.overview_frame.pack(fill="both", expand=True)
        for widget in self.overview_frame.winfo_children():
            widget.destroy()

        header = CTkFrame(self.overview_frame, corner_radius=0, fg_color="#142C6B")
        header.pack(fill="x")
        CTkLabel(header, text="Account Overview", font=("Helvetica", 20, "bold"), text_color="#FFFFFF").pack(side="left", padx=10, pady=10)
        CTkButton(header, text="Back", command=self.show_main_frame, corner_radius=10, fg_color="#FFFFFF", text_color="#0A1F44", width=100).pack(side="right", padx=10, pady=10)

        summary_frame = CTkFrame(self.overview_frame, corner_radius=10, fg_color="#1E3A8A")
        summary_frame.pack(pady=10, padx=20, fill="x")
        total_balance = sum(acc['balance'] for acc in self.accounts)
        CTkLabel(summary_frame, text=f"Total Balance: {total_balance:.2f} €", font=("Helvetica", 16, "bold"), text_color="#00C853").pack(pady=5)
        monthly_expenses = self.calculate_monthly_expenses()
        for month, amount in monthly_expenses.items():
            CTkLabel(summary_frame, text=f"{month}: -{amount:.2f} €", font=("Helvetica", 14), text_color="#FF5252").pack(pady=2)

        alerts_frame = CTkFrame(self.overview_frame, corner_radius=10, fg_color="#1E3A8A")
        alerts_frame.pack(pady=10, padx=20, fill="x")
        CTkLabel(alerts_frame, text="Alerts", font=("Helvetica", 16, "bold"), text_color="#FFFFFF").pack(pady=5)
        for acc in self.accounts:
            if acc['balance'] < 0:
                CTkLabel(alerts_frame, text=f"Overdraft Alert: {acc['name']} ({acc['balance']:.2f} €)", font=("Helvetica", 14), text_color="#FF5252").pack(pady=2)
            elif acc['balance'] < 100:
                CTkLabel(alerts_frame, text=f"Low Balance Warning: {acc['name']} ({acc['balance']:.2f} €)", font=("Helvetica", 14), text_color="#FF5252").pack(pady=2)

        CTkButton(self.overview_frame, text="Show Chart", command=self.show_graph, corner_radius=10, fg_color="#FFFFFF", text_color="#0A1F44", width=150).pack(pady=10)

    def calculate_monthly_expenses(self):
        expenses = {}
        with app.app_context():
            for account in self.accounts:
                result, status = get_transactions(self.token, account['id'])
                if status == 200:
                    for t in result:
                        if t['type'] in ['withdrawal', 'transfer']:
                            month = t['date'][:7]
                            amount = float(t['amount'])
                            if t['type'] == 'transfer' and t['destination_account_id'] not in [a['id'] for a in self.accounts]:
                                expenses[month] = expenses.get(month, 0) + amount
                            elif t['type'] == 'withdrawal':
                                expenses[month] = expenses.get(month, 0) + amount
        return expenses

    def load_clients(self):
        for widget in self.clients_frame.winfo_children():
            widget.destroy()
        
        with app.app_context():
            all_accounts_result, status = get_all_accounts(self.token)
            if status == 200:
                self.all_accounts = all_accounts_result
            else:
                CTkLabel(self.clients_frame, text="Error loading accounts.", font=("Helvetica", 14), text_color="#FF5252").pack(pady=10)
                return
            
            self.clients = User.query.filter_by(banker_id=self.current_id).all()
            if not self.clients:
                CTkLabel(self.clients_frame, text="No clients assigned yet.", font=("Helvetica", 14), text_color="#FFFFFF").pack(pady=10)
                return

        for i, client in enumerate(self.clients):
            frame = CTkFrame(self.clients_frame, corner_radius=10, fg_color="#1E3A8A")
            frame.grid(row=i, column=0, sticky="ew", padx=5, pady=5)
            name = f"{client.last_name} {client.first_name}"
            email = client.email
            client_id = client.id
            client_accounts = [acc for acc in self.all_accounts if str(acc['user_id']) == str(client_id)]
            
            alert_text = ""
            for acc in client_accounts:
                if acc['balance'] < 0:
                    alert_text = " [Overdraft Alert]"
                    break
                elif acc['balance'] < 100:
                    alert_text = " [Low Balance Warning]"
                    break

            CTkLabel(frame, text=f"{name} ({email}){alert_text}", font=("Helvetica", 14), text_color="#FF5252" if alert_text else "#FFFFFF").pack(side="left", padx=10)
            CTkButton(frame, text="Details", command=lambda c=client: self.show_client_details(c), corner_radius=10, fg_color="#FFFFFF", text_color="#0A1F44", width=100).pack(side="right", padx=5)
            CTkButton(frame, text="Message", command=lambda c=client: self.send_message(c), corner_radius=10, fg_color="#FFFFFF", text_color="#0A1F44", width=100).pack(side="right", padx=5)

    def show_client_details(self, client):
        self.client_window = ctk.CTkToplevel(self)
        self.client_window.title(f"Details for {client.last_name}")
        self.client_window.geometry("600x500")
        self.client_window.configure(fg_color="#0A1F44")
        self.fade_in(self.client_window)
        frame = CTkFrame(self.client_window, corner_radius=10, fg_color="#142C6B")
        frame.pack(pady=20, padx=20, fill="both", expand=True)
        name = f"{client.last_name} {client.first_name}"
        email = client.email
        CTkLabel(frame, text=f"Client: {name}", font=("Helvetica", 18, "bold"), text_color="#FFFFFF").pack(pady=10)
        CTkLabel(frame, text=f"Email: {email}", font=("Helvetica", 14), text_color="#FFFFFF").pack(pady=5)
        
        accounts_label = CTkLabel(frame, text="Accounts:", font=("Helvetica", 16, "bold"), text_color="#FFFFFF")
        accounts_label.pack(pady=5)
        accounts_frame = CTkScrollableFrame(frame, width=560, height=150, fg_color="#1E3A8A")
        accounts_frame.pack(pady=5)
        client_id = client.id
        client_accounts = [acc for acc in self.all_accounts if str(acc['user_id']) == str(client_id)]
        for i, acc in enumerate(client_accounts):
            alert_text = " (Overdraft)" if acc['balance'] < 0 else " (Low Balance)" if acc['balance'] < 100 else ""
            CTkLabel(accounts_frame, text=f"Account Name: {acc['name']} - Balance: {acc['balance']} €{alert_text}", font=("Helvetica", 12), text_color="#FF5252" if alert_text else "#FFFFFF").grid(row=i, column=0, padx=5, pady=2)

        transactions_label = CTkLabel(frame, text="Transactions:", font=("Helvetica", 16, "bold"), text_color="#FFFFFF")
        transactions_label.pack(pady=5)
        transactions_frame = CTkScrollableFrame(frame, width=560, height=150, fg_color="#1E3A8A")
        transactions_frame.pack(pady=5)
        row = 0
        for acc in client_accounts:
            result, status = get_transactions(self.token, acc['id'])
            if status == 200:
                for t in result:
                    frame_t = CTkFrame(transactions_frame, corner_radius=5, fg_color="#0A1F44")
                    frame_t.grid(row=row, column=0, sticky="ew", padx=5, pady=2)
                    CTkLabel(frame_t, text=f"{t['description']} - {t['amount']} €", font=("Helvetica", 12), text_color="#FFFFFF").pack(side="left", padx=5)
                    CTkButton(frame_t, text="Edit", command=lambda t=t: self.edit_transaction(t), corner_radius=5, fg_color="#FFFFFF", text_color="#0A1F44", width=50).pack(side="right", padx=5)
                    row += 1

        CTkButton(frame, text="Add Transaction", command=lambda c=client: self.add_transaction_for_client(c), corner_radius=10, fg_color="#FFFFFF", text_color="#0A1F44", width=150).pack(pady=10)

    def add_transaction_for_client(self, client):
        client_id = client.id
        client_accounts = [acc for acc in self.all_accounts if str(acc['user_id']) == str(client_id)]
        
        self.transaction_window = ctk.CTkToplevel(self)
        self.transaction_window.title("Add Transaction for Client")
        self.transaction_window.geometry("400x450")
        self.transaction_window.configure(fg_color="#0A1F44")
        self.fade_in(self.transaction_window)
        frame = CTkFrame(self.transaction_window, corner_radius=10, fg_color="#142C6B")
        frame.pack(pady=20, padx=20, fill="both", expand=True)
        CTkLabel(frame, text=f"Add Transaction for {client.last_name}", font=("Helvetica", 18, "bold"), text_color="#FFFFFF").pack(pady=10)
        self.client_account_combo = CTkComboBox(frame, values=[acc['name'] for acc in client_accounts], fg_color="#1E3A8A", text_color="#FFFFFF")
        self.client_account_combo.pack(pady=10)
        self.client_transaction_type = CTkComboBox(frame, values=["deposit", "withdrawal", "transfer"], fg_color="#1E3A8A", text_color="#FFFFFF", command=self.toggle_client_transaction_fields)
        self.client_transaction_type.pack(pady=10)
        self.client_description_entry = CTkEntry(frame, placeholder_text="Description", width=250, corner_radius=8, fg_color="#1E3A8A", text_color="#FFFFFF")
        self.client_description_entry.pack(pady=10)
        self.client_amount_entry = CTkEntry(frame, placeholder_text="Amount", width=250, corner_radius=8, fg_color="#1E3A8A", text_color="#FFFFFF")
        self.client_amount_entry.pack(pady=10)
        self.client_category_combo = CTkComboBox(frame, values=["Leisure", "Meal", "Bribe", "Income", "Other"], fg_color="#1E3A8A", text_color="#FFFFFF")
        self.client_category_combo.pack(pady=10)
        self.client_dest_account_label = CTkLabel(frame, text="Destination Account", font=("Helvetica", 14), text_color="#FFFFFF")
        self.client_dest_account_combo = CTkComboBox(frame, values=[acc['name'] for acc in client_accounts if acc['name'] != self.client_account_combo.get()], fg_color="#1E3A8A", text_color="#FFFFFF")
        self.client_dest_account_label.pack_forget()
        self.client_dest_account_combo.pack_forget()
        CTkButton(frame, text="Submit", command=lambda: self.submit_transaction_for_client(client), corner_radius=25, fg_color="#00C853", text_color="#FFFFFF", width=150).pack(pady=20)

    def toggle_client_transaction_fields(self, choice):
        if choice == "transfer":
            self.client_dest_account_label.pack(pady=5)
            self.client_dest_account_combo.pack(pady=10)
            self.client_dest_account_combo.configure(values=[acc['name'] for acc in self.all_accounts if acc['name'] != self.client_account_combo.get()])
        else:
            self.client_dest_account_label.pack_forget()
            self.client_dest_account_combo.pack_forget()

    def submit_transaction_for_client(self, client):
        account_name = self.client_account_combo.get()
        client_id = client.id
        client_accounts = [acc for acc in self.all_accounts if str(acc['user_id']) == str(client_id)]
        account_id = next((acc['id'] for acc in client_accounts if acc['name'] == account_name), None)
        transaction_type = self.client_transaction_type.get()
        description = self.client_description_entry.get()
        amount = self.client_amount_entry.get()
        category = self.client_category_combo.get()
        dest_name = self.client_dest_account_combo.get() if transaction_type == "transfer" else None
        dest_account_id = None if not dest_name else next((acc['id'] for acc in self.all_accounts if acc['name'] == dest_name), None)
        
        if not all([account_id, description, amount]):
            tk.messagebox.showerror("Error", "Please fill in all mandatory fields.")
            return
        try:
            amount = float(amount)
        except ValueError:
            tk.messagebox.showerror("Error", "Amount must be a valid number.")
            return
        
        with app.app_context():
            result, status = add_transaction(self.token, account_id, f"TX{random.randint(1000, 9999)}", description, amount, transaction_type, category, dest_account_id)
            if status == 201:
                tk.messagebox.showinfo("Success", "Transaction added successfully!")
                self.fade_out(self.transaction_window)
                self.show_client_details(client)
            else:
                tk.messagebox.showerror("Error", result.get('error', 'Unknown error'))

    def edit_transaction(self, transaction):
        self.edit_window = ctk.CTkToplevel(self)
        self.edit_window.title("Edit Transaction")
        self.edit_window.geometry("400x300")
        self.edit_window.configure(fg_color="#0A1F44")
        self.fade_in(self.edit_window)
        frame = CTkFrame(self.edit_window, corner_radius=10, fg_color="#142C6B")
        frame.pack(pady=20, padx=20, fill="both", expand=True)
        CTkLabel(frame, text="Edit Transaction", font=("Helvetica", 18, "bold"), text_color="#FFFFFF").pack(pady=10)
        self.edit_desc_entry = CTkEntry(frame, placeholder_text="Description", width=250, fg_color="#1E3A8A", text_color="#FFFFFF")
        self.edit_desc_entry.insert(0, transaction['description'])
        self.edit_desc_entry.pack(pady=10)
        self.edit_amount_entry = CTkEntry(frame, placeholder_text="Amount", width=250, fg_color="#1E3A8A", text_color="#FFFFFF")
        self.edit_amount_entry.insert(0, transaction['amount'])
        self.edit_amount_entry.pack(pady=10)
        CTkButton(frame, text="Save", command=lambda: self.save_transaction(transaction), corner_radius=25, fg_color="#00C853", text_color="#FFFFFF", width=150).pack(pady=20)

    def save_transaction(self, transaction):
        new_desc = self.edit_desc_entry.get()
        new_amount = self.edit_amount_entry.get()
        try:
            float(new_amount)
        except ValueError:
            tk.messagebox.showerror("Error", "Amount must be a valid number.")
            return
        transaction['description'] = new_desc
        transaction['amount'] = float(new_amount)
        tk.messagebox.showinfo("Success", "Transaction updated successfully!")
        self.fade_out(self.edit_window)
        self.show_admin_frame()

    def send_message(self, client):
        self.message_window = ctk.CTkToplevel(self)
        self.message_window.title(f"Message to {client.last_name}")
        self.message_window.geometry("400x300")
        self.message_window.configure(fg_color="#0A1F44")
        self.fade_in(self.message_window)
        frame = CTkFrame(self.message_window, corner_radius=10, fg_color="#142C6B")
        frame.pack(pady=20, padx=20, fill="both", expand=True)
        name = f"{client.last_name} {client.first_name}"
        CTkLabel(frame, text=f"Send Message to {name}", font=("Helvetica", 18, "bold"), text_color="#FFFFFF").pack(pady=10)
        self.message_entry = CTkEntry(frame, placeholder_text="Your message", width=300, height=100, corner_radius=8, fg_color="#1E3A8A", text_color="#FFFFFF")
        self.message_entry.pack(pady=10)
        CTkButton(frame, text="Send", command=lambda: self.confirm_message(client), corner_radius=25, fg_color="#FFFFFF", text_color="#0A1F44").pack(pady=20)

    def confirm_message(self, client):
        message = self.message_entry.get()
        if not message:
            tk.messagebox.showerror("Error", "Please enter a message.")
            return
        tk.messagebox.showinfo("Success", f"Message sent to {client.last_name}: {message}")
        self.fade_out(self.message_window)

    def show_all_transactions(self):
        self.clients_frame.pack_forget()
        self.all_transactions_frame.pack(fill="both", expand=True)
        for widget in self.all_transactions_frame.winfo_children():
            widget.destroy()
        header = CTkFrame(self.all_transactions_frame, corner_radius=0, fg_color="#142C6B")
        header.pack(fill="x")
        CTkLabel(header, text="All Transactions", font=("Helvetica", 20, "bold"), text_color="#FFFFFF").pack(side="left", padx=10, pady=10)
        CTkButton(header, text="Back", command=self.show_admin_frame, corner_radius=10, fg_color="#FFFFFF", text_color="#0A1F44", width=100).pack(side="right", padx=10, pady=10)
        transactions_list = CTkScrollableFrame(self.all_transactions_frame, width=960, height=500, corner_radius=0, fg_color="#0A1F44")
        transactions_list.pack(pady=10, padx=20, fill="both", expand=True)
        all_transactions = []
        with app.app_context():
            for account in self.all_accounts:
                result, status = get_transactions(self.token, account['id'])
                if status == 200:
                    all_transactions.extend(result)
        for i, transaction in enumerate(all_transactions):
            frame = CTkFrame(transactions_list, corner_radius=10, fg_color="#1E3A8A")
            frame.grid(row=i, column=0, sticky="ew", padx=5, pady=5)
            CTkLabel(frame, text=f"{transaction['description']} (Account {transaction['account_id']})", font=("Helvetica", 14), text_color="#FFFFFF").pack(side="left", padx=10)
            amount_str = f"+{transaction['amount']:.2f}" if transaction['type'] == 'deposit' else f"-{transaction['amount']:.2f}"
            CTkLabel(frame, text=amount_str + " €", font=("Helvetica", 14, "bold"), text_color="#00C853" if transaction['type'] == 'deposit' else "#FF5252").pack(side="right", padx=10)
            CTkLabel(frame, text=transaction['date'].split('T')[0], font=("Helvetica", 12), text_color="#B0C4DE").pack(side="right", padx=10)

    def add_client_window(self):
        self.add_client_win = ctk.CTkToplevel(self)
        self.add_client_win.title("Add Client")
        self.add_client_win.geometry("400x300")
        self.add_client_win.configure(fg_color="#0A1F44")
        self.fade_in(self.add_client_win)
        frame = CTkFrame(self.add_client_win, corner_radius=10, fg_color="#142C6B")
        frame.pack(pady=20, padx=20, fill="both", expand=True)
        CTkLabel(frame, text="Add Existing Client", font=("Helvetica", 18, "bold"), text_color="#FFFFFF").pack(pady=10)
        
        with app.app_context():
            all_users = User.query.filter(User.banker_id.is_(None)).all()
            user_emails = [user.email for user in all_users]
        
        self.client_email_combo = CTkComboBox(frame, values=user_emails, fg_color="#1E3A8A", text_color="#FFFFFF", width=250)
        self.client_email_combo.pack(pady=10)
        CTkButton(frame, text="Add Client", command=self.add_client_to_banker, corner_radius=25, fg_color="#FFFFFF", text_color="#0A1F44").pack(pady=20)

    def add_client_to_banker(self):
        email = self.client_email_combo.get()
        if not email:
            tk.messagebox.showerror("Error", "Please select a client email.")
            return
        with app.app_context():
            client = User.query.filter_by(email=email).first()
            if client:
                if client.banker_id is not None:
                    tk.messagebox.showerror("Error", f"Client {client.last_name} is already assigned to a banker.")
                    return
                client.banker_id = self.current_id
                db.session.commit()
                tk.messagebox.showinfo("Success", f"Client {client.last_name} added successfully!")
                self.fade_out(self.add_client_win)
                self.load_clients()  # Recharge immédiatement la liste des clients
            else:
                tk.messagebox.showerror("Error", "Client not found in the database.")

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