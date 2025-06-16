from db import get_db_connection
from sqlcipher3 import dbapi2 as sqlite3
from dialogs import EditDialog
from PyQt6.QtWidgets import QMessageBox
class EditDialogMixin:
    def on_cell_click(self, row):
        row_data = [self.data_table.item(row, c).text() for c in range(self.data_table.columnCount())]
        column_names = [self.data_table.horizontalHeaderItem(i).text() for i in range(self.data_table.columnCount())]
        self.edit_dialog = EditDialog(row_data, column_names, self.current_table_name, self)
        self.edit_dialog.editingFinished.connect(self.on_editing_finished)
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

            QMessageBox.information(self, "Успешно", "Данные успешно обновлены!")

            # Перезагружаем данные в таблицу
        except sqlite3.Error as e:
            print(f"Ошибка при сохранении данных: {e}")

        