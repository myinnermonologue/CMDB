from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QGridLayout, QLabel, QComboBox, QCompleter,
    QCheckBox, QPushButton, QAbstractItemView, QMessageBox,QSizePolicy,
    QListWidget, QTextEdit, QLineEdit,QListWidgetItem, QGroupBox, QVBoxLayout, QScrollArea
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt, QSettings
from db import get_db_connection
from datetime import datetime, timedelta
from sqlcipher3 import dbapi2 as sqlite3

STATUS_START_COL = 70  # статус и состояние всегда с 70-й позиции

def make_padded_line(full_device_data, status_str):
    name = str(full_device_data)
    if len(name) >= STATUS_START_COL:
        return f"{name} {status_str}"
    else:
        spaces = ' ' * (STATUS_START_COL - len(name))
        return f"{name}{spaces}{status_str}"

class MoveMixin:
    def load_users(self, combobox, show_disabled_cb):
        combobox.clear()
        combobox.addItem("")
        user_list = []

        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            if show_disabled_cb and show_disabled_cb.isChecked():
                cursor.execute("SELECT DISTINCT full_name_tabel FROM CKR_users ORDER BY full_name_tabel ASC")
            else:
                cursor.execute("SELECT DISTINCT full_name_tabel FROM CKR_users WHERE status = 'Enabled' ORDER BY full_name_tabel ASC")

            items = cursor.fetchall()
            for item in items:
                if item[0]:
                    user_list.append(str(item[0]))
                    combobox.addItem(str(item[0]))

            completer = QCompleter(user_list, combobox)
            completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
            completer.setFilterMode(Qt.MatchFlag.MatchContains)
            combobox.setCompleter(completer)

            cursor.close()
            conn.close()
        except sqlite3.Error as e:
            print(f"Ошибка при загрузке ФИО: {e}")

    def move_action_func(self):
        if hasattr(self, 'save_search_text'):
            self.save_search_text()
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)

        grid = QGridLayout()

        # === Отправитель ===
        grid.addWidget(QLabel("Объект"), 0, 0)
        self.fio_input = QComboBox()
        self.fio_input.setEditable(True)
        self.fio_input.addItem("")
        grid.addWidget(self.fio_input, 1, 0)

        # === Получатель ===
        grid.addWidget(QLabel("Объект"), 0, 2)
        self.fio_output = QComboBox()
        self.fio_output.setEditable(True)
        self.fio_output.addItem("")
        grid.addWidget(self.fio_output, 1, 2)

        # === Чекбоксы ===
        checkbox_widget_left = QWidget()
        checkbox_layout_left = QVBoxLayout(checkbox_widget_left)
        checkbox_widget_right = QWidget()
        checkbox_layout_right = QVBoxLayout(checkbox_widget_right)
        options = [
            "Хранение", "Перемещение", "Поиск", "Резерв",
            "Исправно", "Не исправно", "Ремонт", "На списание",
            "Списано", "Утиль", "Показать уволенных"
        ]

        self.checkboxes_left = []
        self.checkboxes_right = []
        self.show_disabled_left_cb = None
        self.show_disabled_right_cb = None

        for opt in options:
            cb = QCheckBox(opt)
            if opt == "Показать уволенных":
                self.show_disabled_left_cb = cb
            self.checkboxes_left.append(cb)
            checkbox_layout_left.addWidget(cb)
        checkbox_layout_left.setContentsMargins(5, 5, 5, 5)
        checkbox_layout_left.setSpacing(4)
        scroll_area_left = QScrollArea()
        scroll_area_left.setWidgetResizable(True)
        scroll_area_left.setWidget(checkbox_widget_left)
        scroll_area_left.setMaximumHeight(200)

        for opt in options:
            cb = QCheckBox(opt)
            if opt == "Показать уволенных":
                self.show_disabled_right_cb = cb
            self.checkboxes_right.append(cb)
            checkbox_layout_right.addWidget(cb)
        checkbox_layout_right.setContentsMargins(5, 5, 5, 5)
        checkbox_layout_right.setSpacing(4)
        scroll_area_right = QScrollArea()
        scroll_area_right.setWidgetResizable(True)
        scroll_area_right.setWidget(checkbox_widget_right)
        scroll_area_right.setMaximumHeight(200)

        # --- Поисковые поля и списки устройств ---
        self.search_left = QLineEdit()
        self.search_left.setPlaceholderText("Поиск техники...")
        grid.addWidget(self.search_left, 9, 0)
        self.list_left = QListWidget()
        self.list_left.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        self.list_left.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        grid.addWidget(self.list_left, 10, 0)

        # --- Список выделенных слева ---
        self.selected_list_left = QListWidget()
        self.selected_list_left.setSelectionMode(QListWidget.SelectionMode.NoSelection)
        self.selected_list_left.setFixedHeight(140)
        self.selected_list_left.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        grid.addWidget(self.selected_list_left, 11, 0)
        self.selected_list_left.itemClicked.connect(lambda item: self._remove_selected_item('left', item))

        self.search_right = QLineEdit()
        self.search_right.setPlaceholderText("Поиск техники...")
        grid.addWidget(self.search_right, 9, 2)
        self.list_right = QListWidget()
        self.list_right.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        self.list_right.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        grid.addWidget(self.list_right, 10, 2)

        # --- Список выделенных справа ---
        self.selected_list_right = QListWidget()
        self.selected_list_right.setSelectionMode(QListWidget.SelectionMode.NoSelection)
        self.selected_list_right.setFixedHeight(140)
        self.selected_list_right.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        grid.addWidget(self.selected_list_right, 11, 2)
        self.selected_list_right.itemClicked.connect(lambda item: self._remove_selected_item('right', item))

        # Чекбоксы под списками
        grid.addWidget(scroll_area_left, 12, 0)
        grid.addWidget(scroll_area_right, 12, 2)

        # --- Стили выделения для списков ---
        highlight_style = """
        QListWidget::item:selected {
            background-color: #0078d7;
            color: white;
            font-weight: bold;
        }
        """
        self.list_left.setStyleSheet(highlight_style)
        self.list_right.setStyleSheet(highlight_style)

        # === Загрузка пользователей ===
        self.load_users(self.fio_input, self.show_disabled_left_cb)
        self.load_users(self.fio_output, self.show_disabled_right_cb)

        # === Тип движения ===
        grid.addWidget(QLabel("Тип движения"), 5, 0)
        self.combo_move_type = QComboBox()
        self.combo_move_type.addItems(["выдача", "перемещение", "на склад", "в поиск", "изменение"])
        grid.addWidget(self.combo_move_type, 6, 0)

        # === Комментарий ===
        grid.addWidget(QLabel("Комментарий к обращению"), 7, 0)
        self.comment_input = QTextEdit()
        self.comment_input.setFixedHeight(60)
        grid.addWidget(self.comment_input, 8, 0)

        # === № обращения ===
        grid.addWidget(QLabel("№ обращения"), 3, 0)
        self.request_input = QLineEdit()
        grid.addWidget(self.request_input, 4, 0)

        # === Кнопка перемещения ===
        move_layout = QVBoxLayout()
        self.move_right_btn = QPushButton("Переместить---->>>")
        self.move_right_btn.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        self.move_right_btn.setFixedHeight(60)
        move_layout.addWidget(self.move_right_btn)
        grid.addLayout(move_layout, 9, 1)

        # Настройка растягивания колонок
        grid.setColumnStretch(0, 3)
        grid.setColumnStretch(1, 1)
        grid.setColumnStretch(2, 3)

        # Финальная сборка
        main_layout.addLayout(grid)
        main_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setCentralWidget(main_widget)

        if self.current_user_role.lower() == "auditor":
            self.move_right_btn.clicked.connect(lambda: QMessageBox.warning(self, "Нет доступа", "У вас нет прав на перемещение техники."))
        else:
            self.move_right_btn.clicked.connect(self.move_device_between_users)

        # Теперь подключаем сигналы автосохранения формы
        self.fio_input.currentIndexChanged.connect(self.save_move_form_state)
        self.fio_output.currentIndexChanged.connect(self.save_move_form_state)
        self.fio_input.currentIndexChanged.connect(lambda: self.update_device_list(self.fio_input, self.list_left))
        self.fio_output.currentIndexChanged.connect(lambda: self.update_device_list(self.fio_output, self.list_right))
        self.fio_input.currentIndexChanged.connect(self._clear_both_selected)
        self.fio_output.currentIndexChanged.connect(self._clear_both_selected)
        self.request_input.textChanged.connect(self.save_move_form_state)
        self.combo_move_type.currentIndexChanged.connect(self.save_move_form_state)
        self.comment_input.textChanged.connect(self.save_move_form_state)
        for cb in self.checkboxes_left:
            cb.stateChanged.connect(self.save_move_form_state)
        for cb in self.checkboxes_right:
            cb.stateChanged.connect(self.save_move_form_state)
        for cb in self.checkboxes_left:
            cb.stateChanged.connect(lambda: self.update_device_list(self.fio_input, self.list_left))
        for cb in self.checkboxes_right:
            cb.stateChanged.connect(lambda: self.update_device_list(self.fio_output, self.list_right))
        # Connect 'Показать уволенных' checkboxes to reload user lists
        if self.show_disabled_left_cb:
            self.show_disabled_left_cb.stateChanged.connect(lambda: self.load_users(self.fio_input, self.show_disabled_left_cb))
        if self.show_disabled_right_cb:
            self.show_disabled_right_cb.stateChanged.connect(lambda: self.load_users(self.fio_output, self.show_disabled_right_cb))
        # --- Автосохранение значений в QSettings ---
        self.fio_input.currentIndexChanged.connect(lambda: QSettings('CKR', 'CMDB').setValue('move/fio_input', self.fio_input.currentText()))
        self.fio_output.currentIndexChanged.connect(lambda: QSettings('CKR', 'CMDB').setValue('move/fio_output', self.fio_output.currentText()))

        # --- Подключаем фильтрацию ---
        self.search_left.textChanged.connect(lambda text: self.filter_device_list('left', text))
        self.search_right.textChanged.connect(lambda text: self.filter_device_list('right', text))

        # После создания всех виджетов — восстановить состояние формы, если нужно
        if hasattr(self, 'restore_move_form_state'):
            self.restore_move_form_state()

        self.selected_left_ids = set()
        self.selected_right_ids = set()
        self.list_left.itemSelectionChanged.connect(self._update_selected_left)
        self.list_right.itemSelectionChanged.connect(self._update_selected_right)

    def move_device_between_users(self):
        # Используем только объекты из нижней таблицы (selected_left_ids)
        selected_ids = list(self.selected_left_ids)
        if not self.fio_input.currentText().strip():
            QMessageBox.warning(self, "Ошибка", "Не выбран отправитель (слева).")
            return
        if not self.fio_output.currentText().strip():
            QMessageBox.warning(self, "Ошибка", "Не выбран получатель (справа).")
            return
        if not selected_ids:
            QMessageBox.information(self, "Внимание", "Не выбрана техника для перемещения (выделите объекты в нижней таблице).")
            return
        if not self.request_input.text().strip() or not self.comment_input.toPlainText().strip():
            QMessageBox.warning(self, "Ошибка", "Поля '№ обращения' и 'Комментарий' не могут быть пустыми.")
            return
        if self.fio_input.currentText().strip() == self.fio_output.currentText().strip():
            QMessageBox.warning(self, "Ошибка", "Нельзя передавать технику самому себе!")
            return
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
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
            for full_device_data in selected_ids:
                cursor.execute("SELECT old_id FROM Table_Devices WHERE full_device_data = ? AND assigned_to = ?", (full_device_data, from_id))
                device_id_row = cursor.fetchone()
                if not device_id_row:
                    print(f"Техника '{full_device_data}' не найдена.")
                    continue
                device_id = device_id_row[0]
                cursor.execute("UPDATE Table_Devices SET assigned_to = ? WHERE old_id = ?", (to_id, device_id))
                cursor.execute("SELECT old_id FROM History")
                rows = cursor.fetchall()
                valid_ids = []
                for row in rows:
                    try:
                        valid_ids.append(int(row[0]))
                    except (TypeError, ValueError):
                        continue
                next_old_id = max(valid_ids) + 1 if valid_ids else 1
                cursor.execute("""
                    INSERT INTO History (
                        old_id, date, type_of_action, who_add_to_db,
                        tech_move, where_moved, from_moved, ticket, description
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (next_old_id, now_str, action_type, user_name, device_id, to_id, from_id, ticket, comment))
            conn.commit()
            QMessageBox.information(self, "Успешно", "Техника успешно перемещена.")
            if hasattr(self, 'last_move_form_data'):
                del self.last_move_form_data
            # После перемещения очищаем выделение
            self.selected_left_ids.clear()
            self._refresh_selected_list('left')
            self.update_device_list(self.fio_input, self.list_left)
            self.update_device_list(self.fio_output, self.list_right)
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

            cursor.execute(
                "SELECT old_id FROM CKR_users WHERE full_name_tabel = ?",
                (selected_full_name,)
            )
            result = cursor.fetchone()
            if not result:
                return
            user_old_id = result[0]

            # --- Новый блок: получаем полный список устройств пользователя (без фильтрации чекбоксами) ---
            # Для выравнивания: всегда добавляем clock_placeholder (⌚ или пробел)
            cursor.execute(
                "SELECT d.old_id, d.full_device_data, d.status, d.condition, CASE WHEN h.tech_move IS NOT NULL THEN 1 ELSE 0 END as was_moved_recently "
                "FROM Table_Devices d "
                "LEFT JOIN (SELECT DISTINCT tech_move FROM History WHERE date >= ?) h ON d.old_id = h.tech_move "
                "WHERE d.assigned_to = ?",
                ((datetime.now() - timedelta(hours=24)).strftime("%Y-%m-%d %H:%M:%S"), user_old_id)
            )
            all_devices_unfiltered = []
            target_line_width = 97
            for device_id, full_device_data, status, condition, was_recently_moved in cursor.fetchall():
                if not full_device_data:
                    continue
                status_parts = []
                if status:
                    status_parts.append(status)
                if condition:
                    status_parts.append(condition)
                status_str = ", ".join(status_parts)
                clock_placeholder = "⌚" if was_recently_moved else " "
                if status_str:
                    status_with_clock = f"{status_str} {clock_placeholder}"
                else:
                    status_with_clock = f"{clock_placeholder}"
                padded_line = make_padded_line(full_device_data, status_with_clock)
                all_devices_unfiltered.append((padded_line, full_device_data, status, condition))
            if list_widget == self.list_left:
                self.all_devices_left_unfiltered = all_devices_unfiltered
            elif list_widget == self.list_right:
                self.all_devices_right_unfiltered = all_devices_unfiltered
            # --- Конец нового блока ---

            checkboxes = self.checkboxes_left if fio_combobox == self.fio_input else self.checkboxes_right
            selected_statuses = [
                checkbox_to_db_status[cb.text()]
                for cb in checkboxes
                if cb.isChecked() and cb.text() in checkbox_to_db_status
            ]

            time_24_hours_ago = (datetime.now() - timedelta(hours=24)).strftime("%Y-%m-%d %H:%M:%S")

            base_query = """
                SELECT 
                    d.old_id,
                    d.full_device_data,
                    d.status,
                    d.condition,
                    CASE 
                        WHEN h.tech_move IS NOT NULL THEN 1
                        ELSE 0
                    END as was_moved_recently
                FROM Table_Devices d
                LEFT JOIN (
                    SELECT DISTINCT tech_move
                    FROM History
                    WHERE date >= ?
                ) h ON d.old_id = h.tech_move
                WHERE d.assigned_to = ?
            """
            params = [time_24_hours_ago, user_old_id]

            if selected_statuses:
                placeholders = ','.join(['?'] * len(selected_statuses))
                base_query += f" AND (d.status IN ({placeholders}) OR d.condition IN ({placeholders}))"
                params.extend(selected_statuses + selected_statuses)

            cursor.execute(base_query, params)
            devices = cursor.fetchall()

            # --- Отключаем сигнал itemSelectionChanged ---
            if list_widget == self.list_left:
                try:
                    self.list_left.itemSelectionChanged.disconnect(self._update_selected_left)
                except Exception:
                    pass
            elif list_widget == self.list_right:
                try:
                    self.list_right.itemSelectionChanged.disconnect(self._update_selected_right)
                except Exception:
                    pass

            list_widget.clear()
            list_widget.setFont(QFont("Courier New", 10))

            device_items = []
            target_line_width = 97
            for device_id, full_device_data, status, condition, was_recently_moved in devices:
                if not full_device_data:
                    continue
                status_parts = []
                if status:
                    status_parts.append(status)
                if condition:
                    status_parts.append(condition)
                status_str = ", ".join(status_parts)
                clock_placeholder = "⌚" if was_recently_moved else " "
                if status_str:
                    status_with_clock = f"{status_str} {clock_placeholder}"
                else:
                    status_with_clock = f"{clock_placeholder}"
                padded_line = make_padded_line(full_device_data, status_with_clock)
                device_items.append((padded_line, full_device_data))

            # Сортировка по алфавиту
            device_items.sort(key=lambda x: x[0])

            if list_widget == self.list_left:
                self.all_devices_left = device_items
                self.all_devices_left_full = device_items.copy()
            elif list_widget == self.list_right:
                self.all_devices_right = device_items
                self.all_devices_right_full = device_items.copy()

            # --- Вручную выставляем выделение для видимых, не меняя selected_left_ids/selected_right_ids ---
            for padded_line, full_device_data in device_items:
                item = QListWidgetItem(padded_line)
                item.setData(Qt.ItemDataRole.UserRole, full_device_data)
                list_widget.addItem(item)
                if list_widget == self.list_left and full_device_data in self.selected_left_ids:
                    item.setSelected(True)
                elif list_widget == self.list_right and full_device_data in self.selected_right_ids:
                    item.setSelected(True)

            # --- Включаем сигнал обратно ---
            if list_widget == self.list_left:
                self.list_left.itemSelectionChanged.connect(self._update_selected_left)
            elif list_widget == self.list_right:
                self.list_right.itemSelectionChanged.connect(self._update_selected_right)

            cursor.close()
            conn.close()

        except sqlite3.Error as e:
            print(f"Ошибка при загрузке техники: {e}")

    def filter_device_list(self, side, text):
        """
        Фильтрует список устройств по введённому тексту (поиск по всей строке, без учёта регистра)
        side: 'left' или 'right'
        text: строка поиска
        """
        if side == 'left':
            list_widget = self.list_left
            all_devices = getattr(self, 'all_devices_left_full', getattr(self, 'all_devices_left', []))
            selected_ids = self.selected_left_ids
        else:
            list_widget = self.list_right
            all_devices = getattr(self, 'all_devices_right_full', getattr(self, 'all_devices_right', []))
            selected_ids = self.selected_right_ids
        list_widget.blockSignals(True)
        list_widget.clear()
        text_lower = text.lower()
        first_selected_item = None
        for padded_line, full_device_data in all_devices:
            if not text_lower or text_lower in padded_line.lower() or text_lower in full_device_data.lower():
                item = QListWidgetItem(padded_line)
                item.setData(Qt.ItemDataRole.UserRole, full_device_data)
                list_widget.addItem(item)
                if full_device_data in selected_ids:
                    item.setSelected(True)
                    if first_selected_item is None:
                        first_selected_item = item
        if first_selected_item:
            list_widget.setCurrentItem(first_selected_item)
        list_widget.blockSignals(False)

    def save_move_form_state(self):
        self.last_move_form_data = {
            'fio_input': self.fio_input.currentText(),
            'fio_output': self.fio_output.currentText(),
            'checkboxes_left': [cb.isChecked() for cb in self.checkboxes_left],
            'checkboxes_right': [cb.isChecked() for cb in self.checkboxes_right],
            'request_input': self.request_input.text(),
            'combo_move_type': self.combo_move_type.currentIndex(),
            'comment_input': self.comment_input.toPlainText()
        }

    def restore_move_form_state(self):
        if hasattr(self, 'last_move_form_data'):
            data = self.last_move_form_data
            self.fio_input.setCurrentText(data.get('fio_input', ''))
            self.fio_output.setCurrentText(data.get('fio_output', ''))
            for cb, checked in zip(self.checkboxes_left, data.get('checkboxes_left', [])):
                cb.setChecked(checked)
            for cb, checked in zip(self.checkboxes_right, data.get('checkboxes_right', [])):
                cb.setChecked(checked)
            self.request_input.setText(data.get('request_input', ''))
            self.combo_move_type.setCurrentIndex(data.get('combo_move_type', 0))
            self.comment_input.setPlainText(data.get('comment_input', ''))

    def _update_selected_left(self):
        # Получаем текущее выделение только из видимых
        current_selected = set()
        for i in range(self.list_left.count()):
            item = self.list_left.item(i)
            if item.isSelected():
                current_selected.add(item.data(Qt.ItemDataRole.UserRole))
        # Добавляем к уже выделенным
        self.selected_left_ids |= current_selected
        # Удаляем из выделения только те, которые видимы и явно сняты пользователем
        visible_ids = set(item.data(Qt.ItemDataRole.UserRole) for item in [self.list_left.item(i) for i in range(self.list_left.count())])
        for id_ in list(self.selected_left_ids):
            if id_ in visible_ids and id_ not in current_selected:
                self.selected_left_ids.remove(id_)
        self._refresh_selected_list('left')

    def _update_selected_right(self):
        current_selected = set()
        for i in range(self.list_right.count()):
            item = self.list_right.item(i)
            if item.isSelected():
                current_selected.add(item.data(Qt.ItemDataRole.UserRole))
        self.selected_right_ids |= current_selected
        visible_ids = set(item.data(Qt.ItemDataRole.UserRole) for item in [self.list_right.item(i) for i in range(self.list_right.count())])
        for id_ in list(self.selected_right_ids):
            if id_ in visible_ids and id_ not in current_selected:
                self.selected_right_ids.remove(id_)
        self._refresh_selected_list('right')

    def _refresh_selected_list(self, side):
        if side == 'left':
            selected_ids = self.selected_left_ids
            all_devices_full = getattr(self, 'all_devices_left_unfiltered', [])
            selected_list = self.selected_list_left
        else:
            selected_ids = self.selected_right_ids
            all_devices_full = getattr(self, 'all_devices_right_unfiltered', [])
            selected_list = self.selected_list_right
        selected_list.clear()
        shown = set()
        # Создаём отображение: full_device_data -> padded_line
        device_map = {full_device_data: padded_line for padded_line, full_device_data, status, condition in all_devices_full}
        target_line_width = 97
        for full_device_data in selected_ids:
            if full_device_data not in shown:
                if full_device_data in device_map:
                    padded_line = device_map[full_device_data]
                else:
                    # Если устройства нет в списке, делаем строку вручную с пробелом для выравнивания
                    status_bracketed = " "
                    padded_line = make_padded_line(full_device_data, status_bracketed)
                item = QListWidgetItem(padded_line)
                item.setData(Qt.ItemDataRole.UserRole, full_device_data)
                selected_list.addItem(item)
                shown.add(full_device_data)

    def _remove_selected_item(self, side, item):
        full_device_data = item.data(Qt.ItemDataRole.UserRole)
        if side == 'left':
            self.selected_left_ids.discard(full_device_data)
            self._refresh_selected_list('left')
            # Снимаем выделение в основной таблице
            for i in range(self.list_left.count()):
                it = self.list_left.item(i)
                if it.data(Qt.ItemDataRole.UserRole) == full_device_data:
                    it.setSelected(False)
        else:
            self.selected_right_ids.discard(full_device_data)
            self._refresh_selected_list('right')
            for i in range(self.list_right.count()):
                it = self.list_right.item(i)
                if it.data(Qt.ItemDataRole.UserRole) == full_device_data:
                    it.setSelected(False)

    def _clear_both_selected(self):
        """Очищает обе нижние таблицы и все связанные выделения при смене сотрудника/склада."""
        self.selected_left_ids.clear()
        self.selected_right_ids.clear()
        self.selected_list_left.clear()
        self.selected_list_right.clear()
        self.list_left.clearSelection()
        self.list_right.clearSelection()

