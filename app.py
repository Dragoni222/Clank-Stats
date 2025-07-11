import sys
from PyQt6.QtWidgets import QApplication
from gui.main_window import CardGridViewer

def run_app():
    app = QApplication(sys.argv)
    viewer = CardGridViewer("cardpics")
    viewer.show()
    sys.exit(app.exec())
