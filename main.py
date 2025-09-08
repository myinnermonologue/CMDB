import os
os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"
os.environ["QT_SCALE_FACTOR_ROUNDING_POLICY"] = "RoundPreferFloor"
# os.environ["QT_SCALE_FACTOR"] = "1"  # если хотите всегда 100%

import sys
import threading
from PyQt6.QtWidgets import QApplication
from main_window import MainWindow
from PyQt6.QtCore import QSettings
import shutil
import sqlite3
from sync import main as sync_main  # Синхронизация данных из Excel

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS  # PyInstaller
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def get_db_connection():
    db_file = "Database_CMDB.db"
    test_db_file = "test_cmdb.db"
    if not os.path.exists(db_file):
        # Если нет основной базы, копируем тестовую
        if os.path.exists(test_db_file):
            shutil.copyfile(test_db_file, db_file)
        else:
            raise FileNotFoundError("Нет ни основной базы, ни тестовой test_cmdb.db!")
    # Открываем как обычную SQLite-базу
    conn = sqlite3.connect(db_file)
    return conn

if __name__ == "__main__":
    # Опциональная синхронизация данных из Excel в фоне (не блокирует запуск)
    if os.getenv("CMDB_SYNC_ON_START", "0") == "1":
        threading.Thread(target=sync_main, daemon=True).start()
    app = QApplication(sys.argv)
    # icon_path = resource_path("icon.ico")
    # app.setWindowIcon(QIcon(icon_path))

    # --- Очистка QSettings при выходе из приложения ---
    def clear_store_settings():
        settings = QSettings('CKR', 'CMDB')
        settings.remove('store/fio_input')
        settings.remove('technic/search_field')
        settings.remove('move/fio_input')
        settings.remove('move/fio_output')
    app.aboutToQuit.connect(clear_store_settings)

    window = MainWindow()
    # window.setWindowIcon(QIcon(icon_path))
    screen = QApplication.primaryScreen().availableGeometry()
    window.setMinimumSize(int(screen.width() * 0.7), int(screen.height() * 0.7))
    # Убираем ограничение по высоте для полноценного разворота на весь экран
    window.setMaximumSize(int(screen.width() * 1), int(screen.height() * 1))
    window.showMaximized()
    sys.exit(app.exec())
 