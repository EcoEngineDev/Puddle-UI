import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QGridLayout, QPushButton, QLabel, 
                             QStackedWidget, QFrame, QButtonGroup, QSizePolicy)
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, pyqtSignal
from PyQt5.QtGui import QFont, QIcon, QPixmap, QPainter, QColor, QFontDatabase
from PyQt5.QtSvg import QSvgWidget, QSvgRenderer
from boot import BootSequence

class ThemeManager:
    def __init__(self):
        self.current_theme = "dark"
        self.themes = {
            "dark": {
                "bg_color": "#000000",
                "secondary_bg": "#2d2d2d", 
                "text_color": "#cccccc",
                "accent_color": "#007acc",
                "button_bg": "#3d3d3d",
                "button_hover": "#4d4d4d",
                "icon_color": "#cccccc"
            },
            "light": {
                "bg_color": "#f5f5f5",
                "secondary_bg": "#e0e0e0",
                "text_color": "#000000", 
                "accent_color": "#0066cc",
                "button_bg": "#ffffff",
                "button_hover": "#e8e8e8",
                "icon_color": "#000000"
            }
        }
    
    def get_theme(self):
        return self.themes[self.current_theme]
    
    def toggle_theme(self):
        self.current_theme = "light" if self.current_theme == "dark" else "dark"
        return self.get_theme()

class SvgButton(QPushButton):
    def __init__(self, svg_path, text="", parent=None):
        super().__init__(text, parent)
        self.svg_path = svg_path
        self.setup_button()
    
    def setup_button(self):
        self.setMinimumSize(120, 120)
        self.setMaximumSize(150, 150)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setStyleSheet("""
            QPushButton {
                border: 2px solid #3d3d3d;
                border-radius: 15px;
                background-color: #2d2d2d;
                color: #cccccc;
                font-size: 14px;
                font-weight: bold;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #4d4d4d;
                border-color: #007acc;
            }
            QPushButton:pressed {
                background-color: #000000;
            }
        """)
        
        # Load SVG as icon
        if os.path.exists(self.svg_path):
            icon = QIcon(self.svg_path)
            self.setIcon(icon)
            self.setIconSize(self.size() * 0.6)

class CloseButton(QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(30, 30)
        self.setStyleSheet("""
            QPushButton {
                background-color: #cc0000;
                border: none;
                border-radius: 15px;
            }
            QPushButton:hover {
                background-color: #ff0000;
            }
            QPushButton:pressed {
                background-color: #990000;
            }
        """)
        
class SettingsWidget(QWidget):
    def __init__(self, theme_manager, car_interface, parent=None):
        super().__init__(parent)
        self.theme_manager = theme_manager
        self.car_interface = car_interface
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("SETTINGS")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #cccccc; margin: 20px; qproperty-alignment: AlignCenter;")
        layout.addWidget(title)
        
        # Theme toggle
        theme_frame = QFrame()
        theme_frame.setStyleSheet("""
            QFrame {
                background-color: #2d2d2d;
                border-radius: 10px;
                padding: 10px;
                margin: 10px;
            }
        """)
        theme_layout = QHBoxLayout(theme_frame)
        
        theme_label = QLabel("Theme:")
        theme_label.setStyleSheet("color: #cccccc; font-size: 16px;")
        theme_layout.addWidget(theme_label)
        
        self.theme_button = QPushButton("Dark Mode")
        self.theme_button.setStyleSheet("""
            QPushButton {
                background-color: #007acc;
                color: #cccccc;
                border: none;
                padding: 8px 16px;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #0088dd;
            }
        """)
        self.theme_button.clicked.connect(self.toggle_theme)
        theme_layout.addWidget(self.theme_button)
        
        layout.addWidget(theme_frame)
        
        # Back button
        back_button = QPushButton("BACK")
        back_button.setStyleSheet("""
            QPushButton {
                background-color: #3d3d3d;
                color: #cccccc;
                border: 2px solid #007acc;
                padding: 12px 24px;
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
                margin: 20px;
            }
            QPushButton:hover {
                background-color: #4d4d4d;
            }
        """)
        back_button.clicked.connect(self.car_interface.show_main_ui)
        layout.addWidget(back_button)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def toggle_theme(self):
        new_theme = self.theme_manager.toggle_theme()
        self.theme_button.setText("Light Mode" if self.theme_manager.current_theme == "dark" else "Dark Mode")
        self.car_interface.apply_theme(new_theme)

class MainUI(QWidget):
    def __init__(self, theme_manager, car_interface, parent=None):
        super().__init__(parent)
        self.theme_manager = theme_manager
        self.car_interface = car_interface
        self.setup_ui()
    
    def setup_ui(self):
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setSpacing(30)
        main_layout.setContentsMargins(40, 40, 40, 40)
        
        # Title
        title = QLabel("MALLARD")
        title.setStyleSheet("""
            font-size: 48px; 
            font-weight: bold; 
            color: #007acc; 
            margin: 20px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
            qproperty-alignment: AlignCenter;
        """)
        main_layout.addWidget(title)
        
        # Button grid
        button_grid = QGridLayout()
        button_grid.setSpacing(20)
        
        # Create buttons with icons
        buttons = [
            ("Music", "Media/Icons/music-circle-svgrepo-com.svg"),
            ("Map", "Media/Icons/map-svgrepo-com.svg"),
            ("Audio", "Media/Icons/audio-square-svgrepo-com.svg"),
            ("Settings", "Media/Icons/setting-2-svgrepo-com.svg"),
            ("Volume", "Media/Icons/volume-high-svgrepo-com.svg"),
            ("More", "Media/Icons/more-circle-svgrepo-com.svg")
        ]
        
        for i, (text, icon_path) in enumerate(buttons):
            button = SvgButton(icon_path, text)
            if text == "Settings":
                button.clicked.connect(self.car_interface.show_settings)
            else:
                button.clicked.connect(lambda checked, t=text: self.button_clicked(t))
            
            row = i // 3
            col = i % 3
            button_grid.addWidget(button, row, col)
        
        main_layout.addLayout(button_grid)
        main_layout.addStretch()
        
        self.setLayout(main_layout)
    
    def button_clicked(self, button_name):
        print(f"{button_name} button clicked!")  # Placeholder functionality

class CarInterface(QMainWindow):
    def __init__(self):
        super().__init__()
        self.theme_manager = ThemeManager()
        self.setup_ui()
        self.setup_boot_sequence()
    
    def setup_ui(self):
        # Main window setup
        self.setWindowTitle("MALLARD Car Interface")
        self.setWindowFlags(Qt.FramelessWindowHint)
        
        # Central widget with stacked layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Stacked widget for different screens
        self.stacked_widget = QStackedWidget()
        
        # Boot sequence screen
        self.boot_screen = BootSequence()
        self.stacked_widget.addWidget(self.boot_screen)
        
        # Main UI screen
        self.main_screen = MainUI(self.theme_manager, self, self)
        self.stacked_widget.addWidget(self.main_screen)
        
        # Settings screen
        self.settings_screen = SettingsWidget(self.theme_manager, self, self)
        self.stacked_widget.addWidget(self.settings_screen)
        
        main_layout.addWidget(self.stacked_widget)
        
        # Close button overlay - create before showFullScreen()
        self.close_button = CloseButton(self)
        self.close_button.clicked.connect(self.close)
        
        # Apply initial theme
        self.apply_theme(self.theme_manager.get_theme())
        
        # Show fullscreen after all UI elements are created
        self.showFullScreen()
    
    def setup_boot_sequence(self):
        # Connect boot sequence completion to main UI
        self.boot_screen.boot_complete.connect(self.show_main_ui)
        # Start with boot screen
        self.stacked_widget.setCurrentWidget(self.boot_screen)
        self.boot_screen.start_boot_sequence()
    
    def show_main_ui(self):
        self.stacked_widget.setCurrentWidget(self.main_screen)
    
    def show_settings(self):
        self.stacked_widget.setCurrentWidget(self.settings_screen)
    
    def apply_theme(self, theme):
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {theme['bg_color']};
            }}
            QWidget {{
                background-color: {theme['bg_color']};
                color: {theme['text_color']};
            }}
        """)
    
    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Position close button in bottom right corner
        if hasattr(self, 'close_button'):
            self.close_button.move(self.width() - 40, self.height() - 40)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Load custom font if available
    font_path = "Fonts/Lexend-Regular.ttf"
    if os.path.exists(font_path):
        font_id = QFontDatabase.addApplicationFont(font_path)
        if font_id != -1:
            font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
            app.setFont(QFont(font_family, 12))
    
    interface = CarInterface()
    interface.show()
    
    sys.exit(app.exec_()) 