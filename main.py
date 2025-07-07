import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QStackedWidget, QPushButton, QHBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFontDatabase, QFont
from boot import BootSequence
from speedometer import SpeedometerWidget

class MainUI(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Speedometer in top left with offset
        self.speedometer = SpeedometerWidget()
        speedo_layout = QVBoxLayout()
        speedo_layout.addWidget(self.speedometer, alignment=Qt.AlignTop | Qt.AlignLeft)
        speedo_layout.setContentsMargins(120, 20, 0, 0)  # Offset from top and left
        main_layout.addLayout(speedo_layout)

        # Spacer to push bottom labels down
        main_layout.addStretch()

        # Bottom row layout for version (left) and MALLARD (center)
        bottom_row = QHBoxLayout()
        bottom_row.setContentsMargins(0, 0, 0, 0)

        # Version label at the bottom left
        version_label = QLabel("Puddle Ver. 0.1 Alpha")
        version_label.setStyleSheet("color: #888; font-size: 12px;")
        version_label.setAlignment(Qt.AlignLeft | Qt.AlignBottom)
        bottom_row.addWidget(version_label, alignment=Qt.AlignLeft | Qt.AlignBottom)

        # Center MALLARD label (expand to center)
        mallard_label = QLabel("M A L L A R D")
        mallard_label.setStyleSheet("color: #fff; font-size: 24px; font-family: 'Lexend Bold', 'Lexend', Arial, sans-serif; letter-spacing: 0.5em;")
        mallard_label.setAlignment(Qt.AlignCenter | Qt.AlignBottom)
        bottom_row.addStretch()
        bottom_row.addWidget(mallard_label, alignment=Qt.AlignCenter | Qt.AlignBottom)
        bottom_row.addStretch()

        main_layout.addLayout(bottom_row)
        self.setLayout(main_layout)
        self.setStyleSheet("background-color: #000;")

class CarInterface(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MALLARD Car Interface")
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setStyleSheet("background-color: #000;")
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        self.boot_screen = BootSequence()
        self.main_screen = MainUI(self)
        self.stacked_widget.addWidget(self.boot_screen)
        self.stacked_widget.addWidget(self.main_screen)
        self.boot_screen.boot_complete.connect(self.show_main_ui)
        self.stacked_widget.setCurrentWidget(self.boot_screen)
        self.showFullScreen()
        self.boot_screen.start_boot_sequence()

        # Add debug close button (red circle) in bottom right
        self.close_button = QPushButton(self)
        self.close_button.setFixedSize(32, 32)
        self.close_button.setStyleSheet('''
            QPushButton {
                background-color: #ff2222;
                border-radius: 16px;
                border: none;
            }
            QPushButton:hover {
                background-color: #ff5555;
            }
        ''')
        self.close_button.clicked.connect(self.close)
        self.close_button.raise_()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Position close button in bottom right corner
        margin = 16
        if hasattr(self, 'close_button'):
            self.close_button.move(self.width() - self.close_button.width() - margin, self.height() - self.close_button.height() - margin)

    def show_main_ui(self):
        self.stacked_widget.setCurrentWidget(self.main_screen)
        self.main_screen.speedometer.setFocus()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    # Load Lexend font
    font_path = "Fonts/Lexend-Regular.ttf"
    if QFontDatabase.addApplicationFont(font_path) != -1:
        app.setFont(QFont("Lexend", 12))
    interface = CarInterface()
    interface.show()
    sys.exit(app.exec_()) 