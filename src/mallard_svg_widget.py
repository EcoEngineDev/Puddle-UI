from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtSvg import QSvgWidget
from PyQt5.QtGui import QPixmap
import os

class MallardSVGWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Create SVG widget
        self.svg_widget = QSvgWidget()
        self.svg_widget.setFixedSize(305, 35)  # Match the SVG viewBox dimensions
        
        # Load the MALLARD SVG
        svg_path = os.path.join("Media", "MALLARD.svg")
        if os.path.exists(svg_path):
            self.svg_widget.load(svg_path)
        else:
            # Fallback to text if SVG not found
            self.svg_widget = QLabel("M A L L A R D")
            self.svg_widget.setStyleSheet("""
                QLabel {
                    color: #FFFFFF;
                    font-family: 'Lexend Bold';
                    font-size: 32px;
                    background-color: transparent;
                }
            """)
            self.svg_widget.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(self.svg_widget)
        
        # Set transparent background
        self.setStyleSheet("background-color: transparent;") 