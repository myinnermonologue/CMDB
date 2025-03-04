import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QLineEdit, QVBoxLayout, QWidget, QTableWidget, QTableWidgetItem
import sqlite3

class SKUDApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("СКУД - Авторизация")
        self.setGeometry(100, 100, 600, 400)
        
        self.initUI()
    
    def initUI(self):
        layout = QVBoxLayout()
        
        self.label_user = QLabel("Пользователь:")
        self.input_user = QLineEdit()
        layout.addWidget(self.label_user)
        layout.addWidget(self.input_user)
        
        self.label_pass = QLabel("Пароль:")
        self.input_pass = QLineEdit()
        self.input_pass.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.label_pass)
        layout.addWidget(self.input_pass)
        
        self.login_btn = QPushButton("Войти")
        self.login_btn.clicked.connect(self.authenticate)
        layout.addWidget(self.login_btn)
        
        self.data_table = QTableWidget()
        self.data_table.setColumnCount(3)
        self.data_table.setHorizontalHeaderLabels(["ID", "Техника", "Статус"])
        layout.addWidget(self.data_table)
        
        self.load_data_btn = QPushButton("Загрузить данные")
        self.load_data_btn.clicked.connect(self.load_data)
        layout.addWidget(self.load_data_btn)
        
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
    
    def authenticate(self):
        user = self.input_user.text()
        password = self.input_pass.text()
        
        if self.check_user_credentials(user, password):
            self.label_user.setText("Доступ разрешен")
            self.load_data()
        else:
            self.label_user.setText("Ошибка авторизации")
    
    def check_user_credentials(self, username, password):
        try:
            conn = sqlite3.connect('skud_db.sqlite')  # Подключение к базе SQLite
            cursor = conn.cursor()
            query = "SELECT * FROM users WHERE username = ? AND password = ?"
            cursor.execute(query, (username, password))
            result = cursor.fetchone()
            cursor.close()
            conn.close()
            
            return bool(result)  # True, если пользователь найден
        except sqlite3.Error as e:
            print(f"Ошибка подключения к базе данных: {e}")
            return False
    
    def load_data(self):
        try:
            conn = sqlite3.connect('skud_db.sqlite')  # Подключение к базе SQLite
            cursor = conn.cursor()
            query = "SELECT * FROM equipment"
            cursor.execute(query)
            records = cursor.fetchall()
            
            self.data_table.setRowCount(len(records))
            for row_idx, row_data in enumerate(records):
                for col_idx, col_data in enumerate(row_data):
                    self.data_table.setItem(row_idx, col_idx, QTableWidgetItem(str(col_data)))
            
            cursor.close()
            conn.close()
        except sqlite3.Error as e:
            print(f"Ошибка подключения к базе данных: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SKUDApp()
    window.show()
    sys.exit(app.exec())
