from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
import os

class navWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        # Home icon button
        home_path = os.path.join("Media", "Icons", "home-hashtag-svgrepo-com.svg")
        if os.path.exists(home_path):
            home_icon = QPushButton()
            home_icon.setIcon(QIcon(home_path))
            home_icon.setIconSize(home_icon.size() * 0.2)  # Make icon 60% of button size
            home_icon.setFixedSize(128, 128)
            home_icon.clicked.connect(lambda: self.button_clicked("Home"))
            layout.addWidget(home_icon)

        # Music icon button
        music_path = os.path.join("Media", "Icons", "music-svgrepo-com.svg")
        if os.path.exists(music_path):
            music_icon = QPushButton()
            music_icon.setIcon(QIcon(music_path))
            music_icon.setIconSize(music_icon.size() * 0.2)  # Make icon 60% of button size
            music_icon.setFixedSize(128, 128)
            music_icon.clicked.connect(lambda: self.button_clicked("Music"))
            layout.addWidget(music_icon)

        # Maps icon button
        maps_path = os.path.join("Media", "Icons", "route-square-svgrepo-com.svg")
        if os.path.exists(maps_path):
            maps_icon = QPushButton()
            maps_icon.setIcon(QIcon(maps_path))
            maps_icon.setIconSize(maps_icon.size() * 0.2)  # Make icon 60% of button size
            maps_icon.setFixedSize(128, 128)
            maps_icon.clicked.connect(lambda: self.button_clicked("Maps"))
            layout.addWidget(maps_icon)

        # Games icon button
        games_path = os.path.join("Media", "Icons", "gameboy-svgrepo-com.svg")
        if os.path.exists(games_path):
            games_icon = QPushButton()
            games_icon.setIcon(QIcon(games_path))
            games_icon.setIconSize(games_icon.size() * 0.2)  # Make icon 60% of button size
            games_icon.setFixedSize(128, 128)
            games_icon.clicked.connect(lambda: self.button_clicked("Games"))
            layout.addWidget(games_icon)

        layout.setAlignment(Qt.AlignCenter)
        self.setLayout(layout)

    def button_clicked(self, button_name):
        print(f"{button_name} button clicked!")
