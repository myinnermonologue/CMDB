import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from main_window import MainWindow
from PyQt6.QtCore import QSettings

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS  # PyInstaller
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    icon_path = resource_path("icon.ico")
    app.setWindowIcon(QIcon(icon_path))

    # --- Очистка QSettings при выходе из приложения ---
    def clear_store_settings():
        settings = QSettings('CKR', 'CMDB')
        settings.remove('store/fio_input')
        settings.remove('technic/search_field')
        settings.remove('move/fio_input')
        settings.remove('move/fio_output')
    app.aboutToQuit.connect(clear_store_settings)

    window = MainWindow()
    window.setWindowIcon(QIcon(icon_path))
    screen = QApplication.primaryScreen().availableGeometry()
    print(screen.width(), screen.height())
    window.setMinimumSize(int(screen.width() * 0.7), int(screen.height() * 0.7))
    window.setMaximumSize(int(screen.width() * 1), int(screen.height() * 0.98))
    window.showMaximized()
    sys.exit(app.exec())
 