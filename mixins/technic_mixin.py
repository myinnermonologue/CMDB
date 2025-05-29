from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QFormLayout, QLineEdit, QTextEdit, QComboBox,
    QCompleter, QLabel, QTableWidget, QTableWidgetItem, QPushButton,QMessageBox
)
from PyQt6.QtCore import Qt
from datetime import datetime
from db import get_db_connection
class TechnicMixin:
    def technic_action_func(self):
            main_layout = QHBoxLayout()

            # === Левая панель ===
            left_widget = QWidget()
            left_form_layout = QFormLayout()
            # left_form_layout.setContentsMargins(10, 10, 10, 10)

            self.where_field = QLineEdit()
            self.serial_field = QLineEdit()
            self.type_field = QLineEdit()
            self.subtype_field = QLineEdit()
            self.manufacturer_field = QLineEdit()
            self.model_field = QLineEdit()
            self.condition_field = QLineEdit()
            self.status_field = QLineEdit()
            self.inventory_field = QLineEdit()
            self.year_field = QLineEdit()
            self.provider_field = QLineEdit()
            self.delivery_field = QLineEdit()
            self.price_field = QLineEdit()
            self.owner_field = QLineEdit()
            self.location_field = QLineEdit()

            left_form_layout.addRow("Где находится:", self.where_field)
            left_form_layout.addRow("Серийный:", self.serial_field)
            left_form_layout.addRow("Тип:", self.type_field)
            left_form_layout.addRow("Подтип:", self.subtype_field)
            left_form_layout.addRow("Производитель:", self.manufacturer_field)
            left_form_layout.addRow("Модель:", self.model_field)
            left_form_layout.addRow("Состояние:", self.condition_field)
            left_form_layout.addRow("Статус:", self.status_field)
            left_form_layout.addRow("Инвентарный №:", self.inventory_field)
            left_form_layout.addRow("Год выпуска:", self.year_field)
            left_form_layout.addRow("Партномер:", QLineEdit())  # необязательное поле
            left_form_layout.addRow("Поставщик:", self.provider_field)
            left_form_layout.addRow("Дата поставки:", self.delivery_field)
            left_form_layout.addRow("Стоимость:", self.price_field)
            left_form_layout.addRow("Собственник:", self.owner_field)
            left_form_layout.addRow("Локация:", self.location_field)

            # Комментарий (QTextEdit) и кнопка "Сохранить"
            comment_layout = QHBoxLayout()
            self.comment_field = QTextEdit()
            self.comment_field.setFixedHeight(50)
            comment_layout.addWidget(self.comment_field)
            left_form_layout.addRow("Комментарий:", comment_layout)

            left_widget.setLayout(left_form_layout)
            left_widget.setFixedWidth(500)

            # === Правая панель ===
            right_widget = QWidget()
            right_layout = QVBoxLayout()
            right_layout.setContentsMargins(0, 0, 0, 0)
            right_layout.setSpacing(5)

            # Поле поиска
            
            self.search_field = QComboBox()
            self.search_field.setEditable(True)
            self.search_field.setPlaceholderText("Поиск устройства...")
            self.search_field.setFixedHeight(30)

            # Загрузка данных из базы
            def load_device_data():
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT full_device_data FROM Table_Devices")
                results = [row[0] for row in cursor.fetchall() if row[0]]
                conn.close()

                self.search_field.clear()
                self.search_field.addItems(results)

                # Создаём completer и привязываем
                completer = QCompleter(results, self.search_field)
                completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
                completer.setFilterMode(Qt.MatchFlag.MatchContains)
                self.search_field.setCompleter(completer)

        

            load_device_data()
            self.search_field.activated.connect(self.on_device_selected)

            # Таблица истории
            self.history_table = QTableWidget()
            self.history_table.setColumnCount(7)
            self.history_table.setHorizontalHeaderLabels(["Дата", "Тип", "Сотр. ИТ", "Куда", "Откуда", "Основание", "Примечание"])
            self.history_table.horizontalHeader().setStretchLastSection(True)
            self.history_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

            right_layout.addWidget(self.search_field)
            right_layout.addWidget(QLabel("История изменения"))
            right_layout.addWidget(self.history_table)
            save_button = QPushButton("Сохранить")
            save_button.clicked.connect(self.save_changes)
            left_form_layout.addRow(save_button)
            right_widget.setLayout(right_layout)

            # Финальный макет
            main_layout.addWidget(left_widget)
            main_layout.addWidget(right_widget)

            central_widget = QWidget()
            central_widget.setLayout(main_layout)
            self.setCentralWidget(central_widget)

    def populate_device_fields(self, selected_text):
        if not selected_text:
            return

        conn = get_db_connection()
        cursor = conn.cursor()

        # Получаем данные из Table_Devices
        cursor.execute("""
            SELECT assigned_to, serial_number, device_type, condition, status,
                inv_number, year_of_release, owner_of_device, date_of_supply,
                price, owner_of_device
            FROM Table_Devices
            WHERE full_device_data = ?
        """, (selected_text,))
        result = cursor.fetchone()

        if not result:
            conn.close()
            return

        (
            assigned_to, serial_number, device_type, condition, status,
            inv_number, year_of_release, supplier, date_of_supply,
            price, owner_of_device
        ) = result

        # Получаем данные из таблицы CKR_users по assigned_to
        cursor.execute("""
            SELECT full_name_tabel
            FROM CKR_users
            WHERE old_id = ?
        """, (assigned_to,))
        user_result = cursor.fetchone()

        # Проверяем, если результат не пустой
        if user_result:
            full_name_tabel = user_result[0]  # Получаем значение поля full_name_tabel
        else:
            full_name_tabel = "Не найден"

        # Получаем данные из tech_types по old_id = device_type
        cursor.execute("""
            SELECT type_tech, additional_type, brand, model
            FROM tech_types
            WHERE old_id = ?
        """, (device_type,))
        tech_result = cursor.fetchone()
        

        if tech_result:
            type_tech, additional_type, brand, model = tech_result
        else:
            type_tech = additional_type = brand = model = ""

        # Заполняем поля
        self.where_field.setText(str(full_name_tabel or ""))
        self.serial_field.setText(str(serial_number or ""))
        self.type_field.setText(str(type_tech or ""))
        self.subtype_field.setText(str(additional_type or ""))
        self.manufacturer_field.setText(str(brand or ""))
        self.model_field.setText(str(model or ""))
        self.condition_field.setText(str(condition or ""))
        self.status_field.setText(str(status or ""))
        self.inventory_field.setText(str(inv_number or ""))
        self.year_field.setText(str(year_of_release or ""))
        self.provider_field.setText(str(supplier or ""))
        self.delivery_field.setText(str(date_of_supply or ""))
        self.price_field.setText(str(price or ""))
        self.owner_field.setText(str(owner_of_device or ""))
        
                # Получаем old_id устройства
        cursor.execute("SELECT old_id FROM Table_Devices WHERE full_device_data = ?", (selected_text,))
        device_id_result = cursor.fetchone()

        if not device_id_result:
            conn.close()
            return

        device_old_id = device_id_result[0]

        # Получаем историю для устройства
        cursor.execute("""
            SELECT date, type_of_action, who_add_to_db, 
                (SELECT full_name_tabel FROM CKR_users WHERE old_id = h.where_moved),
                (SELECT full_name_tabel FROM CKR_users WHERE old_id = h.from_moved),
                ticket,
                    description
            FROM History h
            WHERE tech_move = ?
            ORDER BY date DESC
        """, (device_old_id,))
        history_rows = cursor.fetchall()

        self.history_table.setRowCount(len(history_rows))
        for row_idx, row_data in enumerate(history_rows):
            for col_idx, value in enumerate(row_data):
                self.history_table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))

        conn.close()

    def on_device_selected(self, index):
        selected_text = self.search_field.itemText(index)
        self.populate_device_fields(selected_text)
    
    def save_changes(self):
        conn = get_db_connection()
        cursor = conn.cursor()

        # Получаем old_id выбранного устройства
        selected_text = self.search_field.currentText()
        cursor.execute("SELECT old_id FROM Table_Devices WHERE full_device_data = ?", (selected_text,))
        result = cursor.fetchone()
        if not result:
            conn.close()
            return
        device_old_id = result[0]

        # Пример обновления данных (обновите под нужные поля)
        cursor.execute("""
            UPDATE Table_Devices
            SET assigned_to = (SELECT old_id FROM CKR_users WHERE full_name_tabel = ?),
                serial_number = ?, condition = ?, status = ?, inv_number = ?,
                year_of_release = ?, date_of_supply = ?, price = ?, owner_of_device = ?
            WHERE old_id = ?
        """, (
            self.where_field.text(),
            self.serial_field.text(),
            self.condition_field.text(),
            self.status_field.text(),
            self.inventory_field.text(),
            self.year_field.text(),
            self.delivery_field.text(),
            self.price_field.text(),
            self.owner_field.text(),
            device_old_id
        ))

        # Добавляем запись в History
        # Добавляем запись в History
        cursor.execute("""
            INSERT INTO History (old_id, date, type_of_action, who_add_to_db, tech_move,
                where_moved, from_moved, ticket, description)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            device_old_id,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),  # нужный формат
            "Изменение",
            self.current_user,  # при наличии — заменить на логин или имя
            device_old_id,
            None,
            None,
            "Ручное изменение",
            self.comment_field.toPlainText()
        ))

        conn.commit()
        conn.close()
        QMessageBox.information(self, "Успешно", "Изменения успешно сохранены и записаны в историю.")