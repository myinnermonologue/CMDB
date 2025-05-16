from PyQt6.QtWidgets import QDialog, QVBoxLayout, QGridLayout, QLabel, QLineEdit, QPushButton
from PyQt6.QtCore import pyqtSignal
from db import get_db_connection

class EditDialog(QDialog):
    editingFinished = pyqtSignal()
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
            self.accept()
            self.editingFinished.emit()
            super().accept()
        except Exception as e:
            print(f"Ошибка при сохранении данных: {e}")