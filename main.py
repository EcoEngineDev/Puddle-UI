from __future__ import annotations  # Add this at the top
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QStackedWidget, QPushButton, QHBoxLayout, QFrame, QGridLayout
from PyQt5.QtCore import Qt, QRectF, QPoint, QSize
from PyQt5.QtGui import QFontDatabase, QFont, QColor
from PyQt5.QtSvg import QSvgRenderer
from PyQt5.QtGui import QPainter
from boot import BootSequence
from speedometer import SpeedometerWidget
from navbar import navWidget
from map_widget import MapWidget
from youtube import YouTubeWidget
from movies import MoviesWidget
import os

class EntertainmentMenu(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.hide()  # Hidden by default

    def setup_ui(self):
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
            "YouTube", "Movies", "Board Games",
            "Wii Games", "Instagram", "Intellectual Games"
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

class MainUI(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Navigation bar at the top
        top_row = QVBoxLayout()
        top_row.setContentsMargins(0, 0, 0, 0)
        top_row.setSpacing(0)

        # nav widget home icon
        self.nav_widget = navWidget()
        self.nav_widget.button_clicked_signal.connect(self.handle_nav_button)
        top_row.addWidget(self.nav_widget)
        main_layout.addLayout(top_row)

        # Main content container
        content_container = QFrame()
        content_layout = QHBoxLayout(content_container)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        
        # Left side with speedometer - fixed position
        speedometer_container = QFrame()
        speedometer_layout = QVBoxLayout(speedometer_container)
        speedometer_layout.setContentsMargins(20, 20, 0, 0)
        self.speedometer = SpeedometerWidget()
        speedometer_layout.addWidget(self.speedometer)
        speedometer_layout.addStretch(1)
        content_layout.addWidget(speedometer_container, 0)
        
        # Center container for entertainment menu and YouTube
        center_container = QFrame()
        center_layout = QVBoxLayout(center_container)
        center_layout.setContentsMargins(0, 0, 0, 0)
        
        self.entertainment_menu = EntertainmentMenu()
        center_layout.addWidget(self.entertainment_menu)
        
        # Add web-based widgets
        self.youtube_widget = YouTubeWidget()
        center_layout.addWidget(self.youtube_widget)
        
        self.movies_widget = MoviesWidget()
        center_layout.addWidget(self.movies_widget)
        
        content_layout.addWidget(center_container, 1)
        
        # Connect entertainment buttons
        self.entertainment_menu.buttons["YouTube"].clicked.connect(self.show_youtube)
        self.entertainment_menu.buttons["Movies"].clicked.connect(self.show_movies)
        
        # Spacer to push speedometer left when map is hidden
        content_layout.addStretch(1)

        # Right side with map
        self.map_widget = MapWidget()
        self.map_widget.hide()
        content_layout.addWidget(self.map_widget, 1)

        main_layout.addWidget(content_container)
        main_layout.addStretch(1)

        # Bottom row with version and MALLARD text
        bottom_container = QFrame()
        bottom_container.setContentsMargins(0, 0, 0, 0)
        bottom_layout = QHBoxLayout(bottom_container)
        bottom_layout.setContentsMargins(4, 0, 4, 4)

        # Version label (left)
        version_container = QFrame()
        version_layout = QVBoxLayout(version_container)
        version_layout.setContentsMargins(0, 0, 0, 2)
        version_label = QLabel("Puddle Ver. 0.1 Alpha")
        version_label.setStyleSheet("color: #888; font-size: 12px;")
        version_layout.addStretch(1)
        version_layout.addWidget(version_label)
        bottom_layout.addWidget(version_container, 1)
        
        # MALLARD text (center)
        mallard_label = QLabel("M A L L A R D")
        mallard_font = QFont("Lexend Bold")
        mallard_font.setPixelSize(32)
        mallard_label.setFont(mallard_font)
        mallard_label.setStyleSheet("color: #FFFFFF; padding: 0 50px;")
        
        bottom_layout.addWidget(mallard_label)
        bottom_layout.addWidget(QWidget(), 1)

        main_layout.addWidget(bottom_container)

        self.setLayout(main_layout)
        self.setStyleSheet("background-color: #000000;")

    def show_youtube(self):
        self.entertainment_menu.hide()
        self.movies_widget.hide()
        self.youtube_widget.show()

    def show_movies(self):
        self.entertainment_menu.hide()
        self.youtube_widget.hide()
        self.movies_widget.show()

    def handle_nav_button(self, button_name):
        # Hide all content first
        self.map_widget.hide()
        self.entertainment_menu.hide()
        self.youtube_widget.hide()
        self.movies_widget.hide()
        
        # Show appropriate content based on button
        if button_name == "Maps":
            self.map_widget.show()
        elif button_name == "Games":
            self.entertainment_menu.show()
        elif button_name == "Home":
            pass  # Just hide everything

class CarInterface(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Puddle")
        self.setStyleSheet("background-color: #000000;")
        self.showFullScreen()

        # Create stacked widget to hold boot sequence and main screen
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        # Create and add boot sequence
        self.boot_sequence = BootSequence()
        self.boot_sequence.setStyleSheet("background-color: #000000;")
        self.stacked_widget.addWidget(self.boot_sequence)

        # Create and add main screen
        self.main_screen = MainUI(self)
        self.stacked_widget.addWidget(self.main_screen)

        # Connect boot sequence completion to switch to main screen
        self.boot_sequence.boot_complete.connect(self.show_main_screen)

        # Start boot sequence
        self.boot_sequence.start_boot_sequence()

    def show_main_screen(self):
        self.stacked_widget.setCurrentWidget(self.main_screen)

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Load custom fonts
    font_dir = "Fonts"
    for font_file in os.listdir(font_dir):
        if font_file.endswith(".ttf"):
            QFontDatabase.addApplicationFont(os.path.join(font_dir, font_file))

    # Create and show main interface
    interface = CarInterface()
    interface.show()

    sys.exit(app.exec()) 