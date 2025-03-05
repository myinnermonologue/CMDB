import sys
from PyQt6.QtWidgets import QGridLayout, QDialog, QApplication, QMainWindow, QPushButton, QLabel, QLineEdit, QVBoxLayout, QWidget, QTableWidget, QTableWidgetItem
from PyQt6.QtCore import Qt
import sqlite3
import xml.etree.ElementTree as ET
class EditDialog(QDialog):
    def __init__(self, row_data, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Редактирование данных")
        self.setGeometry(200, 200, 500, 400)  # Увеличим ширину, чтобы уместить две колонки

        self.row_data = row_data  # Данные выбранной строки
        self.edit_fields = {}

        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        grid = QGridLayout()  # Используем сетку для расположения элементов

        labels = [
            "Old ID", "Serial Number", "Device Type", "Year of Release", "Date of Supply", 
            "Owner of Device", "Assigned To", "Status", "Condition", "Inventory Number", 
            "Supplier", "Price", "Ship Number", "Full Device Data", "Description", "Characteristics", 
            "Project", "Visible", "Reserve"
        ]

        # Создаем поля для редактирования данных
        for idx, label in enumerate(labels):
            row = idx // 2  # Номер строки (каждый второй элемент переходит на новую строку)
            col = idx % 2   # Колонка (0 или 1)

            grid.addWidget(QLabel(label), row, col * 2)  # Метка
            field = QLineEdit(self)
            field.setText(str(self.row_data[idx]))
            self.edit_fields[label] = field
            grid.addWidget(field, row, col * 2 + 1)  # Поле ввода

        layout.addLayout(grid)

        # Кнопка для сохранения изменений
        save_btn = QPushButton("Сохранить изменения", self)
        save_btn.clicked.connect(self.save_changes)
        layout.addWidget(save_btn)

        self.setLayout(layout)
    
    def save_changes(self):
        """Сохраняем изменения и обновляем таблицу в главном окне"""
        updated_data = [field.text() for field in self.edit_fields.values()]
        
        try:
            conn = sqlite3.connect('tech_assets.db')
            cursor = conn.cursor()

            query = """
                UPDATE Table_Devices 
                SET old_id = ?, serial_number = ?, device_type = ?, year_of_release = ?, date_of_supply = ?, 
                    owner_of_device = ?, assigned_to = ?, status = ?, condition = ?, inv_number = ?, 
                    supplier = ?, price = ?, ship_number = ?, full_device_data = ?, description = ?, characteristics = ?,
                    project = ?, visible = ?, reserve = ?
                WHERE old_id = ?
            """
            cursor.execute(query, tuple(updated_data + [self.row_data[0]]))  # Обновление по old_id

            conn.commit()
            cursor.close()
            conn.close()

            print("Данные успешно обновлены!")

            # Автоматически обновляем данные в таблице
            if isinstance(self.parent(), App):
                self.parent().load_data()

            self.accept()  # Закрытие окна

        except sqlite3.Error as e:
            print(f"Ошибка при сохранении данных: {e}")



class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Авторизация")
        self.setGeometry(100, 100, 100, 100)
        self.authUI()
    
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

    def import_data_from_txt(self):
        try:
            # Открываем текстовый файл с кодировкой windows-1251
            with open("Tab_Tehnik.txt", "r", encoding="windows-1251") as file:
                lines = file.readlines()

            # Подключаемся к базе данных SQLite
            conn = sqlite3.connect('tech_assets.db')
            cursor = conn.cursor()

            for line in lines:
                # Разделяем строку на данные по символу ";"
                data = line.strip().split(';')

                # Убираем кавычки с полей, если они есть
                data = [field.replace('"', '') for field in data]

                # Если строка данных имеет меньше 19 элементов, добавляем пустые строки
                if len(data) < 19:
                    data.extend([''] * (19 - len(data)))  # Добавляем недостающие значения как пустые строки
                elif len(data) > 19:
                    data = data[:19]  # Обрезаем лишние данные, если их больше

                # Преобразуем цену в формат с точкой вместо запятой (если это необходимо)
                if data[11].replace(',', '').replace('.', '').isdigit():
                    data[11] = data[11].replace(',', '.')  # Преобразуем цену в формат с точкой

                # Выводим данные для отладки
                print(data)

                # Вставка данных в базу данных
                cursor.execute("""
                    INSERT INTO Table_Devices (
                        old_id, serial_number, device_type, year_of_release, date_of_supply, 
                        owner_of_device, assigned_to, status, condition, inv_number, 
                        supplier, price, ship_number, full_device_data, description, characteristics, 
                        project, visible, reserve
                    ) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, tuple(data))

            # Сохраняем изменения в базе данных и закрываем соединение
            conn.commit()
            cursor.close()
            conn.close()

            print("Данные успешно импортированы!")

        except Exception as e:
            print(f"Ошибка при импорте данных: {e}")
                    
    def fullUI(self):
        layout = QVBoxLayout()

        # Таблица для отображения данных
        self.data_table = QTableWidget()
        self.data_table.setColumnCount(19)  # 19 столбцов
        self.data_table.setHorizontalHeaderLabels([
            "old_id", "serial_number", "device_type", "year_of_release", "date_of_supply", 
            "owner_of_device", "assigned_to", "status", "condition", "inv_number", 
            "supplier", "price", "ship_number", "full_device_data", "description", "characteristics", 
            "project", "visible", "reserve"
        ])
        self.data_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.data_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.data_table.cellClicked.connect(self.on_cell_click)
        layout.addWidget(self.data_table)

        # Кнопка для загрузки данных
        load_data_btn = QPushButton("Загрузить данные", self)
        load_data_btn.clicked.connect(self.load_data)
        layout.addWidget(load_data_btn)

        self.import_txt_btn = QPushButton("Импортировать данные из TXT")
        self.import_txt_btn.clicked.connect(self.import_data_from_txt)  # подключение импорта
        layout.addWidget(self.import_txt_btn)
        # Контейнер для размещения всего интерфейса
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Загрузка данных из базы
        self.load_data()
    

    def authenticate(self):
        user = self.input_user.text()
        password = self.input_pass.text()
        
        if self.check_user_credentials(user, password):
            self.label_user.setText("Доступ разрешен")
            self.setGeometry(100, 100, 600, 400)
            self.fullUI()
        else:
            self.label_user.setText("Ошибка авторизации")
    
    def check_user_credentials(self, username, password):
        try:
            conn = sqlite3.connect('users.db')  # Подключение к базе SQLite
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
            conn = sqlite3.connect('tech_assets.db')  # Подключение к базе данных SQLite
            cursor = conn.cursor()
            
            # Запрос без id
            query = """SELECT old_id, serial_number, device_type, year_of_release, date_of_supply, 
                            owner_of_device, assigned_to, status, condition, inv_number, 
                            supplier, price, ship_number, full_device_data, description, characteristics, 
                            project, visible, reserve FROM Table_Devices"""
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


    def on_cell_click(self, row, column):
        """Когда ячейка таблицы выбрана, открываем диалог с данными"""
        row_data = []
        for col in range(self.data_table.columnCount()):
            row_data.append(self.data_table.item(row, col).text())
        
        # Открытие диалогового окна для редактирования данных
        self.edit_dialog = EditDialog(row_data, self)
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
            conn = sqlite3.connect('tech_assets.db')
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
            self.load_data()

        except sqlite3.Error as e:
            print(f"Ошибка при сохранении данных: {e}")



    def import_data_from_txt(self):
        try:
            # Открываем текстовый файл с кодировкой windows-1251
            with open("Tab_Tehnik.txt", "r", encoding="windows-1251") as file:
                lines = file.readlines()

            # Подключаемся к базе данных SQLite
            conn = sqlite3.connect('tech_assets.db')
            cursor = conn.cursor()

            for line in lines:
                # Разделяем строку на данные по символу ";"
                data = line.strip().split(';')

                # Убираем кавычки с полей, если они есть
                data = [field.replace('"', '') for field in data]

                # Удостоверимся, что строка данных имеет 19 элементов
                if len(data) < 19:
                    # Добавляем пустые строки для недостающих данных
                    data.extend([''] * (19 - len(data)))
                elif len(data) > 19:
                    # Обрезаем лишние данные, если их больше
                    data = data[:19]

                # Преобразуем цену в формат с точкой вместо запятой (если это необходимо)
                if data[11].replace(',', '').replace('.', '').isdigit():
                    data[11] = data[11].replace(',', '.')  # Преобразуем цену в формат с точкой

                # Выводим данные для отладки
                print(data)

                # Вставка данных в базу данных
                cursor.execute("""
                    INSERT INTO Table_Devices (
                        old_id, serial_number, device_type, year_of_release, date_of_supply, 
                        owner_of_device, assigned_to, status, condition, inv_number, 
                        supplier, price, ship_number, full_device_data, description, characteristics, 
                        project, visible, reserve
                    ) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, tuple(data))

            # Сохраняем изменения в базе данных и закрываем соединение
            conn.commit()
            cursor.close()
            conn.close()

            print("Данные успешно импортированы!")

        except Exception as e:
            print(f"Ошибка при импорте данных: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = App()
    window.show()

    sys.exit(app.exec())
