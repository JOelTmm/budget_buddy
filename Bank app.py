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
        self.configure(fg_color="#0A1F44")
        self.token = None
        self.accounts = []
        with app.app_context():
            db.create_all()
        self.init_ui()

    def init_ui(self):
        self.show_login_screen()
    
    def show_login_screen(self):
        self.clear_screen()
        self.login_frame = CTkFrame(self, corner_radius=10, fg_color="#142C6B")
        self.login_frame.pack(pady=50, padx=20, fill="both", expand=True)

        ctk.CTkLabel(self.login_frame, text="Revolut", font=("Helvetica", 30, "bold"), text_color="#FFFFFF").pack(pady=30)
        
        self.email_entry = CTkEntry(self.login_frame, placeholder_text="Email", width=300)
        self.email_entry.pack(pady=10)
        
        self.password_entry = CTkEntry(self.login_frame, placeholder_text="Mot de passe", show="*", width=300)
        self.password_entry.pack(pady=10)
        
        login_button = CTkButton(self.login_frame, text="Se connecter", command=self.login)
        login_button.pack(pady=10)
        
        register_button = CTkButton(self.login_frame, text="Créer un compte", command=self.show_register_screen)
        register_button.pack(pady=10)
    
    def show_register_screen(self):
        self.clear_screen()
        self.register_frame = CTkFrame(self, corner_radius=10, fg_color="#142C6B")
        self.register_frame.pack(pady=50, padx=20, fill="both", expand=True)

        ctk.CTkLabel(self.register_frame, text="Inscription", font=("Helvetica", 30, "bold"), text_color="#FFFFFF").pack(pady=30)
        
        self.reg_email_entry = CTkEntry(self.register_frame, placeholder_text="Email", width=300)
        self.reg_email_entry.pack(pady=10)
        
        self.reg_password_entry = CTkEntry(self.register_frame, placeholder_text="Mot de passe", show="*", width=300)
        self.reg_password_entry.pack(pady=10)
        
        register_button = CTkButton(self.register_frame, text="S'inscrire", command=self.register)
        register_button.pack(pady=20)
    
    def show_dashboard(self):
        self.clear_screen()
        self.main_frame = CTkFrame(self, corner_radius=0, fg_color="#0A1F44")
        self.main_frame.pack(pady=0, padx=0, fill="both", expand=True)
        
        self.accounts_frame = CTkFrame(self.main_frame)
        self.accounts_frame.pack(fill="x")
        self.load_accounts()
        
        self.transactions_frame = CTkScrollableFrame(self.main_frame, width=560, height=400)
        self.transactions_frame.pack(pady=10, padx=20)
        
        filter_frame = CTkFrame(self.main_frame)
        filter_frame.pack(fill="x", pady=10)
        
        self.filter_combo = CTkComboBox(filter_frame, values=["Tous", "Loisir", "Voyage", "Abonnement", "Revenu", "Autre"], command=self.filter_transactions)
        self.filter_combo.pack(side="left", padx=20)
        
        add_button = CTkButton(filter_frame, text="+ Transaction", command=self.open_transaction_window)
        add_button.pack(side="right", padx=20)
    
    def register(self):
        email = self.reg_email_entry.get()
        password = self.reg_password_entry.get()
        with app.app_context():
            result, status = register_user(email, password)
        if status == 201:
            self.show_login_screen()
        else:
            tk.messagebox.showerror("Erreur", result['error'])
    
    def login(self):
        email = self.email_entry.get()
        password = self.password_entry.get()
        with app.app_context():
            result, status = login_user(email, password)
        if status == 200:
            self.token = result['token']
            self.show_dashboard()
        else:
            tk.messagebox.showerror("Erreur", result['error'])
    
    def clear_screen(self):
        for widget in self.winfo_children():
            widget.destroy()
    
if __name__ == "__main__":
    app_gui = BankingApp()
    app_gui.mainloop()
