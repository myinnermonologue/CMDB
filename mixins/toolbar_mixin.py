from PyQt6.QtWidgets import (
    QToolBar, QWidget, QFormLayout, QComboBox, QLineEdit, QTextEdit, QDateTimeEdit,
    QPushButton, QMessageBox, QCompleter,QSpinBox
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
        add_action = QAction("Создание техники", self)
        add_tech_types_action = QAction("Создание типов", self)
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
        add_tech_types_action.triggered.connect(self.add_tech_type_func)

        toolbar.addAction(move_action)
        toolbar.addAction(store_action)
        toolbar.addAction(tech_action)
        toolbar.addAction(employee_action)
        toolbar.addAction(add_action)
        toolbar.addAction(add_tech_types_action)
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
        self.type_input = QComboBox()
        self.subtype_input = QComboBox()
        self.brand_input = QComboBox()
        self.model_input = QComboBox()
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

        def set_combobox_searchable(combo: QComboBox, items: list[str]):
            combo.clear()
            combo.addItems(items)
            completer = QCompleter(items)
            completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
            completer.setFilterMode(Qt.MatchFlag.MatchContains)
            completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
            combo.setCompleter(completer)
            # Убрано: combo.lineEdit().setReadOnly(True)
            # Теперь можно вводить произвольный текст

        # === Загрузка ФИО ===
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT full_name_tabel FROM CKR_users ORDER BY full_name_tabel ASC")
            fio_list = [row[0] for row in cursor.fetchall() if row[0]]
            set_combobox_searchable(self.fio_input, fio_list)
        except Exception as e:
            print(f"Ошибка при загрузке ФИО: {e}")

        # === Загрузка tech_types ===
        self.tech_types = []
        try:
            cursor.execute("SELECT old_id, type_tech, additional_type, brand, model FROM tech_types WHERE visible = 'Да'")
            for row in cursor.fetchall():
                entry = {
                    "old_id": row[0],
                    "type": row[1],
                    "subtype": row[2],
                    "brand": row[3],
                    "model": row[4]
                }
                self.tech_types.append(entry)
        except Exception as e:
            print(f"Ошибка загрузки tech_types: {e}")
        finally:
            cursor.close()
            conn.close()

        # Уникальные значения для списков
        types = sorted(set(t["type"] for t in self.tech_types))
        subtypes = sorted(set(t["subtype"] for t in self.tech_types))
        brands = sorted(set(t["brand"] for t in self.tech_types))
        models = sorted(set(t["model"] for t in self.tech_types))

        self.type_input.addItems(types)
        self.subtype_input.addItems(subtypes)
        self.brand_input.addItems(brands)
        self.model_input.addItems(models)

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
        if hasattr(self, "current_user_role") and self.current_user_role.lower() == "auditor":
            btn_add.clicked.connect(lambda: QMessageBox.warning(self, "Нет доступа", "У вас нет прав на добавление техники."))
        else:
            btn_add.clicked.connect(self.insert_new_device)
        layout.addRow(btn_add)

        self.setCentralWidget(main_widget)
        
        def set_combobox_searchable(combo: QComboBox, items: list[str]):
            combo.clear()
            combo.addItems(items)
            combo.setEditable(True)
            completer = QCompleter(items)
            completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
            completer.setFilterMode(Qt.MatchFlag.MatchContains)
            completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
            combo.setCompleter(completer)
            
        
        set_combobox_searchable(self.type_input, types)
        set_combobox_searchable(self.subtype_input, subtypes)
        set_combobox_searchable(self.brand_input, brands)
        set_combobox_searchable(self.model_input, models)

   

    def insert_new_device(self):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            # Проверка обязательных полей (подтип необязателен)
            fields = [
                self.fio_input.currentText().strip(),
                self.type_input.currentText().strip(),
                self.brand_input.currentText().strip(),
                self.model_input.currentText().strip(),
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

            # Получаем assigned_to
            cursor.execute("SELECT old_id FROM CKR_users WHERE full_name_tabel = ?", (self.fio_input.currentText(),))
            res = cursor.fetchone()
            if not res:
                QMessageBox.warning(self, "Ошибка", "Пользователь не найден.")
                return
            assigned_to = res[0]

            selected_type = self.type_input.currentText()
            selected_subtype = self.subtype_input.currentText().strip()
            selected_brand = self.brand_input.currentText()
            selected_model = self.model_input.currentText()

            matched = next(
                (t for t in self.tech_types if t["type"] == selected_type and
                (t["subtype"] == selected_subtype or (not selected_subtype and not t["subtype"])) and
                t["brand"] == selected_brand and t["model"] == selected_model),
                None
            )
            if not matched:
                QMessageBox.critical(self, "Ошибка", "Такой тип техники не найден в базе.")
                return

            device_type_id = matched["old_id"]

            cursor.execute("SELECT MAX(CAST(id AS INTEGER)) FROM Table_Devices")
            max_id = cursor.fetchone()[0] or 0
            new_id = max_id + 1

            cursor.execute("SELECT MAX(CAST(old_id AS INTEGER)) FROM Table_Devices")
            max_old_id = cursor.fetchone()[0] or 0
            new_old_id = max_old_id + 1

            condition = self.condition_input.currentText()
            status = self.status_input.currentText()
            date_supply = self.date_input.dateTime().toString("dd.MM.yyyy H:mm:ss")

            serial_number = self.serial_input.text().strip()
            if not serial_number:
                serial_number = f"CKRSN{new_old_id}"

            full_name = f"{selected_type}"
            if selected_subtype and selected_subtype.lower() != "не применимо":
                full_name += f" {selected_subtype}"
            full_name += f" {selected_brand}"
            if selected_model.lower() != "не применимо":
                full_name += f" {selected_model}"
            full_name += f" ({serial_number})"

            cursor.execute("""
                INSERT INTO Table_Devices (
                    id, old_id, assigned_to, serial_number, condition, status,
                    inv_number, year_of_release, ship_number, supplier, date_of_supply,
                    price, owner_of_device, description, full_device_data, device_type, visible
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                new_id, new_old_id, assigned_to, serial_number, condition, status,
                self.inv_input.text().strip(), self.year_input.text().strip(), self.ship_input.text().strip(),
                self.supplier_input.text().strip(), date_supply, self.price_input.text().strip(),
                self.owner_input.text().strip(), self.comment_input.toPlainText().strip(), full_name, device_type_id, 'Да'
            ))

            # Запись в историю
            cursor.execute("SELECT MAX(CAST(id AS INTEGER)) FROM History")
            new_hist_id = (cursor.fetchone()[0] or 0) + 1
            cursor.execute("SELECT MAX(CAST(old_id AS INTEGER)) FROM History")
            new_hist_old_id = (cursor.fetchone()[0] or 0) + 1
            now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            cursor.execute("""
                INSERT INTO History (
                    id, old_id, date, type_of_action, who_add_to_db,
                    tech_move, where_moved, from_moved, ticket, description
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                new_hist_id, new_hist_old_id, now_str, "создание нового", "test",
                new_old_id, assigned_to, None, None, self.comment_input.toPlainText().strip()
            ))

            conn.commit()
            QMessageBox.information(self, "Успех", "Техника успешно добавлена.")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при добавлении: {e}")
        finally:
            cursor.close()
            conn.close()



    def add_tech_type_func(self):
        main_widget = QWidget()
        layout = QFormLayout(main_widget)

        self.type_tech_input = QComboBox(); self.type_tech_input.setEditable(True)
        self.additional_type_input = QComboBox(); self.additional_type_input.setEditable(True)
        self.brand_input_tt = QComboBox(); self.brand_input_tt.setEditable(True)
        self.model_input_tt = QComboBox(); self.model_input_tt.setEditable(True)
        self.serial_input_tt = QComboBox()
        self.serial_input_tt.addItems(["yes", "not"])
        self.serial_input_tt.setEditable(True)
        self.typeC_input = QComboBox(); self.typeC_input.setEditable(True)
        self.service_amount_input = QSpinBox(); self.service_amount_input.setMaximum(1000)
        self.visible_input = QComboBox(); self.visible_input.addItems(["Да", "Нет"])

        def load_combobox_data(cursor, column_name, combobox):
            try:
                cursor.execute(f"""
                    SELECT DISTINCT {column_name} 
                    FROM tech_types 
                    WHERE {column_name} IS NOT NULL AND TRIM({column_name}) != ''
                    ORDER BY {column_name} ASC
                """)
                values = [row[0] for row in cursor.fetchall()]
                combobox.clear()
                if values:
                    combobox.addItems(values)
                    combobox.setEditable(True)
                    completer = QCompleter(values)
                    completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
                    completer.setFilterMode(Qt.MatchFlag.MatchContains)
                    combobox.setCompleter(completer)
            except Exception as e:
                print(f"Ошибка загрузки {column_name}: {e}")

        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            load_combobox_data(cursor, "type_tech", self.type_tech_input)
            load_combobox_data(cursor, "additional_type", self.additional_type_input)
            load_combobox_data(cursor, "brand", self.brand_input_tt)
            load_combobox_data(cursor, "model", self.model_input_tt)
            load_combobox_data(cursor, "typeC", self.typeC_input)
        except Exception as e:
            print(f"Ошибка соединения с базой: {e}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

        # Добавь виджеты в layout
        layout.addRow("Тип техники", self.type_tech_input)
        layout.addRow("Доп. тип", self.additional_type_input)
        layout.addRow("Производитель", self.brand_input_tt)
        layout.addRow("Модель", self.model_input_tt)
        layout.addRow("Серийный номер", self.serial_input_tt)
        layout.addRow("ТипC", self.typeC_input)
        layout.addRow("Срок службы", self.service_amount_input)
        layout.addRow("Видимость", self.visible_input)
                # Кнопка для добавления типа техники
        btn_add_type = QPushButton("Добавить тип техники")
        if hasattr(self, "current_user_role") and self.current_user_role.lower() == "auditor":
            btn_add_type.clicked.connect(lambda: QMessageBox.warning(self, "Нет доступа", "У вас нет прав на добавление типа техники."))
        else:
            btn_add_type.clicked.connect(self.insert_new_tech_type)
        layout.addRow(btn_add_type)

        self.setCentralWidget(main_widget)


    def insert_new_tech_type(self):
        conn = None
        cursor = None
        try:
            if not self.type_tech_input.currentText().strip() or not self.brand_input_tt.currentText().strip():
                QMessageBox.warning(self, "Ошибка", "Заполните обязательные поля: тип и производитель.")
                return

            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute("SELECT MAX(CAST(old_id AS INTEGER)) FROM tech_types")
            max_old_id = cursor.fetchone()[0] or 0
            new_old_id = max_old_id + 1

            cursor.execute("""
                INSERT INTO tech_types (
                    old_id, type_tech, additional_type, brand, model,
                    serNumb, typeC, service_amount, visible
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                new_old_id,
                self.type_tech_input.currentText().strip(),
                self.additional_type_input.currentText().strip(),
                self.brand_input_tt.currentText().strip(),
                self.model_input_tt.currentText().strip(),
                self.serial_input_tt.currentText().strip(),
                self.typeC_input.currentText().strip(),
                self.service_amount_input.value(),
                self.visible_input.currentText()
            ))

            conn.commit()
            QMessageBox.information(self, "Успех", "Тип техники успешно добавлен.")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при добавлении типа техники:\n{e}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
