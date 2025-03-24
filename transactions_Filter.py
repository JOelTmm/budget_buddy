import customtkinter as ctk
import mysql.connector


class BudgetBuddyApp:
    def __init__(self, root, current_user=1, current_account=1):
        # Initialize the app with root window, user, and account details
        self.root = root
        self.current_user = current_user
        self.current_account = current_account

        # Establish MySQL connection
        self.conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="admin",
            database="finance"
        )
        self.cursor = self.conn.cursor()

        # Initialize the UI
        self.init_ui()

    def init_ui(self):
        # Set up the main frame for the UI
        self.frame = ctk.CTkFrame(self.root)
        self.frame.pack(padx=20, pady=20, fill="both", expand=True)

        # Initialize variables for filtering
        self.start_date_var = ctk.StringVar()
        self.end_date_var = ctk.StringVar()
        self.category_var = ctk.StringVar(value="all")
        self.amount_var = ctk.StringVar(value="")

        # Create and place the "Start Date" label and entry field
        ctk.CTkLabel(self.frame, text="Date de début :").pack(anchor="w")
        self.start_date_entry = ctk.CTkEntry(self.frame, textvariable=self.start_date_var)
        self.start_date_entry.pack(anchor="w", padx=10)

        # Create and place the "End Date" label and entry field
        ctk.CTkLabel(self.frame, text="Date de fin :").pack(anchor="w")
        self.end_date_entry = ctk.CTkEntry(self.frame, textvariable=self.end_date_var)
        self.end_date_entry.pack(anchor="w", padx=10)

        # Create and place the "Category" label and option menu
        ctk.CTkLabel(self.frame, text="Catégorie :").pack(anchor="w")
        self.category_menu = ctk.CTkOptionMenu(self.frame, variable=self.category_var, values=["all", "withdrawal", "deposit"])
        self.category_menu.pack(anchor="w", padx=10)

        # Create and place the "Amount Sort" label and option menu
        ctk.CTkLabel(self.frame, text="Tri par montant :").pack(anchor="w")
        self.amount_menu = ctk.CTkOptionMenu(self.frame, variable=self.amount_var, values=["", "croissant", "décroissant"])
        self.amount_menu.pack(anchor="w", padx=10)

        # Create and place the "Apply Filters" button
        self.search_button = ctk.CTkButton(self.frame, text="Appliquer les filtres", command=self.apply_filters)
        self.search_button.pack(pady=10)

        # Create and place the result frame for displaying transactions
        self.result_frame = ctk.CTkScrollableFrame(self.frame, height=300)
        self.result_frame.pack(padx=10, pady=10, fill="both", expand=True)

    def get_filtered_transactions(self):
        # Prepare the base query to get transactions
        query = """
        SELECT reference, description, amount, transaction_date, transaction_type, account_id, destination_account_id
        FROM transaction
        WHERE (account_id = %s OR destination_account_id = %s)
        """
        query_values = [self.current_account, self.current_account]

        # Get filter values
        start_date = self.start_date_var.get()
        end_date = self.end_date_var.get()
        category = self.category_var.get()
        amount_order = self.amount_var.get()

        # Filter by date range (if both start and end dates are provided)
        if start_date and end_date:
            query += " AND DATE(transaction_date) BETWEEN %s AND %s"
            query_values.extend([start_date, end_date])
        # Filter by specific start date (if end date is not provided)
        elif start_date and not end_date:
            query += " AND DATE(transaction_date) = %s"
            query_values.append(start_date)

        # Filter by category (if category is not 'all')
        if category and category != "all":
            if category == "withdrawal":
                query += " AND (transaction_type = %s OR (transaction_type = 'transfer' AND account_id = %s))"
                query_values.extend([category, self.current_account])
            elif category == "deposit":
                query += " AND (transaction_type = %s OR (transaction_type = 'transfer' AND destination_account_id = %s))"
                query_values.extend([category, self.current_account])

        # Sort by amount (ascending or descending)
        if amount_order == "croissant":
            query += " ORDER BY amount ASC"
        elif amount_order == "décroissant":
            query += " ORDER BY amount DESC"

        # Execute the query and fetch the results
        self.cursor.execute(query, query_values)
        self.transactions = self.cursor.fetchall()

    def display_transactions(self):
        # Clear any previous results from the result frame
        for widget in self.result_frame.winfo_children():
            widget.destroy()

        # Display each transaction in the result frame
        for ref, desc, amount, date, transaction_type, account_id, destination_account_id in self.transactions:
            if transaction_type == "transfer":
                if account_id == self.current_account:
                    transaction_text = f"{date} | {ref} | {desc} | -{amount}€ | Withdrawal"
                elif destination_account_id == self.current_account:
                    transaction_text = f"{date} | {ref} | {desc} | +{amount}€ | Deposit"
            elif transaction_type == "withdrawal":
                transaction_text = f"{date} | {ref} | {desc} | -{amount}€ | {transaction_type.capitalize()}"
            elif transaction_type == "deposit":
                transaction_text = f"{date} | {ref} | {desc} | +{amount}€ | {transaction_type.capitalize()}"

            # Create a label for each transaction and display it
            label = ctk.CTkLabel(self.result_frame, text=transaction_text, font=("Arial", 12))
            label.pack(anchor="w", padx=10, pady=2)

    def apply_filters(self):
        # Apply the filters and display the results
        self.get_filtered_transactions()
        self.display_transactions()


if __name__ == "__main__":
    # Initialize and run the application
    root = ctk.CTk()
    root.geometry("600x500")
    root.title("Budget Buddy")
    app = BudgetBuddyApp(root)
    root.mainloop()
