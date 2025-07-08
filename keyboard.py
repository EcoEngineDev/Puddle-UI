from PyQt5.QtWidgets import QWidget, QGridLayout, QPushButton, QVBoxLayout
from PyQt5.QtCore import Qt, pyqtSignal, QSize
from PyQt5.QtGui import QFont

class VirtualKeyboard(QWidget):
    key_pressed = pyqtSignal(str)  # Signal emitted when a key is pressed
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(5)
        self.setStyleSheet("""
            QPushButton {
                background-color: #1A1A1A;
                color: #00FFA3;
                border: 2px solid #00FFA3;
                border-radius: 5px;
                font-family: 'Lexend Bold';
                font-size: 16px;
                min-width: 40px;
                min-height: 40px;
            }
            QPushButton:pressed {
                background-color: #00FFA3;
                color: #000000;
            }
        """)
        
        # Main keyboard layout
        keyboard_layout = QGridLayout()
        keyboard_layout.setSpacing(5)
        
        # Define keyboard rows
        rows = [
            ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0'],
            ['q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p'],
            ['a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l'],
            ['z', 'x', 'c', 'v', 'b', 'n', 'm', '.', '/']
        ]
        
        # Add keys to layout
        for row_idx, row in enumerate(rows):
            for col_idx, key in enumerate(row):
                btn = QPushButton(key)
                btn.clicked.connect(lambda checked, k=key: self.key_pressed.emit(k))
                keyboard_layout.addWidget(btn, row_idx, col_idx)
        
        # Special keys row
        special_layout = QGridLayout()
        special_layout.setSpacing(5)
        
        # Space bar
        space_btn = QPushButton('Space')
        space_btn.clicked.connect(lambda: self.key_pressed.emit(' '))
        space_btn.setMinimumWidth(200)
        special_layout.addWidget(space_btn, 0, 0, 1, 3)
        
        # Backspace
        backspace_btn = QPushButton('⌫')
        backspace_btn.clicked.connect(lambda: self.key_pressed.emit('\b'))
        special_layout.addWidget(backspace_btn, 0, 3)
        
        # Enter
        enter_btn = QPushButton('Enter')
        enter_btn.clicked.connect(lambda: self.key_pressed.emit('\n'))
        special_layout.addWidget(enter_btn, 0, 4)
        
        # Hide keyboard button
        hide_btn = QPushButton('▼')
        hide_btn.clicked.connect(self.hide)
        special_layout.addWidget(hide_btn, 0, 5)
        
        layout.addLayout(keyboard_layout)
        layout.addLayout(special_layout)
        self.setLayout(layout)
        
    def showEvent(self, event):
        super().showEvent(event)
        # Ensure keyboard is always at the bottom of the screen
        if self.parent():
            self.move(0, self.parent().height() - self.height())
            
    def sizeHint(self):
        return QSize(800, 300)  # Reasonable default size for the keyboard 