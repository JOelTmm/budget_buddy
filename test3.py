import customtkinter as ctk
import mysql.connector
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class BudgetBuddyApp:
    def __init__(self, root, current_user=1):
        self.root = root
        self.current_user = current_user
        self.root.geometry("800x600")
        self.root.title("Budget Buddy - Overview")

        ctk.set_appearance_mode("dark")
        
        # Connexion à la base de données
        self.conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="admin",
            database="finance"
        )
        self.cursor = self.conn.cursor()
        
        # Frame principal scrollable
        self.scroll_frame = ctk.CTkScrollableFrame(self.root, width=780, height=580)
        self.scroll_frame.pack(padx=10, pady=10, fill="both", expand=True)
        
        self.create_overview_page()

    def create_overview_page(self):
        # Titre principal
        title_label = ctk.CTkLabel(self.scroll_frame, text="Account Overview", font=("Arial", 18, "bold"))
        title_label.pack(pady=10)

        # Affichage des soldes des comptes
        self.show_account_balances()

        # Affichage des dépenses mensuelles
        self.show_monthly_expenses()

        # Affichage des alertes (comptes à découvert)
        self.show_alerts()

        # Affichage du graphique des transactions par seconde
        self.show_transaction_graph_by_second()

    def show_account_balances(self):
        query = """
        SELECT account_name, balance
        FROM account
        WHERE user_id = %s
        """
        self.cursor.execute(query, (self.current_user,))
        accounts = self.cursor.fetchall()

        account_label = ctk.CTkLabel(self.scroll_frame, text="Account Balances:", font=("Arial", 14, "bold"))
        account_label.pack(pady=10)

        for account_name, balance in accounts:
            balance_label = ctk.CTkLabel(self.scroll_frame, text=f"{account_name}: {balance}€")
            balance_label.pack(anchor="w", padx=10)

    def show_monthly_expenses(self):
        query = """
        SELECT YEAR(transaction_date) AS year, MONTH(transaction_date) AS month, SUM(amount) AS total_expenses
        FROM transaction
        WHERE transaction_type = 'withdrawal' AND account_id IN (SELECT account_id FROM account WHERE user_id = %s)
        GROUP BY YEAR(transaction_date), MONTH(transaction_date)
        """
        self.cursor.execute(query, (self.current_user,))
        monthly_expenses = self.cursor.fetchall()

        months = []
        expenses = []
        for year, month, total_expenses in monthly_expenses:
            months.append(f"{month}/{year}")
            expenses.append(total_expenses)

        self.plot_expenses(months, expenses)

    def plot_expenses(self, months, expenses):
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.bar(months, expenses, color='skyblue')
        ax.set_title("Monthly Expenses")
        ax.set_xlabel("Month")
        ax.set_ylabel("Expenses (€)")

        canvas = FigureCanvasTkAgg(fig, self.scroll_frame)
        canvas.get_tk_widget().pack(pady=20)
        canvas.draw()

    def show_alerts(self):
        query = """
        SELECT account_name, balance
        FROM account
        WHERE user_id = %s AND balance < 0
        """
        self.cursor.execute(query, (self.current_user,))
        overdraft_accounts = self.cursor.fetchall()

        if overdraft_accounts:
            alert_label = ctk.CTkLabel(self.scroll_frame, text="⚠️ Overdraft Alert!", font=("Arial", 14, "bold"), text_color="red")
            alert_label.pack(pady=10)

            for account_name, balance in overdraft_accounts:
                account_alert_label = ctk.CTkLabel(self.scroll_frame, text=f"{account_name} is overdrafted: {balance}€")
                account_alert_label.pack(anchor="w", padx=10)

    def show_transaction_graph_by_second(self):
        query = """
        SELECT 
            DATE_FORMAT(transaction_date, '%Y-%m-%d %H:%i:%s') AS transaction_second,
            SUM(amount) AS total_amount
        FROM 
            transaction
        WHERE 
            transaction_type IN ('transfer', 'withdrawal', 'deposit')
        GROUP BY 
            transaction_second
        ORDER BY 
            transaction_second;
        """
        self.cursor.execute(query)
        transaction_data = self.cursor.fetchall()

        times = [data[0] for data in transaction_data]
        amounts = [data[1] for data in transaction_data]

        self.plot_transactions_by_second(times, amounts)

    def plot_transactions_by_second(self, times, amounts):
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(times, amounts, marker='o', color='green', linestyle='-', markersize=5)
        ax.set_title("Transactions by Second")
        ax.set_xlabel("Time (second)")
        ax.set_ylabel("Amount (€)")
        ax.tick_params(axis='x', rotation=45)

        canvas = FigureCanvasTkAgg(fig, self.scroll_frame)
        canvas.get_tk_widget().pack(pady=20)
        canvas.draw()

if __name__ == "__main__":
    root = ctk.CTk()
    app = BudgetBuddyApp(root)
    root.mainloop()
