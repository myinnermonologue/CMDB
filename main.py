import sys
from PyQt6.QtWidgets import QApplication
from main_window import MainWindow
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    screen = QApplication.primaryScreen().availableGeometry()
    print(screen.width(), screen.height())
    window.setMinimumSize(int(screen.width() * 0.7), int(screen.height() * 0.7))
    window.setMaximumSize(int(screen.width() * 1), int(screen.height() * 0.98))
    window.showMaximized()
    sys.exit(app.exec())
