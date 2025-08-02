from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton
from PyQt5.QtCore import Qt, pyqtSignal, QSize
from PyQt5.QtGui import QIcon
import os
# from debug_logger import debug_logger

class navWidget(QWidget):
    # Define signals for button clicks
    button_clicked_signal = pyqtSignal(str)

    def __init__(self, parent=None):
        # debug_logger.log_function_entry("__init__", "navWidget", parent=parent)
        super().__init__(parent)
        self.setup_ui()
        # debug_logger.log_function_exit("__init__", "navWidget")

    def setup_ui(self):
        # debug_logger.log_function_entry("setup_ui", "navWidget")
        layout = QHBoxLayout()
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(20)  # Increased spacing between buttons
        
        # Button style for better appearance
        button_style = """
            QPushButton {
                background-color: #1A1A1A;
                border: 2px solid #00FFA3;
                border-radius: 15px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #00FFA3;
                border-color: #00FFA3;
            }
            QPushButton:pressed {
                background-color: #008060;
                border-color: #008060;
            }
        """
        
        # Add stretch to center the buttons
        layout.addStretch(1)
        
        # Home button
        home_path = "Media/Icons/home-hashtag-svgrepo-com.svg"
        # debug_logger.log_debug(f"Loading home icon: {home_path}", "navWidget")
        if os.path.exists(home_path):
            home_btn = QPushButton()
            home_btn.setIcon(QIcon(home_path))
            home_btn.setIconSize(QSize(64, 64))  # Doubled icon size
            home_btn.setFixedSize(QSize(100, 100))  # Doubled button size
            home_btn.setStyleSheet(button_style)
            home_btn.clicked.connect(lambda: self.button_clicked_signal.emit("Home"))
            layout.addWidget(home_btn)
            # debug_logger.log_debug("Home icon button created", "navWidget")
        else:
            # debug_logger.log_warning(f"Home icon not found: {home_path}", "navWidget")
            pass
        
        # Music button
        music_path = "Media/Icons/music-svgrepo-com.svg"
        # debug_logger.log_debug(f"Loading music icon: {music_path}", "navWidget")
        if os.path.exists(music_path):
            music_btn = QPushButton()
            music_btn.setIcon(QIcon(music_path))
            music_btn.setIconSize(QSize(64, 64))  # Doubled icon size
            music_btn.setFixedSize(QSize(100, 100))  # Doubled button size
            music_btn.setStyleSheet(button_style)
            music_btn.clicked.connect(lambda: self.button_clicked_signal.emit("Music"))
            layout.addWidget(music_btn)
            # debug_logger.log_debug("Music icon button created", "navWidget")
        else:
            # debug_logger.log_warning(f"Music icon not found: {music_path}", "navWidget")
            pass
        
        # Maps button
        maps_path = "Media/Icons/route-square-svgrepo-com.svg"
        # debug_logger.log_debug(f"Loading maps icon: {maps_path}", "navWidget")
        if os.path.exists(maps_path):
            maps_btn = QPushButton()
            maps_btn.setIcon(QIcon(maps_path))
            maps_btn.setIconSize(QSize(64, 64))  # Doubled icon size
            maps_btn.setFixedSize(QSize(100, 100))  # Doubled button size
            maps_btn.setStyleSheet(button_style)
            maps_btn.clicked.connect(lambda: self.button_clicked_signal.emit("Maps"))
            layout.addWidget(maps_btn)
            # debug_logger.log_debug("Maps icon button created", "navWidget")
        else:
            # debug_logger.log_warning(f"Maps icon not found: {maps_path}", "navWidget")
            pass
        
        # Games button
        games_path = "Media/Icons/gameboy-svgrepo-com.svg"
        # debug_logger.log_debug(f"Loading games icon: {games_path}", "navWidget")
        if os.path.exists(games_path):
            games_btn = QPushButton()
            games_btn.setIcon(QIcon(games_path))
            games_btn.setIconSize(QSize(64, 64))  # Doubled icon size
            games_btn.setFixedSize(QSize(100, 100))  # Doubled button size
            games_btn.setStyleSheet(button_style)
            games_btn.clicked.connect(lambda: self.button_clicked_signal.emit("Games"))
            layout.addWidget(games_btn)
            # debug_logger.log_debug("Games icon button created", "navWidget")
        else:
            # debug_logger.log_warning(f"Games icon not found: {games_path}", "navWidget")
            pass
        
        # Add stretch to center the buttons
        layout.addStretch(1)
        self.setLayout(layout)
        # debug_logger.log_function_exit("setup_ui", "navWidget")

    def button_clicked(self, button_name):
        # debug_logger.log_debug(f"Button clicked: {button_name}", "navWidget")
        self.button_clicked_signal.emit(button_name)
