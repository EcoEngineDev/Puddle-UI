import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QStackedWidget, QPushButton, QHBoxLayout
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QFontDatabase, QFont, QColor
from PyQt5.QtSvg import QSvgRenderer
from PyQt5.QtGui import QPainter
from boot import BootSequence
from speedometer import SpeedometerWidget
from navbar import navWidget
from map_widget import MapWidget

class MainUI(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Navigation bar at the top
        top_row = QVBoxLayout()
        top_row.setContentsMargins(0, 0, 0, 0)

        # nav wdiget home icon
        self.nav_widget = navWidget()
        top_row.addWidget(self.nav_widget, alignment=Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
        main_layout.addLayout(top_row)

        # Center content layout
        center_content = QHBoxLayout()
        
        # Left side with speedometer
        left_side = QVBoxLayout()
        self.speedometer = SpeedometerWidget()
        left_side.addWidget(self.speedometer, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        left_side.setContentsMargins(40, 20, 0, 0)  # Reduced left margin from 120 to 40
        left_side.addStretch()
        center_content.addLayout(left_side)

        # Right side with map
        right_side = QVBoxLayout()
        self.map_widget = MapWidget()
        right_side.addWidget(self.map_widget)
        right_side.setContentsMargins(20, 20, 20, 20)
        center_content.addLayout(right_side, stretch=2)  # Map takes 2/3 of the space

        main_layout.addLayout(center_content)

        # Bottom row layout for MALLARD text (center) and version (left)
        bottom_row = QHBoxLayout()
        bottom_row.setContentsMargins(0, 0, 0, 20)  # Add bottom margin

        # Version label (left)
        version_label = QLabel("Puddle Ver. 0.1 Alpha")
        version_label.setStyleSheet("color: #888; font-size: 12px;")
        version_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignBottom)
        bottom_row.addWidget(version_label, alignment=Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignBottom)
        
        bottom_row.addStretch()  # Add stretch before center text

        # MALLARD text (center)
        mallard_label = QLabel("M A L L A R D")
        mallard_font = QFont("Lexend Bold")  # Use Lexend Bold directly
        mallard_font.setPixelSize(32)  # Larger font size
        mallard_label.setFont(mallard_font)
        mallard_label.setStyleSheet("color: #FFFFFF;")  # White text
        mallard_label.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignBottom)
        bottom_row.addWidget(mallard_label, alignment=Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignBottom)
        
        bottom_row.addStretch()  # Add stretch after center text

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
        self.close_button.clicked.connect(self.handle_close)
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

    def handle_close(self):
        self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    # Load Lexend font
    font_path = "Fonts/Lexend-Regular.ttf"
    if QFontDatabase.addApplicationFont(font_path) != -1:
        app.setFont(QFont("Lexend", 12))
    interface = CarInterface()
    interface.show()
    sys.exit(app.exec_()) 