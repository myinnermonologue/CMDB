import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QLabel, QLineEdit, QComboBox, QCheckBox,
    QVBoxLayout, QWidget, QPushButton, QCompleter, QListWidget, QAbstractItemView,
    QGridLayout, QDialog, QTableWidget, QTableWidgetItem, QToolBar, QTextEdit,QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction
from pysqlcipher3 import dbapi2 as sqlite3
from datetime import datetime
from dotenv import load_dotenv
import os
load_dotenv()

def get_db_connection():
    CIP = os.getenv("JWGEWERGJG")
    conn = sqlite3.connect('EncryptedDatabase.db')
    conn.execute(f"PRAGMA key = '{CIP}'")
    CIP = None
    return conn

arr_assets = [
            "old_id", "serial_number", "device_type", "year_of_release", "date_of_supply", 
            "owner_of_device", "assigned_to", "status", "condition", "inv_number", 
            "supplier", "price", "ship_number", "full_device_data", "description", "characteristics", 
            "project", "visible", "reserve"
        ]

query_assets = """SELECT old_id, serial_number, device_type, year_of_release, date_of_supply, 
                            owner_of_device, assigned_to, status, condition, inv_number, 
                            supplier, price, ship_number, full_device_data, description, characteristics, 
                            project, visible, reserve FROM Table_Devices"""

arr_tech_types = [
            "old_id", "type_tech", "additional_type", "visible", "type_of_tech", "brand", "model", "category", "serNumb", "service_amount"
        ]

query_tech_types = """SELECT old_id, type_tech, additional_type, visible, type_of_tech, brand, model, 
            category, serNumb, service_amount FROM tech_types"""

arr_history_user = [
            "old_id", "date", "type", "user", "description_of_change"
        ]

query_history_user = """SELECT old_id, date, type, user, description_of_change FROM history_user"""

arr_history = [
            "old_id", "date", "type_of_action", "who_add_to_db", "tech_move", "where_moved", "from_moved", "ticket", "description"
        ]

query_history = """SELECT old_id, date, type_of_action, who_add_to_db, tech_move, where_moved, from_moved, 
            ticket, description FROM History"""

arr_it_users = ["role", "active", "username", "name_initials", "full_name"]

query_it_users = """SELECT role, active, username, name_initials, full_name FROM it_users"""

arr_ckr_users = ["old_id","last_name","first_name","patronymic","company","unit1","unit2","unit3","unit4", "unit5","unit6",
                "status","position","city","address","tabel_num","supervisor","email","room","description","category","type_of_user",
                "full_name_tabel"]

query_ckr_users = """SELECT old_id,last_name,first_name,patronymic,company,unit1,unit2,unit3,unit4,unit5,unit6,
                status,position,city,address,tabel_num,supervisor,email,room,description,category,type_of_user,
                full_name_tabel FROM CKR_users"""

class EditDialog(QDialog):
    def __init__(self, row_data, column_names, table_name, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Редактирование данных")
        self.setGeometry(200, 200, 500, 400)

        self.row_data = row_data
        self.column_names = column_names
        self.table_name = table_name
        self.edit_fields = {}

        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        grid = QGridLayout()

        for idx, label in enumerate(self.column_names):
            row = idx // 2
            col = idx % 2

            grid.addWidget(QLabel(label), row, col * 2)
            field = QLineEdit(self)
            field.setText(str(self.row_data[idx]))
            self.edit_fields[label] = field
            grid.addWidget(field, row, col * 2 + 1)

        layout.addLayout(grid)

        save_btn = QPushButton("Сохранить изменения", self)
        save_btn.clicked.connect(self.save_changes)
        layout.addWidget(save_btn)

        self.setLayout(layout)

    def save_changes(self):
        updated_data = [field.text() for field in self.edit_fields.values()]
        primary_key = self.column_names[0]
        primary_value = self.row_data[0]

        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            set_clause = ", ".join([f"{col}=?" for col in self.column_names])
            query = f"""UPDATE {self.table_name} 
                        SET {set_clause} 
                        WHERE {primary_key} = ?"""

            cursor.execute(query, tuple(updated_data + [primary_value]))

            conn.commit()
            cursor.close()
            conn.close()

            print("Данные успешно обновлены!")
            self.accept()

        except sqlite3.Error as e:
            print(f"Ошибка при сохранении данных: {e}")

class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_user = None
        self.setWindowTitle("CSC_CMDB")
        self.setGeometry(100, 100, 100, 100)
        self.authUI()

    
    def authenticate(self):
        user = self.input_user.text()
        password = self.input_pass.text()
        
        if self.check_user_credentials(user, password):
            self.current_user = user  # сохраняем имя пользователя
            self.label_user.setText("Доступ разрешен")
            self.setGeometry(100, 100, 600, 400)
            self.fullUI()
        else:
            self.label_user.setText("Ошибка авторизации")
    

    def check_user_credentials(self, username, password):
        try:
            conn = get_db_connection()  # Подключение к базе SQLite
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
        

    def fullUI(self):
        layout = QVBoxLayout()

        # Добавляем Toolbar
        toolbar = QToolBar("Основное меню")
        self.addToolBar(toolbar)

        move_action = QAction("Движение", self)
        store_action = QAction("Склад", self)
        tech_action = QAction("Техника", self)
        employee_action = QAction("Сотрудник", self)
        add_action = QAction("Добавление", self)
        tech_assets_action = QAction("Таблица БД", self)
        tech_types_db_action = QAction("Категории техники", self)
        history_action = QAction("История", self) 
        history_user_action = QAction("Ист. польз.", self)
        it_users_action =  QAction("Сотруд. ИТ", self)
        ckr_users_action = QAction("Пользователи", self)
        tech_types_db_action.triggered.connect(lambda: self.show_db_func(arr_tech_types, query_tech_types))
        tech_assets_action.triggered.connect(lambda: self.show_db_func(arr_assets, query_assets))
        move_action.triggered.connect(self.move_action_func)
        history_action.triggered.connect(lambda: self.show_db_func(arr_history, query_history))
        history_user_action.triggered.connect(lambda: self.show_db_func(arr_history_user, query_history_user))
        it_users_action.triggered.connect(lambda: self.show_db_func(arr_it_users, query_it_users))
        ckr_users_action.triggered.connect(lambda: self.show_db_func(arr_ckr_users, query_ckr_users))
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

        # Контейнер для размещения всего интерфейса
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def show_db_func(self, array, query):
        layout = QVBoxLayout()

        self.data_table = QTableWidget()
        self.data_table.setColumnCount(len(array))
        self.data_table.setHorizontalHeaderLabels(array)
        self.data_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.data_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.data_table.cellClicked.connect(self.on_cell_click)
        layout.addWidget(self.data_table)

        load_data_btn = QPushButton("Загрузить данные", self)
        load_data_btn.clicked.connect(lambda: self.load_data_db(query))
        layout.addWidget(load_data_btn)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.current_table_name = self.extract_table_name(query)
        self.load_data_db(query)

    def extract_table_name(self, query):
        # Простой способ вытащить имя таблицы из SELECT-запроса
        lowered = query.lower()
        if "from" in lowered:
            return lowered.split("from")[1].split()[0]
        return ""

    def update_device_list(self, fio_combobox, list_widget):
        if not hasattr(self, 'fio_input') or not fio_combobox:
            return

        selected_full_name = fio_combobox.currentText()
        if not selected_full_name:
            return

        # Словарь соответствий: чекбокс -> значение в базе
        checkbox_to_db_status = {
            "Хранение": "хранение",
            "Поиск": "поиск",
            "Исправно": "исправно",
            "Ремонт": "ремонт",
            "Списано": "списано",
            "Показать уволенных": "уволено",
            "Перемещение": "перемещение",
            "Резерв": "резерв",
            "Не исправно": "не исправно",
            "На списание": "списано",
            "Утиль": "утилизировано"
        }

        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            # Получаем ID пользователя
            cursor.execute("SELECT old_id FROM CKR_users WHERE full_name_tabel = ?", (selected_full_name,))
            result = cursor.fetchone()
            if result:
                user_old_id = result[0]

                # Выбираем нужные чекбоксы
                if fio_combobox == self.fio_input:
                    checkboxes = self.checkboxes_left
                else:
                    checkboxes = self.checkboxes_right

                # Собираем отмеченные статусы из чекбоксов
                selected_statuses = [
                    checkbox_to_db_status[cb.text()]
                    for cb in checkboxes if cb.isChecked() and cb.text() in checkbox_to_db_status
                ]

                # Формируем SQL-запрос
                if selected_statuses:
                    placeholders = ','.join('?' for _ in selected_statuses)
                    query = f"""
                        SELECT full_device_data FROM Table_Devices 
                        WHERE assigned_to = ? AND status IN ({placeholders})
                    """
                    cursor.execute(query, (user_old_id, *selected_statuses))
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



    def move_action_func(self):

        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)

        # Основная сетка
        grid = QGridLayout()

       # Выпадающий список "Объект"
        grid.addWidget(QLabel("Объект"), 0, 0)
        self.fio_input = QComboBox()
        self.fio_input.setEditable(True)  # Разрешаем ввод текста
        self.fio_input.addItem("")
        grid.addWidget(self.fio_input, 1, 0)
        # Загружаем данные
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

        # Настраиваем автодополнение
        completer = QCompleter(user_list_input, self.fio_input)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        completer.setFilterMode(Qt.MatchFlag.MatchContains)
        self.fio_input.setCompleter(completer)

        grid.addWidget(QLabel("Объект"), 0, 2)
        self.fio_output = QComboBox()
        self.fio_output.setEditable(True)
        self.fio_output.addItem("")
        grid.addWidget(self.fio_output, 1, 2)
        # Загружаем данные
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
        # Настраиваем автодополнение
        completer_output = QCompleter(user_list_output, self.fio_output)
        completer_output.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        completer_output.setFilterMode(Qt.MatchFlag.MatchContains)
        self.fio_output.setCompleter(completer_output)

        self.fio_input.currentIndexChanged.connect(lambda: self.update_device_list(self.fio_input, self.list_left))
        self.fio_output.currentIndexChanged.connect(lambda: self.update_device_list(self.fio_output, self.list_right))
    

        grid.addWidget(QLabel("№ обращения"), 2, 0)
        self.request_input = QLineEdit()
        grid.addWidget(self.request_input, 3, 0)

        grid.addWidget(QLabel("Комментарий к обращению"), 4, 0)
        self.comment_input = QTextEdit()
        grid.addWidget(self.comment_input, 5, 0)
        self.comment_input.setFixedHeight(60)
        # Списки
        self.list_left = QListWidget()
        self.list_right = QListWidget()
        self.list_left.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        self.list_right.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        grid.addWidget(self.list_left, 6, 0)
        grid.addWidget(self.list_right, 6, 2)


        # Кнопки перемещения
        move_layout = QVBoxLayout()
        self.move_right_btn = QPushButton("Переместить---->>>")
        move_layout.addWidget(self.move_right_btn)
        grid.addLayout(move_layout, 6, 1)
        self.move_right_btn.setFixedHeight(60)

        # Чекбоксы
        checkbox_grid_left = QGridLayout()
        checkbox_grid_right = QGridLayout()
        options = [
            "Хранение", "Перемещение", "Поиск", "Резерв",
            "Исправно", "Не исправно", "Ремонт", "На списание",
            "Списано", "Утиль", "Показать уволенных"
        ]

        self.checkboxes_left = [QCheckBox(opt) for opt in options]
        self.checkboxes_right = [QCheckBox(opt) for opt in options]

        # Заполняем левую часть чекбоксов
        row, col = 0, 0
        for i, cb in enumerate(self.checkboxes_left):
            checkbox_grid_left.addWidget(cb, row, col)
            col += 1
            if col >= 2:  # Переход на следующую строку каждые 2 чекбокса
                col = 0
                row += 1

        # Заполняем правую часть чекбоксов
        row, col = 0, 0
        for i, cb in enumerate(self.checkboxes_right):
            checkbox_grid_right.addWidget(cb, row, col)
            col += 1
            if col >= 2:  # Переход на следующую строку каждые 2 чекбокса
                col = 0
                row += 1

        # Вставляем сетки чекбоксов в основную сетку
        grid.addLayout(checkbox_grid_left, 7, 0)
        grid.addLayout(checkbox_grid_right, 7, 2)


        # Добавляем сетку в основной макет
        main_layout.addLayout(grid)
        self.setCentralWidget(main_widget)
        for cb in self.checkboxes_left:
            cb.stateChanged.connect(lambda _, cb=cb: self.update_device_list(self.fio_input, self.list_left))
        for cb in self.checkboxes_right:
            cb.stateChanged.connect(lambda _, cb=cb: self.update_device_list(self.fio_output, self.list_right))
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
            now_str = f"{now.day}.{now.month}.{now.year} {now.hour}:{now.minute}:{now.second}"
            user_name = self.current_user
            ticket = self.request_input.text()
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
                """, (next_old_id, now_str, comment, user_name, device_id, to_id, from_id, ticket, comment))

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


    def authUI(self):
        layout = QVBoxLayout()
        
        self.label_user = QLabel("Пользователь:")
        self.input_user = QLineEdit()
        self.input_user.setFixedSize(200, 30)  # Ширина 200px, высота 30px
        layout.addWidget(self.label_user,alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.input_user,alignment=Qt.AlignmentFlag.AlignCenter)
        

        self.label_pass = QLabel("Пароль:")
        self.input_pass = QLineEdit()
        self.input_pass.setFixedSize(200, 30)
        self.input_pass.setEchoMode(QLineEdit.EchoMode.Password)
        self.label_pass.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.label_pass,alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.input_pass,alignment=Qt.AlignmentFlag.AlignCenter)
        
        
        self.login_btn = QPushButton("Войти")
        self.login_btn.clicked.connect(self.authenticate)
        layout.addWidget(self.login_btn)
        # Минимальный размер
        # Максимальный размер

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
        self.input_pass.returnPressed.connect(self.authenticate)

    def load_data_db(self, query):
        try:
            conn = get_db_connection()  # Подключение к базе данных SQLite
            cursor = conn.cursor()
            
            # Запрос без id
            cursor.execute(query)
            records = cursor.fetchall()
            
            self.data_table.setRowCount(len(records))
            self.data_table.setColumnCount(len(records[0]) if records else 0)  # Устанавливаем количество колонок
            
            for row_idx, row_data in enumerate(records):
                for col_idx, col_data in enumerate(row_data):
                    self.data_table.setItem(row_idx, col_idx, QTableWidgetItem(str(col_data)))
            
            cursor.close()
            conn.close()
        except sqlite3.Error as e:
            print(f"Ошибка подключения к базе данных: {e}")


    def on_cell_click(self, row, col):
        row_data = [self.data_table.item(row, c).text() for c in range(self.data_table.columnCount())]
        column_names = [self.data_table.horizontalHeaderItem(i).text() for i in range(self.data_table.columnCount())]
        
        # Извлекаем имя таблицы из запроса (храним в переменной, задаваемой при вызове show_db_func)
        self.edit_dialog = EditDialog(row_data, column_names, self.current_table_name, self)
        self.edit_dialog.exec()


    def save_edited_data(self):
        """Функция для сохранения отредактированных данных в базе данных"""
        if self.selected_row is None:
            print("Выберите строку для редактирования.")
            return
        
        try:
            updated_data = []
            for field in self.labels.keys():
                updated_data.append(self.edit_fields[field].text())
            
            # Сохранение изменений в базе данных
            conn = get_db_connection()
            cursor = conn.cursor()

            # Формируем запрос для обновления данных
            query = """
                UPDATE Table_Devices 
                SET old_id = ?, serial_number = ?, device_type = ?, year_of_release = ?, date_of_supply = ?, 
                    owner_of_device = ?, assigned_to = ?, status = ?, condition = ?, inv_number = ?, 
                    supplier = ?, price = ?, ship_number = ?, full_device_data = ?, description = ?, characteristics = ?,
                    project = ?, visible = ?, reserve = ?
                WHERE id = ?
            """
            cursor.execute(query, tuple(updated_data + [self.data_table.item(self.selected_row, 0).text()]))

            # Сохраняем изменения и закрываем соединение
            conn.commit()
            cursor.close()
            conn.close()

            print("Данные успешно обновлены!")

            # Перезагружаем данные в таблицу
            self.load_data_assets()

        except sqlite3.Error as e:
            print(f"Ошибка при сохранении данных: {e}")


if __name__ == "__main__":
    
    app = QApplication(sys.argv)
    window = App()
    window.show()

    sys.exit(app.exec())
