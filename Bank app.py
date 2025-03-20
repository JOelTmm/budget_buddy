from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit, QTableWidget, QTableWidgetItem, QMessageBox, QComboBox, QFormLayout
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
import sys
import random
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas

class BankingApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Revolut Clone")
        self.setGeometry(100, 100, 600, 700)
        self.transactions = [
            ("Starbucks", "+3.25", "Aujourd'hui", "Loisir"),
            ("Airbnb", "-100", "Hier", "Voyage"),
            ("Netflix", "-12.99", "15 Mars", "Abonnement"),
            ("Salaire", "+2500", "1 Mars", "Revenu")
        ]
        self.balance = 1905
        self.graph_window = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.balance_label = QLabel(f"Solde: {self.balance} €")
        self.balance_label.setFont(QFont("Arial", 24))
        layout.addWidget(self.balance_label, alignment=Qt.AlignmentFlag.AlignCenter)
        
        self.transaction_table = QTableWidget()
        self.transaction_table.setColumnCount(4)
        self.transaction_table.setHorizontalHeaderLabels(["Nom", "Montant", "Date", "Catégorie"])
        self.load_transactions()
        layout.addWidget(self.transaction_table)
        
        self.filter_box = QComboBox()
        self.filter_box.addItems(["Tous", "Loisir", "Voyage", "Abonnement", "Revenu"])
        self.filter_box.currentIndexChanged.connect(self.filter_transactions)
        layout.addWidget(self.filter_box)
        
        add_button = QPushButton("Ajouter une transaction")
        add_button.clicked.connect(self.open_transaction_window)
        layout.addWidget(add_button)
        
        graph_button = QPushButton("Afficher le graphique")
        graph_button.clicked.connect(self.show_graph)
        layout.addWidget(graph_button)
        
        self.setLayout(layout)
    
    def load_transactions(self, category_filter="Tous"):
        self.transaction_table.setRowCount(0)
        for row, (name, amount, date, category) in enumerate(self.transactions):
            if category_filter == "Tous" or category_filter == category:
                self.transaction_table.insertRow(row)
                self.transaction_table.setItem(row, 0, QTableWidgetItem(name))
                self.transaction_table.setItem(row, 1, QTableWidgetItem(amount))
                self.transaction_table.setItem(row, 2, QTableWidgetItem(date))
                self.transaction_table.setItem(row, 3, QTableWidgetItem(category))
    
    def filter_transactions(self):
        selected_category = self.filter_box.currentText()
        self.load_transactions(selected_category)
    
    def open_transaction_window(self):
        self.transaction_window = QWidget()
        self.transaction_window.setWindowTitle("Ajouter une transaction")
        self.transaction_window.setGeometry(200, 200, 300, 250)
        
        layout = QVBoxLayout()
        form_layout = QFormLayout()
        
        self.name_input = QLineEdit()
        self.amount_input = QLineEdit()
        self.date_input = QLineEdit()
        self.category_input = QComboBox()
        self.category_input.addItems(["Loisir", "Voyage", "Abonnement", "Revenu", "Autre"])
        
        form_layout.addRow("Nom:", self.name_input)
        form_layout.addRow("Montant:", self.amount_input)
        form_layout.addRow("Date:", self.date_input)
        form_layout.addRow("Catégorie:", self.category_input)
        
        layout.addLayout(form_layout)
        
        save_button = QPushButton("Ajouter")
        save_button.clicked.connect(self.add_transaction)
        layout.addWidget(save_button)
        
        self.transaction_window.setLayout(layout)
        self.transaction_window.show()
    
    def add_transaction(self):
        name = self.name_input.text()
        amount = self.amount_input.text()
        date = self.date_input.text()
        category = self.category_input.currentText()
        
        if not name or not amount or not date:
            QMessageBox.warning(self, "Erreur", "Veuillez remplir tous les champs.")
            return
        
        try:
            amount_value = float(amount)
        except ValueError:
            QMessageBox.warning(self, "Erreur", "Le montant doit être un nombre valide.")
            return
        
        self.transactions.append((name, f"{amount_value:+.2f}", date, category))
        self.load_transactions()
        self.transaction_window.close()
    
    def show_graph(self):
        categories = {}
        for _, amount, _, category in self.transactions:
            amount_value = float(amount.replace("+", "").replace("-", ""))
            categories[category] = categories.get(category, 0) + amount_value
        
        fig, ax = plt.subplots()
        ax.bar(categories.keys(), categories.values(), color='blue')
        ax.set_title("Dépenses par catégorie")
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
    app = QApplication(sys.argv)
    window = BankingApp()
    window.show()
    sys.exit(app.exec())
