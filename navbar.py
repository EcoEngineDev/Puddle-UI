from PyQt5.QtWidgets import QWidget, QHBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtSvg import QSvgWidget
import os

class navWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        # Example: Add a home icon SVG
        svg_path = os.path.join("Media", "Icons", "home-hashtag-svgrepo-com.svg")
        if os.path.exists(svg_path):
            home_icon = QSvgWidget(svg_path)
            home_icon.setFixedSize(32, 32)
            layout.addWidget(home_icon)

        # Add more icons here as needed
        # e.g. settings_icon = QSvgWidget(...)
        # layout.addWidget(settings_icon)

        self.setLayout(layout)
