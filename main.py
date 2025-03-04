import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QLineEdit, QVBoxLayout, QWidget
import mysql.connector

class SKUDApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("СКУД - Авторизация")
        self.setGeometry(100, 100, 300, 200)
        
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
        
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
    
    def authenticate(self):
        user = self.input_user.text()
        password = self.input_pass.text()
        
        conn = mysql.connector.connect(host='localhost', user='root', password='root', database='skud_db')
        cursor = conn.cursor()
        
        query = "SELECT * FROM users WHERE username = %s AND password = %s"
        cursor.execute(query, (user, password))
        result = cursor.fetchone()
        
        if result:
            self.label_user.setText("Доступ разрешен")
        else:
            self.label_user.setText("Ошибка авторизации")
        
        cursor.close()
        conn.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SKUDApp()
    window.show()
    sys.exit(app.exec())
