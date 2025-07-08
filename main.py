import sys
from PyQt6.QtWidgets import QApplication
from main_window import MainWindow
from PyQt6.QtCore import QSettings

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # --- Очистка QSettings при выходе из приложения ---
    def clear_store_settings():
        settings = QSettings('CKR', 'CMDB')
        settings.remove('store/fio_input')
        settings.remove('technic/search_field')
        settings.remove('move/fio_input')
        settings.remove('move/fio_output')
    app.aboutToQuit.connect(clear_store_settings)

    window = MainWindow()
    screen = QApplication.primaryScreen().availableGeometry()
    print(screen.width(), screen.height())
    window.setMinimumSize(int(screen.width() * 0.7), int(screen.height() * 0.7))
    window.setMaximumSize(int(screen.width() * 1), int(screen.height() * 0.98))
    window.showMaximized()
    sys.exit(app.exec())
 