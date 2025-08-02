from __future__ import annotations  # Add this at the top
import warnings
import sys
import os
from dotenv import load_dotenv

# Import widget size configuration
from widget_config import WIDGET_WIDTH, WIDGET_HEIGHT, MINIMAP_SIZE

# Filter out all PyQt5 deprecation warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Import all PyQt modules first
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, 
    QStackedWidget, QPushButton, QHBoxLayout, QFrame, QGridLayout
)
from PyQt5.QtCore import Qt, QRectF, QPoint, QSize, QEvent
from PyQt5.QtGui import QFontDatabase, QFont, QColor, QKeyEvent
from PyQt5.QtSvg import QSvgRenderer
from PyQt5.QtGui import QPainter

# Now import the debug logger (commented out for now)
# from debug_logger import debug_logger, log_function

# Load environment variables from .env file
print("Loading environment variables")
load_dotenv()

# Debug: Check if API key is loaded
api_key = os.getenv("GOOGLE_MAPS_API_KEY")
if api_key:
    print(f"Google Maps API key loaded successfully (length: {len(api_key)})")
else:
    print("Google Maps API key not found in environment variables")

# Import custom modules
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
from mini_map import MiniMapWidget
from boot_animation import BootAnimation
from clock_widget import ClockWidget, TimeOnlyWidget, DateOnlyWidget

class EntertainmentMenu(QWidget):
    def __init__(self, parent=None):
        # debug_logger.log_function_entry("__init__", "EntertainmentMenu", parent=parent)
        super().__init__(parent)
        self.setup_ui()
        # debug_logger.log_function_exit("__init__", "EntertainmentMenu")

    def setup_ui(self):
        # debug_logger.log_function_entry("setup_ui", "EntertainmentMenu")
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
        # debug_logger.log_function_exit("setup_ui", "EntertainmentMenu")

class MainUI(QWidget):
    def __init__(self, parent=None):
        # debug_logger.log_function_entry("__init__", "MainUI", parent=parent)
        super().__init__(parent)
        self.setup_ui()
        # debug_logger.log_function_exit("__init__", "MainUI")

    def setup_ui(self):
        # debug_logger.log_function_entry("setup_ui", "MainUI")
        # Main vertical layout for the entire UI
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Navigation bar at the top
        # debug_logger.log_info("Creating navigation widget", "MainUI")
        self.nav_widget = navWidget()
        self.nav_widget.button_clicked_signal.connect(self.handle_nav_button)
        main_layout.addWidget(self.nav_widget)

        # Date display below navbar
        date_container = QFrame()
        date_layout = QHBoxLayout(date_container)
        date_layout.setContentsMargins(0, 5, 0, 5)
        
        # Create date widget (shows date only)
        self.date_widget = DateOnlyWidget()
        self.date_widget.setFixedHeight(25)  # Reduced height
        
        # Create time widget (shows time only)
        self.time_widget = TimeOnlyWidget()
        self.time_widget.setFixedHeight(25)  # Same height as date
        
        date_layout.addStretch(1)
        date_layout.addWidget(self.date_widget)
        date_layout.addSpacing(20)  # Space between date and time
        date_layout.addWidget(self.time_widget)  # Time next to date
        date_layout.addStretch(1)
        
        main_layout.addWidget(date_container)

        # Content area (middle section)
        content_container = QFrame()
        content_layout = QHBoxLayout(content_container)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        
        # Left side with speedometer - fixed position
        # debug_logger.log_info("Creating speedometer widget", "MainUI")
        speedometer_container = QFrame()
        speedometer_layout = QVBoxLayout(speedometer_container)
        speedometer_layout.setContentsMargins(20, 10, 0, 0)  # Reduced top margin from 20 to 10
        self.speedometer = SpeedometerWidget()
        speedometer_layout.addWidget(self.speedometer)
        speedometer_layout.addStretch(1)
        # The '0' parameter gives this widget a fixed size (stretch factor 0)
        content_layout.addWidget(speedometer_container, 0)
        # debug_logger.log_info("Speedometer widget created", "MainUI")
        
        # Center container with stacked widget
        center_container = QFrame()
        center_layout = QVBoxLayout(center_container)
        center_layout.setContentsMargins(0, 0, 0, 0)
        center_layout.setSpacing(0)
        
        # Create stacked widget for content management
        self.content_stack = QStackedWidget()
        
        # Create all widgets
        # debug_logger.log_info("Creating entertainment menu", "MainUI")
        self.entertainment_menu = EntertainmentMenu()
        # debug_logger.log_info("Creating YouTube widget", "MainUI")
        self.youtube_widget = YouTubeWidget()
        # debug_logger.log_info("Creating movies widget", "MainUI")
        self.movies_widget = MoviesWidget()
        # debug_logger.log_info("Creating music menu", "MainUI")
        self.music_menu = MusicMenu()
        # debug_logger.log_info("Creating YouTube music widget", "MainUI")
        self.youtube_music_widget = YouTubeMusicWidget()
        # debug_logger.log_info("Creating Apple music widget", "MainUI")
        self.apple_music_widget = AppleMusicWidget()
        # debug_logger.log_info("Creating SoundCloud widget", "MainUI")
        self.soundcloud_widget = SoundCloudWidget()
        # debug_logger.log_info("Creating intellectual games widget", "MainUI")
        self.intellectual_games_widget = IntellectualGamesWidget()
        
        # Google Maps widget (shared for both main map and minimap)
        # debug_logger.log_info("Creating shared Google Maps widget", "MainUI")
        try:
            # Create a container for the maps widget (similar to YouTube widget)
            self.maps_container = QFrame()
            maps_container_layout = QVBoxLayout(self.maps_container)
            # Change these values to modify map container margins
            # Current: 20px margins (same as YouTube widget)
            maps_container_layout.setContentsMargins(20, 20, 20, 20)  # Same margins as YouTube
            maps_container_layout.setSpacing(0)
            
            self.maps_widget = MapsWidget()
            # Change these values to modify map widget size
            # Current: Uses WIDGET_WIDTH x WIDGET_HEIGHT from configuration
            # Example: 1600x900 for full HD, 1920x1080 for 1080p
            self.maps_widget.setMinimumSize(QSize(WIDGET_WIDTH, WIDGET_HEIGHT))
            self.maps_widget.setMaximumSize(QSize(WIDGET_WIDTH, WIDGET_HEIGHT))
            # For flexible sizing, remove setMaximumSize and use:
            # self.maps_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            self.maps_widget.setSizePolicy(self.youtube_widget.sizePolicy())
            
            # Add maps widget to its container
            maps_container_layout.addWidget(self.maps_widget)
            
            # debug_logger.log_info("Google Maps widget sized to match YouTube widget", "MainUI")
        except Exception as e:
            # debug_logger.log_error(f"Error creating Google Maps widget: {str(e)}", "MainUI", exc_info=True)
            print(f"Error creating Google Maps widget: {str(e)}")
            self.maps_container = QFrame()
            maps_container_layout = QVBoxLayout(self.maps_container)
            maps_container_layout.setContentsMargins(20, 20, 20, 20)
            self.maps_widget = QLabel("Google Maps\nUnavailable")
            self.maps_widget.setStyleSheet("background:#000;color:#666;text-align:center;padding:50px;font-size:18px;")
            self.maps_widget.setMinimumSize(QSize(WIDGET_WIDTH, WIDGET_HEIGHT))
            self.maps_widget.setMaximumSize(QSize(WIDGET_WIDTH, WIDGET_HEIGHT))
            maps_container_layout.addWidget(self.maps_widget)
            # debug_logger.log_info("Fallback Google Maps widget created", "MainUI")

        # Add widgets to stack
        self.content_stack.addWidget(self.entertainment_menu)
        self.content_stack.addWidget(self.youtube_widget)
        self.content_stack.addWidget(self.movies_widget)
        self.content_stack.addWidget(self.music_menu)
        self.content_stack.addWidget(self.youtube_music_widget)
        self.content_stack.addWidget(self.apple_music_widget)
        self.content_stack.addWidget(self.soundcloud_widget)
        self.content_stack.addWidget(self.intellectual_games_widget)
        self.content_stack.addWidget(self.maps_container) # Changed from self.maps_widget to self.maps_container
        
        center_layout.addWidget(self.content_stack)
        # The '1' parameter gives this widget a stretch factor of 1 (takes remaining space)
        content_layout.addWidget(center_container, 1)
        
        # Minimap: use the same Google Maps widget, but smaller and repositioned
        self.minimap_container = QFrame()
        self.minimap_container.setFixedSize(MINIMAP_SIZE, MINIMAP_SIZE)
        self.minimap_container.setStyleSheet("background:#000;border:2px solid #444;border-radius:8px;")
        self.minimap_layout = QVBoxLayout(self.minimap_container)
        self.minimap_layout.setContentsMargins(2, 2, 2, 2)
        # Add the same maps_widget to the minimap container (will be reparented/moved as needed)
        # By default, show the minimap as hidden
        self.minimap_container.hide()
        speedometer_layout.addWidget(self.minimap_container)

        # Connect entertainment buttons
        self.entertainment_menu.buttons["YouTube"].clicked.connect(self.show_youtube)
        self.entertainment_menu.buttons["Movies"].clicked.connect(self.show_movies)
        self.entertainment_menu.buttons["Intellectual Games"].clicked.connect(self.show_intellectual_games)
        
        # Connect music menu buttons
        self.music_menu.buttons["YouTube Music"].clicked.connect(self.show_youtube_music)
        self.music_menu.buttons["Apple Music"].clicked.connect(self.show_apple_music)
        self.music_menu.buttons["SoundCloud"].clicked.connect(self.show_soundcloud)
        
        # Remove the redundant map widget creation and layout additions
        # The maps_widget is already created above and will be managed by show_map/show_minimap methods

        main_layout.addWidget(content_container, 1)  # Give content area stretch

        # Set main layout
        self.setLayout(main_layout)
        
        # Show minimap on boot
        self.show_minimap()
        # debug_logger.log_info("Minimap shown on boot", "MainUI")
        
        # debug_logger.log_function_exit("setup_ui", "MainUI")

    def show_youtube(self):
        self.maps_container.hide() # Changed from self.maps_widget to self.maps_container
        self.content_stack.setCurrentWidget(self.youtube_widget)

    def show_movies(self):
        self.maps_container.hide() # Changed from self.maps_widget to self.maps_container
        self.content_stack.setCurrentWidget(self.movies_widget)

    def show_intellectual_games(self):
        self.maps_container.hide() # Changed from self.maps_widget to self.maps_container
        self.content_stack.setCurrentWidget(self.intellectual_games_widget)

    def show_music_menu(self):
        self.maps_container.hide() # Changed from self.maps_widget to self.maps_container
        self.content_stack.setCurrentWidget(self.music_menu)

    def show_youtube_music(self):
        self.maps_container.hide() # Changed from self.maps_widget to self.maps_container
        self.apple_music_widget.hide()
        self.soundcloud_widget.hide()
        self.youtube_music_widget.show()
        self.content_stack.setCurrentWidget(self.youtube_music_widget)

    def show_apple_music(self):
        self.maps_container.hide() # Changed from self.maps_widget to self.maps_container
        self.youtube_music_widget.hide()
        self.soundcloud_widget.hide()
        self.apple_music_widget.show()
        self.content_stack.setCurrentWidget(self.apple_music_widget)

    def show_soundcloud(self):
        self.maps_container.hide() # Changed from self.maps_widget to self.maps_container
        self.youtube_music_widget.hide()
        self.apple_music_widget.hide()
        self.soundcloud_widget.show()
        self.content_stack.setCurrentWidget(self.soundcloud_widget)

    def handle_nav_button(self, button_name):
        self.hide_minimap()
        if button_name == "Maps":
            self.show_map()
        elif button_name == "Games":
            self.content_stack.setCurrentWidget(self.entertainment_menu)
        elif button_name == "Music":
            self.content_stack.setCurrentWidget(self.music_menu)
        elif button_name == "Home":
            self.content_stack.setCurrentWidget(self.entertainment_menu)
        # Show minimap for all screens except Maps
        if button_name != "Maps":
            self.show_minimap()

    def show_map(self):
        # Show the main Google Maps window (full size)
        self.minimap_container.hide()
        
        print(f"Setting map widget size to {WIDGET_WIDTH}x{WIDGET_HEIGHT}")
        
        # Debug: Log current sizes
        # debug_logger.log_info(f"YouTube widget size: {self.youtube_widget.size()}", "MainUI")
        # debug_logger.log_info(f"Maps container size before resize: {self.maps_container.size()}", "MainUI")
        
        # Restore the maps_widget to its container if it was moved to minimap
        if self.maps_widget.parent() != self.maps_container:
            self.maps_widget.setParent(self.maps_container)
            # Re-add to the container layout
            self.maps_container.layout().addWidget(self.maps_widget)
        
        # Resize the maps_widget to match the size set in setup_ui
        # Change WIDGET_WIDTH and WIDGET_HEIGHT at the top of this file to modify the main map size
        self.maps_widget.setMinimumSize(QSize(WIDGET_WIDTH, WIDGET_HEIGHT))
        self.maps_widget.setMaximumSize(QSize(WIDGET_WIDTH, WIDGET_HEIGHT))
        self.maps_widget.resize(QSize(WIDGET_WIDTH, WIDGET_HEIGHT))
        
        # Ensure the maps_container is properly parented and sized
        self.maps_container.setParent(self.content_stack)
        self.maps_container.setMinimumSize(QSize(WIDGET_WIDTH, WIDGET_HEIGHT))
        self.maps_container.setMaximumSize(QSize(WIDGET_WIDTH, WIDGET_HEIGHT))
        
        # Ensure the widget is properly added to the content stack
        # The widget should already be in the stack from setup_ui, but let's make sure
        if self.maps_container not in [self.content_stack.widget(i) for i in range(self.content_stack.count())]:
            self.content_stack.addWidget(self.maps_container)
        
        # Make sure it's the current widget in the stack
        self.content_stack.setCurrentWidget(self.maps_container)
        self.maps_container.show()
        
        # Force update
        self.maps_container.update()
        self.content_stack.update()
        
        print(f"Map widget actual size: {self.maps_widget.size()}")
        print(f"Map container actual size: {self.maps_container.size()}")
        
        # Debug: Log final sizes
        # debug_logger.log_info(f"Maps container size after resize: {self.maps_container.size()}", "MainUI")
        # debug_logger.log_info(f"Content stack size: {self.content_stack.size()}", "MainUI")
        
        # debug_logger.log_info("Main Google Maps window shown (full size)", "MainUI")

    def show_minimap(self):
        # Show the minimap (same Google Maps widget, but smaller and repositioned)
        # Remove the maps_widget from its container for minimap use
        self.maps_widget.setParent(self.minimap_container)
        # Set minimap size using configuration
        self.maps_widget.setMinimumSize(QSize(MINIMAP_SIZE, MINIMAP_SIZE))
        self.maps_widget.setMaximumSize(QSize(MINIMAP_SIZE, MINIMAP_SIZE))
        self.maps_widget.resize(QSize(MINIMAP_SIZE, MINIMAP_SIZE))
        self.minimap_layout.addWidget(self.maps_widget)
        self.minimap_container.show()
        self.maps_widget.show()
        # debug_logger.log_info("Minimap shown (Google Maps widget resized and moved)", "MainUI")

    def hide_minimap(self):
        self.minimap_container.hide()
        # debug_logger.log_info("Minimap hidden", "MainUI")

class CarInterface(QMainWindow):
    def __init__(self):
        # debug_logger.log_function_entry("__init__", "CarInterface")
        super().__init__()
        self.setWindowTitle("Puddle")
        self.setStyleSheet("background-color: #000000;")
        self.showFullScreen()
        # debug_logger.log_function_exit("__init__", "CarInterface")

        # Create stacked widget to hold boot animation and main screen
        # debug_logger.log_info("Creating stacked widget", "CarInterface")
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        # Create boot animation
        # debug_logger.log_info("Creating boot animation", "CarInterface")
        self.boot_animation = BootAnimation(self)
        self.stacked_widget.addWidget(self.boot_animation)
        
        # Connect boot animation complete signal
        self.boot_animation.boot_complete.connect(self.show_main_ui)

        # Create and add main screen (initially hidden)
        # debug_logger.log_info("Creating main screen", "CarInterface")
        try:
            self.main_screen = MainUI(self)
            self.stacked_widget.addWidget(self.main_screen)
            self.main_screen.hide()  # Hide initially, will show after boot
            # debug_logger.log_info("Main screen created and added to stacked widget", "CarInterface")
        except Exception as e:
            # debug_logger.log_error(f"Error creating main screen: {str(e)}", "CarInterface", exc_info=True)
            print(f"Error creating main screen: {str(e)}")
            self.main_screen = QLabel("Main Screen\nUnavailable")
            self.main_screen.setStyleSheet("background:#000;color:#fff;text-align:center;padding:50px;font-size:24px;")
            self.stacked_widget.addWidget(self.main_screen)
            self.main_screen.hide()  # Hide initially
            # debug_logger.log_info("Fallback main screen created", "CarInterface")

        # Show boot animation first
        self.stacked_widget.setCurrentWidget(self.boot_animation)
        # debug_logger.log_info("Boot animation shown first", "CarInterface")
        
        # Start the boot sequence
        self.boot_animation.start_boot_sequence()

    def show_main_ui(self):
        """Show the main UI after boot animation is complete"""
        # debug_logger.log_info("Showing main UI after boot", "CarInterface")
        self.main_screen.show()
        self.stacked_widget.setCurrentWidget(self.main_screen)
        # debug_logger.log_info("Main UI shown after boot", "CarInterface")

    def keyPressEvent(self, event):
        if isinstance(event, QKeyEvent) and event.key() == Qt.Key_F11:
            if self.isFullScreen():
                self.showNormal()
                # debug_logger.log_info("F11 pressed: Exiting fullscreen", "CarInterface")
            else:
                self.showFullScreen()
                # debug_logger.log_info("F11 pressed: Entering fullscreen", "CarInterface")
        else:
            super().keyPressEvent(event)

if __name__ == "__main__":
    # debug_logger.log_info("Starting Puddle application", "main")
    app = QApplication(sys.argv)

    # Check for command line arguments
    skip_boot = "--skip-boot" in sys.argv

    # Load custom fonts
    # debug_logger.log_info("Loading custom fonts", "main")
    font_dir = "Fonts"
    try:
        if os.path.exists(font_dir):
            for font_file in os.listdir(font_dir):
                if font_file.endswith(".ttf"):
                    font_path = os.path.join(font_dir, font_file)
                    # debug_logger.log_debug(f"Loading font: {font_path}", "main")
                    QFontDatabase.addApplicationFont(font_path)
            # debug_logger.log_info("Fonts loaded successfully", "main")
        else:
            # debug_logger.log_warning(f"Font directory not found: {font_dir}", "main")
            pass
    except Exception as e:
        # debug_logger.log_error(f"Error loading fonts: {str(e)}", "main", exc_info=True)
        pass

    # Create and show main interface
    # debug_logger.log_info("Creating main interface", "main")
    try:
        interface = CarInterface()
        
        # If skip_boot is True, show main UI immediately
        if skip_boot:
            print("Skipping boot animation...")
            interface.show_main_ui()
        
        # debug_logger.log_info("Showing main interface", "main")
        interface.show()
        # debug_logger.log_info("Application started successfully", "main")
    except Exception as e:
        # debug_logger.log_error(f"Error creating/showing interface: {str(e)}", "main", exc_info=True)
        raise

    sys.exit(app.exec()) 
