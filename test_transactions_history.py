import customtkinter as ctk
import mysql.connector

class TransactionHistory :
    def __init__(self):
        self.transactions = []
        self.transactions_text = ""

    def open_connection(self):
            self.conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="admin",
                database="finance"
            )
            self.cursor = self.conn.cursor()

    def display_transactions(self, frame, user):
        for index, (ref, desc, amount, date, type, id) in enumerate(self.transactions):
            if type == "withdrawal" or (type == "transfer" and id == user):
                self.transactions_text = f"{date} | {ref} | {desc} | -{amount}€"
            else :
                self.transactions_text = f"{date} | {ref} | {desc} | {amount}€"
            label = ctk.CTkLabel(frame, text=self.transactions_text, font=("Arial", 12))
            label.pack(anchor="w", padx=10, pady=2)
            
    def get_transactions(self, user, frame):
        self.open_connection()
        self.cursor.execute("SELECT reference, description, amount, transaction_date, transaction_type, account_id FROM transaction  WHERE account_id = %s OR destination_account_id = %s ORDER BY transaction_date DESC", (user, user))
        self.transactions = self.cursor.fetchall()
        self.conn.close()
        self.display_transactions(frame, user)

    def get_transactions_by_date(self, user, frame, date):
        self.open_connection()
        self.cursor.execute("SELECT reference, description, amount, transaction_date, transaction_type, account_id FROM transaction  WHERE (account_id = %s OR destination_account_id = %s) AND transaction_date LIKE %s ORDER BY transaction_date DESC", (user, user, f"%{date}%"))
        self.transactions = self.cursor.fetchall()
        self.conn.close()
        self.display_transactions(frame, user)

    def get_deposits(self, user, frame):
        self.open_connection()
        self.cursor.execute("SELECT reference, description, amount, transaction_date, transaction_type, account_id FROM transaction  WHERE (account_id = %s AND transaction_type = 'deposit') OR (transaction_type = 'transfer' AND destination_account_id = %s) ORDER BY transaction_date DESC", (user, user))
        self.transactions = self.cursor.fetchall()
        self.conn.close()
        self.display_transactions(frame, user)

    def get_withdrawals(self, user, frame):
        self.open_connection()
        self.cursor.execute("SELECT reference, description, amount, transaction_date, transaction_type, account_id FROM transaction  WHERE account_id = %s AND (transaction_type = 'withdrawal' OR transaction_type = 'transfer') ORDER BY transaction_date DESC", (user,))
        self.transactions = self.cursor.fetchall()
        self.conn.close()
        self.display_transactions(frame, user)