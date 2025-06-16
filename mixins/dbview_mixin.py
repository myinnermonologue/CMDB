from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem
)
from db import get_db_connection
from sqlcipher3 import dbapi2 as sqlite3
class DbViewMixin:
    def __init__(self):
        self.records_per_page = 50  # или любое другое число
        self.current_page = 0
        self.total_records = 0
        self.current_query = ""
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

    def go_to_prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.load_data_db_with_pagination(self.current_query)

    def go_to_next_page(self):
        if (self.current_page + 1) * self.records_per_page < self.total_records:
            self.current_page += 1
            self.load_data_db_with_pagination(self.current_query)


    def load_data_db_with_pagination(self, query):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            offset = self.current_page * self.records_per_page
            paginated_query = f"{query} LIMIT {self.records_per_page} OFFSET {offset}"

            cursor.execute(paginated_query)
            records = cursor.fetchall()

            self.data_table.setRowCount(len(records))
            self.data_table.setColumnCount(len(records[0]) if records else 0)

            for row_idx, row_data in enumerate(records):
                for col_idx, col_data in enumerate(row_data):
                    self.data_table.setItem(row_idx, col_idx, QTableWidgetItem(str(col_data)))

            self.page_label.setText(f"Страница {self.current_page + 1} из {max(1, (self.total_records - 1) // self.records_per_page + 1)}")

            self.btn_prev.setEnabled(self.current_page > 0)
            self.btn_next.setEnabled((self.current_page + 1) * self.records_per_page < self.total_records)

            cursor.close()
            conn.close()
        except sqlite3.Error as e:
            print(f"Ошибка при загрузке данных с пагинацией: {e}")
    

    def update_total_record_count(self, query):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            count_query = f"SELECT COUNT(*) FROM ({query})"
            cursor.execute(count_query)
            self.total_records = cursor.fetchone()[0]
            cursor.close()
            conn.close()
        except sqlite3.Error as e:
            print(f"Ошибка при подсчёте записей: {e}")
            self.total_records = 0    

    def show_db_func(self, array, query):
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)  # Отступы по краям
        layout.setSpacing(10)  # Расстояние между элементами

        self.current_query = query 

        self.data_table = QTableWidget()
        self.data_table.setColumnCount(len(array))
        self.data_table.setHorizontalHeaderLabels(array)
        self.data_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.data_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.data_table.cellClicked.connect(self.on_cell_click)

        # Таблица занимает всё доступное пространство
        self.data_table.setSizePolicy(
            self.data_table.sizePolicy().horizontalPolicy(),
            self.data_table.sizePolicy().verticalPolicy().Expanding
        )

        layout.addWidget(self.data_table)

        # Кнопки пагинации с выравниванием по центру
        pagination_layout = QHBoxLayout()
        pagination_layout.addStretch(1)
        self.btn_prev = QPushButton("← Назад")
        self.btn_next = QPushButton("Вперёд →")
        self.page_label = QLabel()
        self.page_label.setFixedWidth(120)  # чтобы не скакал текст

        self.btn_prev.clicked.connect(self.go_to_prev_page)
        self.btn_next.clicked.connect(self.go_to_next_page)

        pagination_layout.addWidget(self.btn_prev)
        pagination_layout.addWidget(self.page_label)
        pagination_layout.addWidget(self.btn_next)
        pagination_layout.addStretch(1)

        layout.addLayout(pagination_layout)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Инициализация пагинации
        self.current_page = 0
        self.update_total_record_count(query)
        self.load_data_db_with_pagination(query)

    def extract_table_name(self, query):
        # Простой способ вытащить имя таблицы из SELECT-запроса
        lowered = query.lower()
        if "from" in lowered:
            return lowered.split("from")[1].split()[0]
        return ""
    
    def on_editing_finished(self):
        self.update_total_record_count(self.current_query)
        self.load_data_db_with_pagination(self.current_query)