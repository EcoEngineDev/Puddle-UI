from PyQt5.QtWidgets import QWidget, QGridLayout, QPushButton
from PyQt5.QtCore import QSize
from PyQt5.QtGui import QFont
# from debug_logger import debug_logger

class MusicMenu(QWidget):
    def __init__(self, parent=None):
        # debug_logger.log_function_entry("__init__", "MusicMenu", parent=parent)
        super().__init__(parent)
        self.setup_ui()
        self.hide()  # Hidden by default
        # debug_logger.log_function_exit("__init__", "MusicMenu")

    def setup_ui(self):
        # debug_logger.log_function_entry("setup_ui", "MusicMenu")
        layout = QGridLayout()
        layout.setSpacing(20)  # Space between buttons
        
        # Button style
        button_style = """
            QPushButton {
                background-color: #1A1A1A;
                color: #00FFA3;
                border: 2px solid #00FFA3;
                border-radius: 10px;
                padding: 15px;
                font-family: 'Lexend Bold';
                font-size: 18px;
            }
            QPushButton:hover {
                background-color: #00FFA3;
                color: #000000;
            }
        """
        
        # Create buttons
        options = [
            "YouTube Music",
            "Apple Music",
            "SoundCloud"
        ]
        
        self.buttons = {}  # Store buttons in a dictionary
        for i, text in enumerate(options):
            btn = QPushButton(text)
            btn.setFont(QFont("Lexend Bold"))
            btn.setStyleSheet(button_style)
            btn.setMinimumSize(QSize(200, 60))
            row = i // 2  # 2 buttons per row
            col = i % 2
            layout.addWidget(btn, row, col)
            self.buttons[text] = btn  # Store button reference
        
        layout.setContentsMargins(50, 50, 50, 50)  # Add some padding around the grid
        self.setLayout(layout)
        # debug_logger.log_function_exit("setup_ui", "MusicMenu") 