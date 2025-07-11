from PyQt6.QtGui import QPainter, QColor
from PyQt6.QtWidgets import QPushButton
from PyQt6.QtCore import pyqtSignal, Qt

from PyQt6.QtWidgets import QPushButton
from PyQt6.QtGui import QPainter, QColor
from PyQt6.QtCore import Qt, pyqtSignal


from PyQt6.QtWidgets import QPushButton
from PyQt6.QtGui import QPainter, QColor
from PyQt6.QtCore import Qt, pyqtSignal, QSize


class CardButton(QPushButton):
    leftClicked = pyqtSignal(object)
    rightClicked = pyqtSignal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.hovered = False
        self.setFlat(True)  # Important: prevent QPushButton from drawing a default background
        self.setStyleSheet("border: none; \n border-radius: 0px; ")  # Clean border, no background override

    def enterEvent(self, event):
        self.hovered = True
        self.update()

    def leaveEvent(self, event):
        self.hovered = False
        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.leftClicked.emit(self)
        elif event.button() == Qt.MouseButton.RightButton:
            self.rightClicked.emit(self)
        super().mousePressEvent(event)

    def paintEvent(self, event):
        super().paintEvent(event)  # ✅ Let QPushButton draw the icon first

        if self.hovered:
            # ✅ Only draw overlay AFTER icon
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter.setPen(Qt.PenStyle.NoPen)

            # Calculate icon area
            icon_size = self.iconSize()
            icon_x = (self.width() - icon_size.width()) // 2
            icon_y = (self.height() - icon_size.height()) // 2
            icon_rect = self.rect().adjusted(icon_x, icon_y, -icon_x, -icon_y)

            # Draw black overlay with some transparency
            painter.setBrush(QColor(0, 0, 0, 100))  # Change alpha to 255 for full black
            painter.drawRect(icon_rect)
