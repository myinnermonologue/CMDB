from PyQt6.QtWidgets import (
    QToolBar, QWidget, QFormLayout, QComboBox, QLineEdit, QTextEdit, QDateTimeEdit,
    QPushButton, QMessageBox, QCompleter
)
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt, QDateTime
from datetime import datetime
from constants import (
    arr_tech_types, query_tech_types,
    arr_assets, query_assets,
    arr_history, query_history,
    arr_history_user, query_history_user,
    arr_it_users, query_it_users,
    arr_ckr_users, query_ckr_users
)
from db import get_db_connection
class ToolbarMixin:
    def setup_toolbar(self):
        """Создаёт тулбар и настраивает действия в зависимости от роли пользователя."""
        toolbar = QToolBar("Основное меню")
        self.addToolBar(toolbar)

        move_action = QAction("Движение", self)
        store_action = QAction("Склад", self)
        tech_action = QAction("Техника", self)
        employee_action = QAction("Сотрудник", self)
        add_action = QAction("Создание", self)
        tech_assets_action = QAction("Таблица БД", self)
        tech_types_db_action = QAction("Категории техники", self)
        history_action = QAction("История", self)
        history_user_action = QAction("Ист. польз.", self)
        it_users_action = QAction("Сотруд. ИТ", self)
        ckr_users_action = QAction("Пользователи", self)

        tech_types_db_action.triggered.connect(lambda: self.show_db_func(arr_tech_types, query_tech_types))
        tech_assets_action.triggered.connect(lambda: self.show_db_func(arr_assets, query_assets))
        move_action.triggered.connect(self.move_action_func)
        history_action.triggered.connect(lambda: self.show_db_func(arr_history, query_history))
        history_user_action.triggered.connect(lambda: self.show_db_func(arr_history_user, query_history_user))
        it_users_action.triggered.connect(lambda: self.show_db_func(arr_it_users, query_it_users))
        ckr_users_action.triggered.connect(lambda: self.show_db_func(arr_ckr_users, query_ckr_users))
        store_action.triggered.connect(self.store_action_func)
        tech_action.triggered.connect(self.technic_action_func)
        employee_action.triggered.connect(self.employee_action_func)
        add_action.triggered.connect(self.add_action_func)

        toolbar.addAction(move_action)
        toolbar.addAction(store_action)
        toolbar.addAction(tech_action)
        toolbar.addAction(employee_action)
        toolbar.addAction(add_action)
        toolbar.addAction(tech_assets_action)
        toolbar.addAction(tech_types_db_action)
        toolbar.addAction(history_action)
        toolbar.addAction(history_user_action)
        toolbar.addAction(it_users_action)
        toolbar.addAction(ckr_users_action)

        # Список ограниченных кнопок
        restricted_actions = [
            tech_types_db_action,
            tech_assets_action,
            history_action,
            history_user_action,
            it_users_action,
            ckr_users_action
        ]

        if hasattr(self, "current_user_role") and self.current_user_role and self.current_user_role.lower() in ["manager", "auditor"]:
            for action in restricted_actions:
                toolbar.removeAction(action)

    def add_action_func(self):
        main_widget = QWidget()
        layout = QFormLayout(main_widget)

        # === Поля ===
        self.fio_input = QComboBox()
        self.fio_input.setEditable(True)
        self.fio_input.addItem("")
        self.serial_input = QLineEdit()
        self.type_input = QLineEdit()
        self.subtype_input = QLineEdit()
        self.brand_input = QLineEdit()
        self.model_input = QLineEdit()
        self.condition_input = QComboBox()
        self.status_input = QComboBox()
        self.inv_input = QLineEdit()
        self.year_input = QLineEdit()
        self.ship_input = QLineEdit()
        self.supplier_input = QLineEdit()
        self.date_input = QDateTimeEdit()
        self.price_input = QLineEdit()
        self.owner_input = QLineEdit()
        self.comment_input = QTextEdit()

        self.condition_input.addItems(["исправно", "не исправно"])
        self.status_input.addItems(["эксплуатация", "хранение", "поиск", "списано", "ремонт", "утилизировано"])
        self.date_input.setCalendarPopup(True)
        self.date_input.setDisplayFormat("dd.MM.yyyy H:mm:ss")
        self.date_input.setDateTime(QDateTime.currentDateTime())

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT full_name_tabel FROM CKR_users ORDER BY full_name_tabel ASC")
            users = [row[0] for row in cursor.fetchall() if row[0]]
            self.fio_input.addItems(users)
            completer = QCompleter(users)
            completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
            completer.setFilterMode(Qt.MatchFlag.MatchContains)
            self.fio_input.setCompleter(completer)
            cursor.close()
            conn.close()
        except Exception as e:
            print(f"Ошибка при загрузке ФИО: {e}")

        layout.addRow("Где находится", self.fio_input)
        layout.addRow("Серийный", self.serial_input)
        layout.addRow("Тип", self.type_input)
        layout.addRow("Подтип", self.subtype_input)
        layout.addRow("Производитель", self.brand_input)
        layout.addRow("Модель", self.model_input)
        layout.addRow("Состояние", self.condition_input)
        layout.addRow("Статус", self.status_input)
        layout.addRow("Инвентарный", self.inv_input)
        layout.addRow("Год выпуска", self.year_input)
        layout.addRow("Партномер", self.ship_input)
        layout.addRow("Поставщик", self.supplier_input)
        layout.addRow("Дата поставки", self.date_input)
        layout.addRow("Стоимость", self.price_input)
        layout.addRow("Собственник", self.owner_input)
        layout.addRow("Комментарий", self.comment_input)

        btn_add = QPushButton("Добавить технику")
        if self.current_user_role.lower() == "auditor":
            btn_add.clicked.connect(lambda: QMessageBox.warning(self, "Нет доступа", "У вас нет прав на добавление техники."))
        else:
            btn_add.clicked.connect(self.insert_new_device)
        layout.addRow(btn_add)

        self.setCentralWidget(main_widget)

    def insert_new_device(self):
        fields = [
            self.fio_input.currentText().strip(),
            self.serial_input.text().strip(),
            self.type_input.text().strip(),
            self.subtype_input.text().strip(),
            self.brand_input.text().strip(),
            self.model_input.text().strip(),
            self.inv_input.text().strip(),
            self.year_input.text().strip(),
            self.ship_input.text().strip(),
            self.supplier_input.text().strip(),
            self.price_input.text().strip(),
            self.owner_input.text().strip()
        ]

        if any(not val for val in fields):
            QMessageBox.warning(self, "Ошибка", "Заполните все обязательные поля!")
            return

        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute("SELECT MAX(CAST(old_id AS INTEGER)) FROM Table_Devices")
            max_device_id = cursor.fetchone()[0] or 0
            new_device_id = max_device_id + 1

            cursor.execute("SELECT MAX(CAST(id AS INTEGER)) FROM Table_Devices")
            max_id = cursor.fetchone()[0] or 0
            new_id = max_id + 1

            cursor.execute("SELECT MAX(CAST(old_id AS INTEGER)) FROM tech_types")
            max_type_id = cursor.fetchone()[0] or 0
            new_type_id = max_type_id + 1

            # Получаем assigned_to
            cursor.execute("SELECT old_id FROM CKR_users WHERE full_name_tabel = ?", (self.fio_input.currentText(),))
            assigned_to = cursor.fetchone()[0]

            condition = self.condition_input.currentText()
            status = self.status_input.currentText()
            date_supply = self.date_input.dateTime().toString("dd.MM.yyyy H:mm:ss")

            type_ = self.type_input.text().strip()
            subtype = self.subtype_input.text().strip()
            brand = self.brand_input.text().strip()
            model = self.model_input.text().strip()
            serial = self.serial_input.text().strip()

            full_name = f"{type_}"
            if subtype.lower() != "не применимо":
                full_name += f" {subtype}"
            full_name += f" {brand}"
            if model.lower() != "не применимо":
                full_name += f" {model}"
            full_name += f" ({serial})"

            cursor.execute("""
                INSERT INTO Table_Devices (
                    id, old_id, assigned_to, serial_number, condition, status,
                    inv_number, year_of_release, ship_number, supplier, date_of_supply,
                    price, owner_of_device, description, full_device_data, device_type
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                new_id, new_device_id, assigned_to, serial, condition, status,
                self.inv_input.text().strip(), self.year_input.text().strip(),
                self.ship_input.text().strip(), self.supplier_input.text().strip(),
                date_supply, self.price_input.text().strip(), self.owner_input.text().strip(),
                self.comment_input.toPlainText().strip(), full_name, new_type_id
            ))

            cursor.execute("""
                INSERT INTO tech_types (old_id, type_tech, additional_type, brand, model)
                VALUES (?, ?, ?, ?, ?)
            """, (new_type_id, type_, subtype, brand, model))

                    # === Добавляем запись в History ===
            cursor.execute("SELECT MAX(CAST(id AS INTEGER)) FROM History")
            max_hist_id = cursor.fetchone()[0] or 0
            new_hist_id = max_hist_id + 1

            cursor.execute("SELECT MAX(CAST(old_id AS INTEGER)) FROM History")
            max_hist_old_id = cursor.fetchone()[0] or 0
            new_hist_old_id = max_hist_old_id + 1

            now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            comment = self.comment_input.toPlainText().strip()

            cursor.execute("""
                INSERT INTO History (
                    id, old_id, date, type_of_action, who_add_to_db,
                    tech_move, where_moved, from_moved, ticket, description
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                new_hist_id, new_hist_old_id, now_str, "создание нового", "test",
                new_device_id, assigned_to, None, None, comment
            ))

            conn.commit()
            QMessageBox.information(self, "Успех", "Техника успешно добавлена.")

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при добавлении: {e}")
        finally:
            cursor.close()
            conn.close()