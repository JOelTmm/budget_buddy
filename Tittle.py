import customtkinter as ctk
import mysql.connector


class BudgetBuddyApp:
    def __init__(self, root):
        # Initialize the app with the root window
        self.root = root
        self.root.geometry("600x400")
        self.root.title("Budget Buddy")
        ctk.set_appearance_mode("dark")

        # Set initial user and account details
        self.current_user = 1
        self.current_account = 1

        # Fetch and organize account data
        self.accounts_data = self.get_accounts()
        self.user_account = self.organize_accounts()

        # Initialize display with the first account
        self.account_name = list(self.user_account[self.current_user][0].keys())[self.current_account - 1]
        self.account_balance = list(self.user_account[self.current_user][0].values())[self.current_account - 1]

        # Title label with account name and balance
        self.title_label = ctk.CTkLabel(self.root, text=f"{self.account_name} : {self.account_balance} €", font=("Arial", 18, "bold"))
        self.title_label.pack(pady=10)
        self.title_label.bind("<Button-1>", lambda e: self.on_title_click())

        # Main frame
        self.frame = ctk.CTkFrame(self.root, width=550, height=300)
        self.frame.pack(padx=10, pady=10, fill="both", expand=True)

    def get_accounts(self):
        # Connect to MySQL and fetch account data
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="admin",
            database="finance"
        )
        cursor = conn.cursor()
        cursor.execute("SELECT user_id, account_name, balance FROM account")
        accounts_data = cursor.fetchall()
        conn.close()
        return accounts_data

    def organize_accounts(self):
        # Organize accounts data by user_id
        user_account = {}
        for user_id, account_name, balance in self.accounts_data:
            if user_id not in user_account:
                user_account[user_id] = []
            user_account[user_id].append({account_name: balance})
        return user_account

    def update_account_display(self, account_name, balance):
        # Update the display with the selected account and balance
        self.title_label.configure(text=f"{account_name} : {balance} €")

    def on_title_click(self):
        # Display account options when the title is clicked
        account_names = [list(account.keys())[0] for account in self.user_account[self.current_user]]
        balances = [list(account.values())[0] for account in self.user_account[self.current_user]]

        def on_account_selected(selected_account):
            # Handle account selection
            account_index = account_names.index(selected_account)
            selected_balance = balances[account_index]
            self.update_account_display(selected_account, selected_balance)
            self.option_menu.place_forget()

        # Create an option menu for selecting accounts
        self.option_menu = ctk.CTkOptionMenu(self.root, values=account_names, command=on_account_selected)
        self.option_menu.place(x=self.title_label.winfo_x(), y=self.title_label.winfo_y() + self.title_label.winfo_height())


if __name__ == "__main__":
    # Initialize and run the application
    root = ctk.CTk()
    app = BudgetBuddyApp(root)
    root.mainloop()
