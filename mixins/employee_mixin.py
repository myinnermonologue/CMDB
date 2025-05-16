from PyQt6.QtWidgets import (
    QWidget, QGridLayout, QVBoxLayout, QLabel, QComboBox, QLineEdit, QTextEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QMessageBox, QCompleter, QFileDialog
)
from PyQt6.QtCore import Qt
from datetime import datetime
from db import get_db_connection
from openpyxl import Workbook
import os

class EmployeeMixin:
    def employee_action_func(self):
        main_widget = QWidget()
        main_layout = QGridLayout(main_widget)

        # === Левая часть ===
        form_layout = QGridLayout()

        self.combo_fio_employee = QComboBox()
        self.combo_fio_employee.setEditable(True)
        form_layout.addWidget(self.combo_fio_employee, 0, 0, 1, 2)

        self.label_to_column = {
            "Фамилия": "last_name",
            "Имя": "first_name",
            "Отчество": "patronymic",
            "Табельный": "tabel_num",
            "Компания": "company",
            "Отдел 1": "unit1",
            "Отдел 2": "unit2",
            "Отдел 3": "unit3",
            "Отдел 4": "unit4",
            "Отдел 5": "unit5",
            "Должность": "position",
            "Город": "city",
            "Статус": "status",
            "Руководитель": "supervisor",
            "Email": "email"
        }

        fields = list(self.label_to_column.keys())
        self.employee_fields = {}

        for i, label_text in enumerate(fields):
            label = QLabel(label_text)
            line_edit = QLineEdit()
            self.employee_fields[label_text] = line_edit
            form_layout.addWidget(label, i + 1, 0)
            form_layout.addWidget(line_edit, i + 1, 1)

        form_layout.addWidget(QLabel("Комментарий"), len(fields) + 1, 0)
        self.employee_comment = QTextEdit()
        self.employee_comment.setFixedHeight(50)
        form_layout.addWidget(self.employee_comment, len(fields) + 1, 1)

        self.btn_save_employee = QPushButton("Сохранить изменения")
        form_layout.addWidget(self.btn_save_employee, len(fields) + 2, 1)
        if self.current_user_role.lower() == "auditor":
            self.btn_save_employee.clicked.connect(
                lambda: (
                    QMessageBox.warning(self, "Нет доступа", "У вас нет прав на сохранение данных."),
                    self.load_employee_data()
                )
            )
        else:
            self.btn_save_employee.clicked.connect(self.save_employee_data)
        main_layout.addLayout(form_layout, 0, 0)

        # === Правая часть ===
        right_layout = QVBoxLayout()

        right_layout.addWidget(QLabel("Выданные активы"))
        self.issued_assets_text = QTextEdit()
        self.issued_assets_text.setReadOnly(True)
        right_layout.addWidget(self.issued_assets_text)

        self.btn_export_employee = QPushButton("Экспорт в excel")
        right_layout.addWidget(self.btn_export_employee)
        self.btn_export_employee.clicked.connect(self.export_issued_assets_to_excel)

        right_layout.addWidget(QLabel("История изменения"))
        self.employee_history_table = QTableWidget()
        self.employee_history_table.setColumnCount(5)
        self.employee_history_table.setHorizontalHeaderLabels(["Дата", "Тип", "Техника", "Основание", "Примечание"])
        self.employee_history_table.horizontalHeader().setStretchLastSection(True)
        right_layout.addWidget(self.employee_history_table)

        main_layout.addLayout(right_layout, 0, 1)

        self.setCentralWidget(main_widget)
        self.combo_fio_employee.currentIndexChanged.connect(self.load_employee_data)

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT full_name_tabel FROM CKR_users ORDER BY full_name_tabel ASC")
            users = [row[0] for row in cursor.fetchall() if row[0]]
            self.combo_fio_employee.addItem("")
            self.combo_fio_employee.addItems(users)

            completer = QCompleter(users)
            completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
            completer.setFilterMode(Qt.MatchFlag.MatchContains)
            self.combo_fio_employee.setCompleter(completer)
            cursor.close()
            conn.close()

        except Exception as e:
            print(f"Ошибка при загрузке сотрудников: {e}")

    def save_employee_data(self):
        full_name = self.combo_fio_employee.currentText().strip()
        if not full_name:
            QMessageBox.warning(self, "Ошибка", "Выберите сотрудника для сохранения.")
            return

        try:
            last_name = self.employee_fields["Фамилия"].text().strip()
            first_name = self.employee_fields["Имя"].text().strip()
            patronymic = self.employee_fields["Отчество"].text().strip()
            tabel_num = self.employee_fields["Табельный"].text().strip()
            tabel_num = str(tabel_num) if tabel_num else ""
            new_full_name = f"{last_name} {first_name} {patronymic} ({tabel_num})".strip()

            values = {
                self.label_to_column[label]: self.employee_fields[label].text().strip()
                for label in self.employee_fields
            }
            values.update({
                "description": self.employee_comment.toPlainText().strip(),
                "full_name_tabel": new_full_name
            })

            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT last_name, first_name, patronymic, tabel_num, company,
                        unit1, unit2, unit3, unit4, unit5,
                        position, city, status, supervisor, email, description, full_name_tabel
                FROM CKR_users
                WHERE full_name_tabel = ?
                LIMIT 1
            """, (full_name,))
            old_row = cursor.fetchone()
            old_keys = list(values.keys()) + ["full_name_tabel"]
            old_values = dict(zip(old_keys, [str(x) if x is not None else "" for x in old_row])) if old_row else {}

            set_clause = ", ".join([f'"{col}" = ?' for col in values])
            query = f"""
                UPDATE CKR_users
                SET {set_clause}
                WHERE full_name_tabel = ?
            """


            print("SQL-запрос:", query)
            print("Параметры:", [str(v) for v in list(values.values()) + [full_name]])

            cursor.execute(query, list(values.values()) + [full_name])
            conn.commit()

            self.load_employee_data()

            cursor.execute("SELECT DISTINCT full_name_tabel FROM CKR_users ORDER BY full_name_tabel ASC")
            users = [row[0] for row in cursor.fetchall() if row[0]]
            self.combo_fio_employee.blockSignals(True)
            self.combo_fio_employee.clear()
            self.combo_fio_employee.addItem("")
            self.combo_fio_employee.addItems(users)
            self.combo_fio_employee.setCurrentText(new_full_name)
            self.combo_fio_employee.blockSignals(False)

            completer = QCompleter(users)
            completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
            completer.setFilterMode(Qt.MatchFlag.MatchContains)
            self.combo_fio_employee.setCompleter(completer)

            cursor.execute("SELECT old_id FROM CKR_users WHERE full_name_tabel = ?", (new_full_name,))
            user_id_row = cursor.fetchone()
            user_old_id = user_id_row[0] if user_id_row else None

            # Получаем максимальный id для history_user
            cursor.execute("SELECT MAX(CAST(id AS INTEGER)) FROM history_user WHERE id GLOB '[0-9]*'")
            max_id = cursor.fetchone()[0]
            next_id = (max_id + 1) if max_id is not None else 1

            cursor.execute("SELECT MAX(CAST(old_id AS INTEGER)) FROM history_user WHERE old_id GLOB '[0-9]*'")
            max_old_id = cursor.fetchone()[0]
            next_old_id = (max_old_id + 1) if max_old_id is not None else 1

            now = f"{datetime.now().day}.{datetime.now().month}.{datetime.now().year} {datetime.now().strftime('%H:%M:%S')}"
            who_changed = getattr(self, "username", os.environ.get("USERNAME", ""))

            for key in values:
                old_val = old_values.get(key, "")
                new_val = values[key]
                if str(old_val) != str(new_val):
                    try:
                        cursor.execute("""
                            INSERT INTO history_user (id, old_id, date, type, user, description_of_change, who_changed)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                        """, (
                            next_id, next_old_id, now, "изменение поля", str(user_old_id), f"поле {key} было: {str(old_val)}", who_changed
                        ))
                        print(f"Добавлено: поле {key} было: {str(old_val)}")
                        next_id += 1
                    except Exception as e:
                        print(f"Ошибка при вставке (было): {e}")
                    try:
                        cursor.execute("""
                            INSERT INTO history_user (id, old_id, date, type, user, description_of_change, who_changed)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                        """, (
                            next_id, next_old_id, now, "изменение поля", str(user_old_id), f"поле {key} стало: {str(new_val)}", who_changed
                        ))
                        print(f"Добавлено: поле {key} стало: {str(new_val)}")
                        next_id += 1
                    except Exception as e:
                        print(f"Ошибка при вставке (стало): {e}")
                    next_old_id += 1
                    print(f"Добавляю в history_user: поле {key} было: {str(old_val)} -> стало: {str(new_val)}")

            conn.commit()
            cursor.close()
            conn.close()
            QMessageBox.information(self, "Успешно", "Данные сотрудника и история изменений успешно обновлены.")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить данные: {str(e)}")


        
    def export_issued_assets_to_excel(self):
        text = self.issued_assets_text.toPlainText().strip()
        fio = self.combo_fio_employee.currentText().strip()

        if not text:
            QMessageBox.warning(self, "Ошибка", "Нет данных для экспорта.")
            return

        if not fio:
            QMessageBox.warning(self, "Ошибка", "ФИО сотрудника не выбрано.")
            return

        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Сохранить как",
            "",
            "Excel файлы (*.xlsx)"
        )

        if not filepath:
            return  # пользователь отменил

        if not filepath.endswith(".xlsx"):
            filepath += ".xlsx"

        try:
            wb = Workbook()
            ws = wb.active
            ws.title = "Выданные активы"

            # Первая строка: ФИО сотрудника
            ws.append([fio])
            ws.append([])  # Пустая строка

            # Сами активы
            for line in text.splitlines():
                ws.append([line])

            # Автоширина колонки
            max_len = max((len(str(cell.value)) for cell in ws["A"] if cell.value), default=10)
            ws.column_dimensions['A'].width = max_len + 2

            wb.save(filepath)

            QMessageBox.information(self, "Экспорт завершён", f"Файл успешно сохранён:\n{filepath}")

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить файл:\n{str(e)}")

    def load_employee_data(self):
        full_name = self.combo_fio_employee.currentText().strip()
        if not full_name:
            for field in self.employee_fields.values():
                field.clear()
            self.employee_comment.clear()
            return

        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT last_name, first_name, patronymic, tabel_num, company,
                    unit1, unit2, unit3, unit4, unit5,
                    position, city, status, supervisor, email, description
                FROM CKR_users
                WHERE full_name_tabel = ?
                LIMIT 1
            """, (full_name,))
            row = cursor.fetchone()

            if row:
                keys = list(self.employee_fields.keys())
                for i, key in enumerate(keys):
                    if i < len(row):
                        self.employee_fields[key].setText(str(row[i]) if row[i] else "")

                # Комментарий
                self.employee_comment.setPlainText(str(row[-1]) if row[-1] else "")
            else:
                for field in self.employee_fields.values():
                    field.clear()
                self.employee_comment.clear()
                    # === Загрузка выданных активов ===
            self.issued_assets_text.clear()

            # Получаем old_id до закрытия курсора
            cursor.execute("SELECT old_id FROM CKR_users WHERE full_name_tabel = ?", (full_name,))
            user_id_row = cursor.fetchone()

            if user_id_row:
                user_id = user_id_row[0]

                cursor.execute("""
                    SELECT full_device_data 
                    FROM Table_Devices 
                    WHERE assigned_to = ? AND full_device_data IS NOT NULL
                    ORDER BY full_device_data
                """, (user_id,))
                assets = [row[0] for row in cursor.fetchall() if row[0]]

                if assets:
                    self.issued_assets_text.setPlainText("\n".join(assets))
                else:
                    self.issued_assets_text.setPlainText("Нет выданных активов.")
            else:
                self.issued_assets_text.setPlainText("Сотрудник не найден.")
                        # === Загрузка истории ===
            self.employee_history_table.setRowCount(0)

            cursor.execute("SELECT old_id FROM CKR_users WHERE full_name_tabel = ?", (full_name,))
            user_id_row = cursor.fetchone()

            if user_id_row:
                user_id = user_id_row[0]

                # Получаем историю, где where_moved = old_id
                cursor.execute("""
                    SELECT date, type_of_action, tech_move, ticket, description
                    FROM History
                    WHERE where_moved = ?
                    ORDER BY date DESC
                """, (user_id,))
                history_rows = cursor.fetchall()

                # Словарь: old_id -> full_device_data
                cursor.execute("SELECT old_id, full_device_data FROM Table_Devices")
                device_map = {str(row[0]): row[1] for row in cursor.fetchall() if row[1]}

                self.employee_history_table.setRowCount(len(history_rows))

                for row_idx, (date, action, tech_id, ticket, desc) in enumerate(history_rows):
                    tech_name = device_map.get(str(tech_id), "")
                    self.employee_history_table.setItem(row_idx, 0, QTableWidgetItem(str(date)))
                    self.employee_history_table.setItem(row_idx, 1, QTableWidgetItem(str(action)))
                    self.employee_history_table.setItem(row_idx, 2, QTableWidgetItem(str(tech_name)))
                    self.employee_history_table.setItem(row_idx, 3, QTableWidgetItem(str(ticket)))
                    self.employee_history_table.setItem(row_idx, 4, QTableWidgetItem(str(desc)))


            cursor.close()
            conn.close()

        except Exception as e:
            print(f"Ошибка при загрузке данных сотрудника: {e}")