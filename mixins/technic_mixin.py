from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QFormLayout, QLineEdit, QTextEdit, QComboBox,
    QCompleter, QLabel, QTableWidget, QTableWidgetItem, QPushButton,QMessageBox
)
from PyQt6.QtCore import Qt, QSettings
from datetime import datetime
from db import get_db_connection
import traceback
class TechnicMixin:
    def technic_action_func(self):
        # Удаляем старые ссылки на виджеты, чтобы не обращаться к удалённым объектам
        for attr in [
            "where_field", "serial_field", "type_field", "subtype_field", "manufacturer_field", "model_field",
            "condition_field", "status_field", "inventory_field", "year_field", "provider_field", "delivery_field",
            "price_field", "owner_field", "location_field", "part_field", "sn_on_box_field", "sn_on_device_field",
            "comment_field", "search_field", "history_table"
        ]:
            if hasattr(self, attr):
                delattr(self, attr)

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
        self.condition_field = QComboBox()
        self.condition_field.addItems(["исправно", "не исправно", "утилизировано", "ремонт", "списано"])

        self.status_field = QComboBox()
        self.status_field.addItems(["поиск", "резерв", "утилизировано", "хранение", "эксплуатация"])
        self.inventory_field = QLineEdit()
        self.year_field = QLineEdit()
        self.provider_field = QComboBox()
        self.provider_field.addItems(["ООО \"ЦКР\"", "АО \"Джет\"", "ПАО НЛМК", "ПАО ПГК"])
        self.provider_field.setEditable(True)
        self.delivery_field = QLineEdit()
        self.price_field = QLineEdit()
        self.owner_field = QComboBox()
        self.owner_field.addItems(["ООО \"ЦКР\"", "АО \"Джет\"", "ПАО НЛМК", "ПАО ПГК"])
        self.location_field = QLineEdit()
        self.part_field = QLineEdit()
        self.sn_on_box_field = QLineEdit()
        self.sn_on_device_field = QLineEdit()

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
        left_form_layout.addRow("Партномер:", self.part_field)
        left_form_layout.addRow("Поставщик:", self.provider_field)
        left_form_layout.addRow("Дата поставки:", self.delivery_field)
        left_form_layout.addRow("Стоимость:", self.price_field)
        left_form_layout.addRow("Собственник:", self.owner_field)
        left_form_layout.addRow("Локация:", self.location_field)
        left_form_layout.addRow("SN на коробке:", self.sn_on_box_field)
        left_form_layout.addRow("SN на устройстве:", self.sn_on_device_field)

        # Комментарий (QTextEdit) и кнопка "Сохранить"
        comment_layout = QHBoxLayout()
        self.comment_field = QTextEdit()
        self.comment_field.setFixedHeight(50)
        comment_layout.addWidget(self.comment_field)
        left_form_layout.addRow("Комментарий:", comment_layout)
                    # Поля, которые можно редактировать
        editable_fields = {
            self.serial_field,
            self.sn_on_box_field,
            self.sn_on_device_field,
            self.condition_field,
            self.status_field,
            self.inventory_field,
            self.year_field,
            self.part_field,
            self.provider_field,
            self.delivery_field,
            self.price_field,
            self.owner_field
        }

        # Устанавливаем только нужные как редактируемые
        for field in [
            self.where_field,
            self.type_field,
            self.subtype_field,
            self.manufacturer_field,
            self.model_field,
            self.location_field,
        ]:
            field.setReadOnly(True)

        # Для всех остальных — явно отключаем редактирование, если не входит в editable
        for field in [
            self.serial_field, self.sn_on_box_field, self.sn_on_device_field, self.inventory_field, self.year_field, self.part_field,
            self.provider_field, self.delivery_field, self.price_field, self.owner_field
        ]:
            if isinstance(field, QLineEdit):
                field.setReadOnly(False)
            elif isinstance(field, QComboBox):
                field.setEnabled(True)

        for combo in [self.condition_field, self.status_field]:
            combo.setEnabled(True)

        self.comment_field.setReadOnly(False)
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

        self.load_device_data()
        self.search_field.activated.connect(self.on_device_selected)

        # --- Восстановление значения из QSettings ---
        settings = QSettings('CKR', 'CMDB')
        search_text = settings.value('technic/search_field', '')
        if search_text and self.search_field.findText(search_text) != -1:
            self.search_field.setCurrentText(search_text)
        elif search_text:
            self.search_field.addItem(search_text)
            self.search_field.setCurrentText(search_text)

        # Таблица истории
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(7)
        self.history_table.setHorizontalHeaderLabels(["Дата", "Тип", "Сотр. ИТ", "Куда", "Откуда", "Основание", "Примечание"])
        self.history_table.horizontalHeader().setStretchLastSection(True)
        self.history_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.history_table.setSortingEnabled(True)

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

        # Автоматическая подгрузка данных устройства
        self.auto_populate_from_search()

        # --- Автосохранение значения в QSettings ---
        self.search_field.currentIndexChanged.connect(lambda: QSettings('CKR', 'CMDB').setValue('technic/search_field', self.search_field.currentText()))

    def populate_device_fields(self, selected_text):
        if not hasattr(self, "history_table"):
            return

        if not selected_text:
            return

        conn = get_db_connection()
        cursor = conn.cursor()

        # Получаем данные из Table_Devices
        cursor.execute("""
            SELECT
                assigned_to,
                serial_number,
                sn_on_box,
                sn_on_device,
                device_type,
                "condition",
                status,
                inv_number,
                year_of_release,
                supplier,
                date_of_supply,
                price,
                owner_of_device,
                description
            FROM Table_Devices
            WHERE full_device_data = ?
        """, (selected_text,))
        result = cursor.fetchone()

        if not result:
            conn.close()
            return

        (
            assigned_to,
            serial_number,
            sn_on_box,
            sn_on_device,
            device_type,
            condition,
            status,
            inv_number,
            year_of_release,
            supplier,
            date_of_supply,
            price,
            owner_of_device,
            description
        ) = result

        # Получаем данные из таблицы CKR_users по assigned_to
        cursor.execute("""
            SELECT full_name_tabel, address
            FROM CKR_users
            WHERE old_id = ?
        """, (assigned_to,))
        user_result = cursor.fetchone()

        # Проверяем, если результат не пустой
        if user_result:
            full_name_tabel = user_result[0]
            user_address = user_result[1]
        else:
            full_name_tabel = "Не найден"
            user_address = ""

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
        self.sn_on_box_field.setText(str(sn_on_box or ""))
        self.sn_on_device_field.setText(str(sn_on_device or ""))
        self.type_field.setText(str(type_tech or ""))
        self.subtype_field.setText(str(additional_type or ""))
        self.manufacturer_field.setText(str(brand or ""))
        self.model_field.setText(str(model or ""))
        self.condition_field.setCurrentText(str(condition or ""))
        self.status_field.setCurrentText(str(status or ""))
        self.inventory_field.setText(str(inv_number or ""))
        self.year_field.setText(str(year_of_release or ""))
        self.provider_field.setCurrentText(str(supplier or ""))
        self.delivery_field.setText(str(date_of_supply or ""))
        self.price_field.setText(str(price or ""))
        self.owner_field.setCurrentText(str(owner_of_device or ""))
        self.location_field.setText(str(user_address or ""))
        self.comment_field.setPlainText(str(description or ""))

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

        # Фильтруем только записи, где description НЕ содержит 'было'
        filtered_history_rows = [row for row in history_rows if not (row[-1] and 'было' in row[-1])]

        self.history_table.setRowCount(len(filtered_history_rows))
        for row_idx, row_data in enumerate(filtered_history_rows):
            for col_idx, value in enumerate(row_data):
                self.history_table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))

        conn.close()

    def on_device_selected(self, index):
        selected_text = self.search_field.itemText(index)
        self.populate_device_fields(selected_text)
    
    def save_changes(self):
        def normalize_number(value: str):
            value = value.strip().lower()
            if value in ("", "nan", "none"):
                return None
            try:
                return float(value)
            except ValueError:
                return None

        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            selected_text = self.search_field.currentText()
            cursor.execute("SELECT old_id FROM Table_Devices WHERE full_device_data = ?", (selected_text,))
            result = cursor.fetchone()
            if not result:
                conn.close()
                return

            device_old_id = result[0]

            cursor.execute("""
                SELECT serial_number, sn_on_box, sn_on_device, "condition", status, inv_number,
                    year_of_release, supplier, date_of_supply, price,
                    owner_of_device, description
                FROM Table_Devices
                WHERE old_id = ?
            """, (device_old_id,))

            current_data = cursor.fetchone()
            if not current_data:
                conn.close()
                return

            def normalize_price(value: str):
                value = value.strip()
                if value == "":
                    return None
                return value.replace(",", ".")

            price_value = normalize_price(self.price_field.text())

            new_data = (
                self.serial_field.text().strip(),
                self.sn_on_box_field.text().strip(),
                self.sn_on_device_field.text().strip(),
                self.condition_field.currentText().strip(),
                self.status_field.currentText().strip(),
                self.inventory_field.text().strip(),
                self.year_field.text().strip(),
                self.provider_field.currentText().strip(),
                self.delivery_field.text().strip(),
                price_value,
                self.owner_field.currentText().strip(),
                self.comment_field.toPlainText().strip()
            )

            cursor.execute("""
                UPDATE Table_Devices
                SET serial_number = ?, sn_on_box = ?, sn_on_device = ?, "condition" = ?,
                    status = ?, inv_number = ?, year_of_release = ?, supplier = ?,
                    date_of_supply = ?, price = ?, owner_of_device = ?, description = ?,
                    assigned_to = (SELECT old_id FROM CKR_users WHERE full_name_tabel = ?)
                WHERE old_id = ?
            """, new_data + (self.where_field.text(), device_old_id))

            # --- HISTORY ID ---
            cursor.execute("SELECT COALESCE(MAX(old_id), 0) FROM History")
            history_id = int(cursor.fetchone()[0]) + 1

            def add_history(field_name, old_value, new_value):
                nonlocal history_id

                if str(old_value).strip() != str(new_value).strip():
                    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                    desc = f"{field_name} изменено с '{old_value}' на '{new_value}'"

                    cursor.execute("""
                        INSERT INTO History (
                            old_id, date, type_of_action, who_add_to_db,
                            tech_move, where_moved, from_moved, ticket, description
                        )
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        history_id,
                        now,
                        "изменение",
                        self.current_user,
                        device_old_id,
                        None,
                        None,
                        None,
                        desc
                    ))

                    history_id += 1

            # --- full_device_data ---
            cursor.execute("SELECT full_device_data FROM Table_Devices WHERE old_id = ?", (device_old_id,))
            old_full_device_data = cursor.fetchone()
            old_full_device_data = old_full_device_data[0] if old_full_device_data else ""

            type_ = self.type_field.text().strip()
            subtype = self.subtype_field.text().strip()
            brand = self.manufacturer_field.text().strip()
            model = self.model_field.text().strip()
            serial = self.serial_field.text().strip()

            full_name = f"{type_}"
            if subtype and subtype.lower() != "не применимо":
                full_name += f" {subtype}"
            full_name += f" {brand}"
            if model and model.lower() != "не применимо":
                full_name += f" {model}"
            full_name += f" ({serial})"

            cursor.execute(
                "UPDATE Table_Devices SET full_device_data = ? WHERE old_id = ?",
                (full_name, device_old_id)
            )

            if old_full_device_data != full_name:
                add_history("full_device_data", old_full_device_data, full_name)

            # --- изменения полей ---
            add_history("Состояние", current_data[3], self.condition_field.currentText())
            add_history("Статус", current_data[4], self.status_field.currentText())
            add_history("Инвентарный номер", current_data[5], self.inventory_field.text())
            add_history("Год выпуска", current_data[6], self.year_field.text())
            add_history("Поставщик", current_data[7], self.provider_field.currentText())
            add_history("Дата поставки", current_data[8], self.delivery_field.text())
            add_history("Стоимость", current_data[9], price_value)
            add_history("Собственник", current_data[10], self.owner_field.currentText())
            add_history("SN на коробке", current_data[1], self.sn_on_box_field.text())
            add_history("SN на устройстве", current_data[2], self.sn_on_device_field.text())
            add_history("Комментарий", current_data[11], self.comment_field.toPlainText())

            conn.commit()
            conn.close()

            QMessageBox.information(self, "Успешно", "Изменения сохранены")
            self.load_device_data()

        except Exception as e:
            print("ERROR:", e)
            print(traceback.format_exc())
            QMessageBox.critical(self, "Ошибка", traceback.format_exc())

    def load_device_data(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT full_device_data FROM Table_Devices")
        results = [row[0] for row in cursor.fetchall() if row[0]]
        conn.close()

        self.search_field.clear()
        self.search_field.addItems(results)
        # Восстановить текст поиска, если был
        if hasattr(self, 'last_search_text') and self.last_search_text:
            self.search_field.setEditText(self.last_search_text)
        # Создаём completer и привязываем
        completer = QCompleter(results, self.search_field)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        completer.setFilterMode(Qt.MatchFlag.MatchContains)
        self.search_field.setCompleter(completer)
        # --- Автоматическая подгрузка данных устройства ---
        self.auto_populate_from_search()

    def auto_populate_from_search(self):
        text = self.last_search_text if hasattr(self, 'last_search_text') and self.last_search_text else self.search_field.currentText()
        idx = self.search_field.findText(text)
        if text and idx != -1:
            self.populate_device_fields(text)

    def save_search_text(self):
        # Сохраняет текст поиска, безопасно (если виджет не удалён)
        if hasattr(self, 'search_field') and self.search_field is not None:
            try:
                self.last_search_text = self.search_field.currentText()
            except RuntimeError:
                pass  # Виджет уже удалён, ничего не делаем

    def restore_search_text(self):
        # Восстанавливает текст поиска
        if hasattr(self, 'search_field') and hasattr(self, 'last_search_text'):
            self.search_field.setEditText(self.last_search_text)