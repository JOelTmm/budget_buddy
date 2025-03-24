from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit, QTableWidget, QTableWidgetItem, QMessageBox, QComboBox, QFormLayout
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
import sys
from appV2 import app, db, register_user, login_user, create_account, add_transaction, get_transactions, get_balance, list_accounts, token_required
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
from decimal import Decimal
import random  
class BankingApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Revolut Clone")
        self.setGeometry(100, 100, 600, 700)
        self.token = None
        self.current_user_id = None
        self.graph_window = None
        self.accounts = []
        with app.app_context():
            db.create_all()
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout()

        # Écran de login
        self.login_widget = QWidget()
        login_layout = QFormLayout()
        self.email_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        login_button = QPushButton("Login")
        login_button.clicked.connect(self.login)
        login_layout.addRow("Email:", self.email_input)
        login_layout.addRow("Password:", self.password_input)
        login_layout.addWidget(login_button)
        self.login_widget.setLayout(login_layout)
        self.layout.addWidget(self.login_widget)

        # Interface principale (cachée au départ)
        self.main_widget = QWidget()
        main_layout = QVBoxLayout()

        self.balance_label = QLabel("Solde: 0.00 €")
        self.balance_label.setFont(QFont("Arial", 24))
        main_layout.addWidget(self.balance_label, alignment=Qt.AlignmentFlag.AlignCenter)

        self.transaction_table = QTableWidget()
        self.transaction_table.setColumnCount(4)
        self.transaction_table.setHorizontalHeaderLabels(["Nom", "Montant", "Date", "Catégorie"])
        main_layout.addWidget(self.transaction_table)

        self.filter_box = QComboBox()
        self.filter_box.addItems(["Tous", "Loisir", "Voyage", "Abonnement", "Revenu", "Autre"])
        self.filter_box.currentIndexChanged.connect(self.filter_transactions)
        main_layout.addWidget(self.filter_box)

        add_button = QPushButton("Ajouter une transaction")
        add_button.clicked.connect(self.open_transaction_window)
        main_layout.addWidget(add_button)

        graph_button = QPushButton("Afficher le graphique")
        graph_button.clicked.connect(self.show_graph)
        main_layout.addWidget(graph_button)

        self.main_widget.setLayout(main_layout)
        self.layout.addWidget(self.main_widget)
        self.main_widget.hide()  # Caché jusqu’au login

        self.setLayout(self.layout)

    def login(self):
        email = self.email_input.text()
        password = self.password_input.text()
        with app.app_context():
            result, status = login_user(email, password)
        if status == 200:
            self.token = result['token']
            self.login_widget.hide()
            self.main_widget.show()
            self.load_accounts()
            self.update_balance()
            self.load_transactions()
        else:
            QMessageBox.warning(self, "Erreur", result['error'])

    def load_accounts(self):
        with app.app_context():
            result, status = list_accounts(self.token)
            if status == 200:
                self.accounts = result['accounts']

    def update_balance(self):
        total_balance = sum(acc['balance'] for acc in self.accounts)
        self.balance_label.setText(f"Solde: {total_balance:.2f} €")

    def load_transactions(self, category_filter="Tous"):
        self.transaction_table.setRowCount(0)
        if not self.accounts:
            return
        with app.app_context():
            for account in self.accounts:
                result, status = get_transactions(self.token, account['id'])
                if status == 200:
                    for row, transaction in enumerate(result):
                        if category_filter == "Tous" or category_filter == transaction['category']:
                            self.transaction_table.insertRow(self.transaction_table.rowCount())
                            self.transaction_table.setItem(row, 0, QTableWidgetItem(transaction['description']))
                            amount_str = f"{transaction['amount']:+.2f}" if transaction['type'] in ['deposit', 'transfer'] else f"-{transaction['amount']:.2f}"
                            self.transaction_table.setItem(row, 1, QTableWidgetItem(amount_str))
                            self.transaction_table.setItem(row, 2, QTableWidgetItem(transaction['date'].split('T')[0]))
                            self.transaction_table.setItem(row, 3, QTableWidgetItem(transaction['category']))

    def filter_transactions(self):
        selected_category = self.filter_box.currentText()
        self.load_transactions(selected_category)

    def open_transaction_window(self):
        self.transaction_window = QWidget()
        self.transaction_window.setWindowTitle("Ajouter une transaction")
        self.transaction_window.setGeometry(200, 200, 300, 300)

        layout = QVBoxLayout()
        form_layout = QFormLayout()

        self.account_combo = QComboBox()
        for i, acc in enumerate(self.accounts, 1):
            self.account_combo.addItem(f"{i}. {acc['name']} (ID: {acc['id']})", acc['id'])
        self.transaction_type = QComboBox()
        self.transaction_type.addItems(["deposit", "withdrawal", "transfer"])
        self.description_input = QLineEdit()
        self.amount_input = QLineEdit()
        self.category_input = QComboBox()
        self.category_input.addItems(["Loisir", "Voyage", "Abonnement", "Revenu", "Autre"])
        self.dest_account_combo = QComboBox()
        self.dest_account_combo.addItem("None", None)
        for i, acc in enumerate(self.accounts, 1):
            self.dest_account_combo.addItem(f"{i}. {acc['name']} (ID: {acc['id']})", acc['id'])

        form_layout.addRow("Compte source:", self.account_combo)
        form_layout.addRow("Type:", self.transaction_type)
        form_layout.addRow("Description:", self.description_input)
        form_layout.addRow("Montant:", self.amount_input)
        form_layout.addRow("Catégorie:", self.category_input)
        form_layout.addRow("Compte destination (transfert):", self.dest_account_combo)

        layout.addLayout(form_layout)

        save_button = QPushButton("Ajouter")
        save_button.clicked.connect(self.add_transaction)
        layout.addWidget(save_button)

        self.transaction_window.setLayout(layout)
        self.transaction_window.show()

    def add_transaction(self):
        account_id = self.account_combo.currentData()
        transaction_type = self.transaction_type.currentText()
        description = self.description_input.text()
        amount = self.amount_input.text()
        category = self.category_input.currentText()
        dest_account_id = self.dest_account_combo.currentData()

        if not description or not amount:
            QMessageBox.warning(self, "Erreur", "Veuillez remplir tous les champs.")
            return

        try:
            float(amount)
        except ValueError:
            QMessageBox.warning(self, "Erreur", "Le montant doit être un nombre valide.")
            return

        with app.app_context():
            result, status = add_transaction(
                self.token, account_id, f"TX{random.randint(1000, 9999)}", description, amount, transaction_type, category, dest_account_id
            )
            if status == 201:
                self.load_accounts()
                self.update_balance()
                self.load_transactions()
                self.transaction_window.close()
            else:
                QMessageBox.warning(self, "Erreur", result['error'])

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

        fig, ax = plt.subplots()
        ax.bar(categories.keys(), categories.values(), color='blue')
        ax.set_title("Dépenses et revenus par catégorie")
        ax.set_ylabel("Montant (€)")

        if self.graph_window is None:
            self.graph_window = QWidget()
            self.graph_window.setWindowTitle("Graphique des finances")
            layout = QVBoxLayout()
            self.canvas = FigureCanvas(fig)
            layout.addWidget(self.canvas)
            self.graph_window.setLayout(layout)
        else:
            self.canvas.figure = fig
            self.canvas.draw()

        self.graph_window.show()

if __name__ == "__main__":
    qt_app = QApplication(sys.argv)
    window = BankingApp()
    window.show()
    sys.exit(qt_app.exec())