from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton
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
        home_path = os.path.join("Media", "Icons", "home-hashtag-svgrepo-com.svg")
        if os.path.exists(home_path):
            home_icon = QPushButton(QSvgWidget(home_path))
            home_icon.setFixedSize(128, 128)
            layout.addWidget(home_icon)
        music_path = os.path.join("Media", "Icons", "music-svgrepo-com.svg")
        if os.path.exists(music_path):
            music_icon = QPushButton(QSvgWidget(music_path))
            music_icon.setFixedSize(128, 128)
            layout.addWidget(music_icon)
        maps_path = os.path.join("Media", "Icons", "route-square-svgrepo-com.svg")
        if os.path.exists(maps_path):
            maps_icon = QPushButton(QSvgWidget(maps_path))
            maps_icon.setFixedSize(128, 128)
            layout.addWidget(maps_icon)
        games_path = os.path.join("Media", "Icons", "gameboy-svgrepo-com.svg")
        if os.path.exists(games_path):
            games_icon = QPushButton(QSvgWidget(games_path))
            games_icon.setFixedSize(128, 128)
            layout.addWidget(games_icon)

        # Add more icons here as needed
        # e.g. settings_icon = QSvgWidget(...)
        # layout.addWidget(settings_icon)

        layout.setAlignment(Qt.AlignCenter)
        self.setLayout(layout)

        def button_clicked(self):
            print("Button clicked!")
