import sys
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QMessageBox
from PyQt6.QtCore import QTimer
from mixins.toolbar_mixin import ToolbarMixin
from mixins.technic_mixin import TechnicMixin
from mixins.employee_mixin import EmployeeMixin
from mixins.store_mixin import StoreMixin
from mixins.move_mixin import MoveMixin
from mixins.dbview_mixin import DbViewMixin
from mixins.edit_dialog_mixin import EditDialogMixin
import os # для получения имени пользователя
from db import get_db_connection

class MainWindow(
    QMainWindow,
    ToolbarMixin,
    TechnicMixin,
    EmployeeMixin,
    StoreMixin,
    MoveMixin,
    DbViewMixin,
    EditDialogMixin
):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CSC_CMDB")
        self.current_user = None
        self.current_user_role = None  # или получить из логина пользователя
        domain = os.environ.get("USERDOMAIN")
        username = os.environ.get("USERNAME")
        # --- Добавьте эти строки ---
        self.records_per_page = 50
        self.current_page = 0
        self.total_records = 0
        self.current_query = ""
        self.current_table_name = ""
        # -----------------------   ----
        if domain.upper() != "PC_NEAKTUALNO":
            QMessageBox.critical(None, "Ошибка доступа", f"Недопустимый домен: {domain}")
            sys.exit()

        # Проверка пользователя в БД
        if not self.is_user_in_db(username):
            QMessageBox.critical(None, "Ошибка доступа", f"Пользователь {username} не найден в системе.")
            sys.exit()
            
        QTimer.singleShot(100, lambda: QMessageBox.information(
            None,  # <-- центр экрана
            "Добро пожаловать",
            f"Добро пожаловать, {self.current_user_full_name}!\nВаша роль: {self.current_user_role}"
        ))
        # Центральный виджет и основной layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.layout = QVBoxLayout(central_widget)

        # Инициализация тулбара
        self.setup_toolbar()

    def is_user_in_db(self, username):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT full_name, role FROM it_users WHERE LOWER(username) = LOWER(?)", (username,))
            result = cursor.fetchone()
            conn.close()
            if result:
                full_name, role = result
                self.current_user_full_name = full_name
                self.current_user_role = role
                return True
            return False
        except Exception as e:
            print(f"Ошибка при проверке пользователя: {e}")
            return False