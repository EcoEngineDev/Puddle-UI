from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt
from PyQt5.QtSvg import QGraphicsSvgItem
from PyQt5.QtGui import QFont, QPainter, QColor, QPen, QFontDatabase, QRadialGradient, QBrush
import math
import os

class navWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        

        self.setFocusPolicy(Qt.StrongFocus)
        # Load Lexend-Thin font if available
        font_path = "Fonts/Lexend-Thin.ttf"
        if QFontDatabase.addApplicationFont(font_path) != -1:
            self.lexend_font = QFont("Lexend Thin", 24, QFont.Normal)
            self.lexend_font_small = QFont("Lexend Thin", 16, QFont.Normal)
        else:
            self.lexend_font = QFont("Arial", 24, QFont.Normal)
            self.lexend_font_small = QFont("Arial", 16, QFont.Normal)

    
    def setup_ui(self):
        # SVG item
        svg_path = os.path.join("Media", "Icons", "home-hashtag-svgrepo-com.svg")
        self.svg_item = QGraphicsSvgItem(svg_path)
        self.svg_item.setFlags(self.svg_item.ItemClipsToShape)
        self.svg_item.setCacheMode(self.svg_item.NoCache)
        self.svg_item.setZValue(0)
        self.svg_item.setTransformOriginPoint(self.svg_item.boundingRect().center())
        self.svg_item.setScale(4.0)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Up:
            self.set_speed(self.speed + 1)
        elif event.key() == Qt.Key_Down:
            self.set_speed(self.speed - 1)
        else:
            super().keyPressEvent(event)

    def focusInEvent(self, event):
        self.setStyleSheet("border: 2px solid #007acc;")
        super().focusInEvent(event)

    def focusOutEvent(self, event):
        self.setStyleSheet("")
        super().focusOutEvent(event)
