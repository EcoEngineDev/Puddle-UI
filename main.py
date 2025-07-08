from __future__ import annotations  # Add this at the top
import warnings
import sys

# Filter out all PyQt5 deprecation warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QStackedWidget, QPushButton, QHBoxLayout, QFrame, QGridLayout
from PyQt5.QtCore import Qt, QRectF, QPoint, QSize
from PyQt5.QtGui import QFontDatabase, QFont, QColor
from PyQt5.QtSvg import QSvgRenderer
from PyQt5.QtGui import QPainter
from boot import BootSequence
from speedometer import SpeedometerWidget
from navbar import navWidget
from maps import MapsWidget
from youtube import YouTubeWidget
from movies import MoviesWidget
from music_menu import MusicMenu
from youtube_music import YouTubeMusicWidget
from apple_music import AppleMusicWidget
from soundcloud import SoundCloudWidget
from intellectual_games_widget import IntellectualGamesWidget
import os

class EntertainmentMenu(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        # Main layout to center the grid
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Container for grid to allow centering
        grid_container = QFrame()
        grid_container.setStyleSheet("background: transparent;")
        grid_layout = QGridLayout(grid_container)
        grid_layout.setSpacing(20)  # Space between buttons
        
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
            btn.setFixedSize(QSize(250, 80))  # Fixed size for consistent layout
            row = i // 2  # 2 buttons per row
            col = i % 2
            grid_layout.addWidget(btn, row, col)
            self.buttons[text] = btn
        
        # Center the grid in the widget
        main_layout.addStretch(1)
        main_layout.addWidget(grid_container)
        main_layout.addStretch(1)
        
        # Center horizontally
        container_layout = QHBoxLayout()
        container_layout.addStretch(1)
        container_layout.addLayout(main_layout)
        container_layout.addStretch(1)
        
        self.setLayout(container_layout)
        self.setStyleSheet("background-color: transparent;")

class MainUI(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        # Main vertical layout for the entire UI
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Navigation bar at the top
        self.nav_widget = navWidget()
        self.nav_widget.button_clicked_signal.connect(self.handle_nav_button)
        main_layout.addWidget(self.nav_widget)

        # Content area (middle section)
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
        
        # Center container with stacked widget
        center_container = QFrame()
        center_layout = QVBoxLayout(center_container)
        center_layout.setContentsMargins(0, 0, 0, 0)
        center_layout.setSpacing(0)
        
        # Create stacked widget for content management
        self.content_stack = QStackedWidget()
        
        # Create all widgets
        self.entertainment_menu = EntertainmentMenu()
        self.youtube_widget = YouTubeWidget()
        self.movies_widget = MoviesWidget()
        self.music_menu = MusicMenu()
        self.youtube_music_widget = YouTubeMusicWidget()
        self.apple_music_widget = AppleMusicWidget()
        self.soundcloud_widget = SoundCloudWidget()
        self.intellectual_games_widget = IntellectualGamesWidget()
        
        # Add widgets to stack
        self.content_stack.addWidget(self.entertainment_menu)
        self.content_stack.addWidget(self.youtube_widget)
        self.content_stack.addWidget(self.movies_widget)
        self.content_stack.addWidget(self.music_menu)
        self.content_stack.addWidget(self.youtube_music_widget)
        self.content_stack.addWidget(self.apple_music_widget)
        self.content_stack.addWidget(self.soundcloud_widget)
        self.content_stack.addWidget(self.intellectual_games_widget)
        
        center_layout.addWidget(self.content_stack)
        content_layout.addWidget(center_container, 1)
        
        # Connect entertainment buttons
        self.entertainment_menu.buttons["YouTube"].clicked.connect(self.show_youtube)
        self.entertainment_menu.buttons["Movies"].clicked.connect(self.show_movies)
        self.entertainment_menu.buttons["Intellectual Games"].clicked.connect(self.show_intellectual_games)
        
        # Connect music menu buttons
        self.music_menu.buttons["YouTube Music"].clicked.connect(self.show_youtube_music)
        self.music_menu.buttons["Apple Music"].clicked.connect(self.show_apple_music)
        self.music_menu.buttons["SoundCloud"].clicked.connect(self.show_soundcloud)
        
        # Right side with map
        self.map_widget = MapsWidget()
        content_layout.addWidget(self.map_widget, 1)
        self.map_widget.hide()

        main_layout.addWidget(content_container, 1)  # Give content area stretch

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
        mallard_label.setAlignment(Qt.AlignCenter)
        
        bottom_layout.addWidget(mallard_label)
        bottom_layout.addWidget(QWidget(), 1)  # Spacer

        main_layout.addWidget(bottom_container)

        self.setLayout(main_layout)
        self.setStyleSheet("background-color: #000000;")
        
        # Show initial content
        self.content_stack.setCurrentWidget(self.entertainment_menu)

    def show_youtube(self):
        self.map_widget.hide()
        self.content_stack.setCurrentWidget(self.youtube_widget)

    def show_movies(self):
        self.map_widget.hide()
        self.content_stack.setCurrentWidget(self.movies_widget)

    def show_intellectual_games(self):
        self.map_widget.hide()
        self.content_stack.setCurrentWidget(self.intellectual_games_widget)

    def show_music_menu(self):
        self.map_widget.hide()
        self.content_stack.setCurrentWidget(self.music_menu)

    def show_youtube_music(self):
        self.map_widget.hide()
        self.content_stack.setCurrentWidget(self.youtube_music_widget)

    def show_apple_music(self):
        self.map_widget.hide()
        self.content_stack.setCurrentWidget(self.apple_music_widget)

    def show_soundcloud(self):
        self.map_widget.hide()
        self.content_stack.setCurrentWidget(self.soundcloud_widget)

    def handle_nav_button(self, button_name):
        if button_name == "Maps":
            self.content_stack.hide()
            self.map_widget.show()
        elif button_name == "Games":
            self.map_widget.hide()
            self.content_stack.show()
            self.content_stack.setCurrentWidget(self.entertainment_menu)
        elif button_name == "Music":
            self.map_widget.hide()
            self.content_stack.show()
            self.content_stack.setCurrentWidget(self.music_menu)
        elif button_name == "Home":
            self.map_widget.hide()
            self.content_stack.show()
            self.content_stack.setCurrentWidget(self.entertainment_menu)

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