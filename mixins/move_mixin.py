from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QGridLayout, QLabel, QComboBox, QCompleter,
    QCheckBox, QPushButton, QAbstractItemView, QMessageBox,
    QListWidget, QTextEdit, QLineEdit
)
from PyQt6.QtCore import Qt
from db import get_db_connection
from datetime import datetime
from pysqlcipher3 import dbapi2 as sqlite3
class MoveMixin:
    def move_action_func(self): 
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)

        # Основная сетка
        grid = QGridLayout()

        # === Отправитель ===
        grid.addWidget(QLabel("Объект"), 0, 0)
        self.fio_input = QComboBox()
        self.fio_input.setEditable(True)
        self.fio_input.addItem("")
        grid.addWidget(self.fio_input, 1, 0)

        user_list_input = []
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT full_name_tabel FROM CKR_users ORDER BY full_name_tabel ASC")
            items = cursor.fetchall()
            for item in items:
                if item[0]:
                    user_list_input.append(str(item[0]))
                    self.fio_input.addItem(str(item[0]))
            cursor.close()
            conn.close()
        except sqlite3.Error as e:
            print(f"Ошибка при загрузке ФИО: {e}")

        completer = QCompleter(user_list_input, self.fio_input)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        completer.setFilterMode(Qt.MatchFlag.MatchContains)
        self.fio_input.setCompleter(completer)

        # === Получатель ===
        grid.addWidget(QLabel("Объект"), 0, 2)
        self.fio_output = QComboBox()
        self.fio_output.setEditable(True)
        self.fio_output.addItem("")
        grid.addWidget(self.fio_output, 1, 2)

        user_list_output = []
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT full_name_tabel FROM CKR_users ORDER BY full_name_tabel ASC")
            items = cursor.fetchall()
            for item in items:
                if item[0]:
                    user_list_output.append(str(item[0]))
                    self.fio_output.addItem(str(item[0]))
            cursor.close()
            conn.close()
        except sqlite3.Error as e:
            print(f"Ошибка при загрузке ФИО: {e}")

        completer_output = QCompleter(user_list_output, self.fio_output)
        completer_output.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        completer_output.setFilterMode(Qt.MatchFlag.MatchContains)
        self.fio_output.setCompleter(completer_output)

        self.fio_input.currentIndexChanged.connect(lambda: self.update_device_list(self.fio_input, self.list_left))
        self.fio_output.currentIndexChanged.connect(lambda: self.update_device_list(self.fio_output, self.list_right))

        # === № обращения ===
        grid.addWidget(QLabel("№ обращения"), 2, 0)
        self.request_input = QLineEdit()
        grid.addWidget(self.request_input, 3, 0)

        # === Тип движения ===
        grid.addWidget(QLabel("Тип движения"), 4, 0)
        self.combo_move_type = QComboBox()
        self.combo_move_type.addItems(["выдача", "перемещение", "на склад", "создание нового", "в поиск", "изменение"])
        grid.addWidget(self.combo_move_type, 5, 0)

        # === Комментарий ===
        grid.addWidget(QLabel("Комментарий к обращению"), 6, 0)
        self.comment_input = QTextEdit()
        self.comment_input.setFixedHeight(60)
        grid.addWidget(self.comment_input, 7, 0)

        # === Списки устройств ===
        self.list_left = QListWidget()
        self.list_right = QListWidget()
        self.list_left.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        self.list_right.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        grid.addWidget(self.list_left, 8, 0)
        grid.addWidget(self.list_right, 8, 2)

        # === Кнопка перемещения ===
        move_layout = QVBoxLayout()
        self.move_right_btn = QPushButton("Переместить---->>>")
        self.move_right_btn.setFixedHeight(60)
        move_layout.addWidget(self.move_right_btn)
        grid.addLayout(move_layout, 8, 1)

        # === Чекбоксы ===
        checkbox_grid_left = QGridLayout()
        checkbox_grid_right = QGridLayout()
        options = [
            "Хранение", "Перемещение", "Поиск", "Резерв",
            "Исправно", "Не исправно", "Ремонт", "На списание",
            "Списано", "Утиль", "Показать уволенных"
        ]

        self.checkboxes_left = [QCheckBox(opt) for opt in options]
        self.checkboxes_right = [QCheckBox(opt) for opt in options]

        # Левая сторона чекбоксов
        row, col = 0, 0
        for cb in self.checkboxes_left:
            checkbox_grid_left.addWidget(cb, row, col)
            col += 1
            if col >= 2:
                col = 0
                row += 1

        # Правая сторона чекбоксов
        row, col = 0, 0
        for cb in self.checkboxes_right:
            checkbox_grid_right.addWidget(cb, row, col)
            col += 1
            if col >= 2:
                col = 0
                row += 1

        # Добавляем чекбоксы в сетку
        grid.addLayout(checkbox_grid_left, 9, 0)
        grid.addLayout(checkbox_grid_right, 9, 2)

        # Финальная сборка
        main_layout.addLayout(grid)
        self.setCentralWidget(main_widget)

        for cb in self.checkboxes_left:
            cb.stateChanged.connect(lambda _, cb=cb: self.update_device_list(self.fio_input, self.list_left))
        for cb in self.checkboxes_right:
            cb.stateChanged.connect(lambda _, cb=cb: self.update_device_list(self.fio_output, self.list_right))

        if self.current_user_role.lower() == "auditor":
            self.move_right_btn.clicked.connect(lambda: QMessageBox.warning(self, "Нет доступа", "У вас нет прав на перемещение техники."))
        else:
            self.move_right_btn.clicked.connect(self.move_device_between_users)

    def move_device_between_users(self):
        selected_items = self.list_left.selectedItems()

        if not self.fio_input.currentText().strip():
            QMessageBox.warning(self, "Ошибка", "Не выбран отправитель (слева).")
            return

        if not self.fio_output.currentText().strip():
            QMessageBox.warning(self, "Ошибка", "Не выбран получатель (справа).")
            return

        if not selected_items:
            QMessageBox.information(self, "Внимание", "Не выбрана техника для перемещения.")
            return

        # Проверка на пустоту поля № обращения и комментария
        if not self.request_input.text().strip() or not self.comment_input.toPlainText().strip():
            QMessageBox.warning(self, "Ошибка", "Поля '№ обращения' и 'Комментарий' не могут быть пустыми.")
            return

        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            # Получаем ID пользователей (от кого -> кому)
            cursor.execute("SELECT old_id FROM CKR_users WHERE full_name_tabel = ?", (self.fio_input.currentText(),))
            from_user_id = cursor.fetchone()
            cursor.execute("SELECT old_id FROM CKR_users WHERE full_name_tabel = ?", (self.fio_output.currentText(),))
            to_user_id = cursor.fetchone()

            if not from_user_id or not to_user_id:
                QMessageBox.critical(self, "Ошибка", "Не удалось получить ID пользователей.")
                return

            from_id = from_user_id[0]
            to_id = to_user_id[0]

            now = datetime.now()
            now_str = now.strftime("%Y-%m-%d %H:%M:%S")
            user_name = self.current_user
            ticket = self.request_input.text()
            action_type = self.combo_move_type.currentText()
            comment = self.comment_input.toPlainText()

            for selected_item in selected_items:
                selected_text = selected_item.text()

                # Найдём ID техники
                cursor.execute("SELECT old_id FROM Table_Devices WHERE full_device_data = ? AND assigned_to = ?", (selected_text, from_id))
                device_id_row = cursor.fetchone()

                if not device_id_row:
                    print(f"Техника '{selected_text}' не найдена.")
                    continue

                device_id = device_id_row[0]

                # Обновляем владельца в Table_Devices
                cursor.execute("UPDATE Table_Devices SET assigned_to = ? WHERE old_id = ?", (to_id, device_id))

                # Получаем следующий old_id для истории
                cursor.execute("SELECT old_id FROM History")
                rows = cursor.fetchall()

                valid_ids = []
                for row in rows:
                    try:
                        valid_ids.append(int(row[0]))
                    except (TypeError, ValueError):
                        continue

                next_old_id = max(valid_ids) + 1 if valid_ids else 1

                # Добавляем запись в History
                cursor.execute("""
                    INSERT INTO History (
                        old_id, date, type_of_action, who_add_to_db,
                        tech_move, where_moved, from_moved, ticket, description
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (next_old_id, now_str, action_type, user_name, device_id, to_id, from_id, ticket, comment))

                # Обновляем интерфейс
                self.list_right.addItem(selected_text)
                self.list_left.takeItem(self.list_left.row(selected_item))

            conn.commit()
            QMessageBox.information(self, "Успешно", "Техника успешно перемещена.")

        except sqlite3.Error as e:
            QMessageBox.critical(self, "Ошибка базы данных", f"Ошибка при перемещении техники:\n{str(e)}")

        finally:
            try:
                cursor.close()
                conn.close()
            except:
                pass

    def update_device_list(self, fio_combobox, list_widget):
        if not hasattr(self, 'fio_input') or not fio_combobox:
            return

        selected_full_name = fio_combobox.currentText()
        if not selected_full_name:
            return

        checkbox_to_db_status = {
            "Хранение": "хранение",
            "Перемещение": "перемещение",
            "Поиск": "поиск",
            "Ремонт": "ремонт",
            "Утиль": "утилизировано",
            "Исправно": "исправно",
            "Не исправно": "не исправно",
            "На списание": "на списание",
            "Списано": "списано"
        }
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            # Получаем ID пользователя
            cursor.execute("SELECT old_id FROM CKR_users WHERE full_name_tabel = ?", (selected_full_name,))
            result = cursor.fetchone()
            if not result:
                return

            user_old_id = result[0]

            # Определяем нужные чекбоксы
            checkboxes = self.checkboxes_left if fio_combobox == self.fio_input else self.checkboxes_right

            selected_statuses = [
                checkbox_to_db_status[cb.text()]
                for cb in checkboxes if cb.isChecked() and cb.text() in checkbox_to_db_status
            ]

            if selected_statuses:
                # Создаём 2 набора плейсхолдеров
                placeholders_status = ','.join(['?'] * len(selected_statuses))
                placeholders_condition = ','.join(['?'] * len(selected_statuses))
                query = f"""
                    SELECT full_device_data FROM Table_Devices 
                    WHERE assigned_to = ? AND (
                        status IN ({placeholders_status}) OR 
                        condition IN ({placeholders_condition})
                    )
                """
                # параметры: user_id, значения для status, значения для condition
                params = [user_old_id] + selected_statuses + selected_statuses
                cursor.execute(query, params)
            else:
                # Без фильтра
                query = "SELECT full_device_data FROM Table_Devices WHERE assigned_to = ?"
                cursor.execute(query, (user_old_id,))

            # Обновляем список
            devices = cursor.fetchall()
            list_widget.clear()
            for dev in devices:
                if dev[0]:
                    list_widget.addItem(dev[0])

            cursor.close()
            conn.close()

        except sqlite3.Error as e:
            print(f"Ошибка при загрузке техники: {e}")
