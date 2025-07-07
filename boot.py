import sys
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, pyqtSignal, QRect
from PyQt5.QtGui import QFont, QFontDatabase
from PyQt5.QtSvg import QSvgWidget

class BootSequence(QWidget):
    boot_complete = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.fade_to_main_ui)
        
    def setup_ui(self):
        # Set up the boot screen layout
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create MALLARD label
        self.mallard_label = QLabel("MALLARD")
        # Use style sheet to center the text
        self.mallard_label.setStyleSheet("""
            QLabel {
                font-size: 72px;
                font-weight: bold;
                color: #007acc;
                background-color: transparent;
                text-shadow: 3px 3px 6px rgba(0,0,0,0.7);
                text-align: center;
                qproperty-alignment: AlignCenter;
            }
        """)
        
        # Set opacity to 0 initially
        self.setWindowOpacity(0.0)
        
        layout.addWidget(self.mallard_label)
        self.setLayout(layout)
        
        # Set background
        self.setStyleSheet("""
            QWidget {
                background-color: #000000;
            }
        """)
    
    def start_boot_sequence(self):
        """Start the boot animation sequence with zoom and fade effects"""
        # Set initial opacity and scale
        self.setWindowOpacity(0.0)
        
        # Create zoom in animation using font size
        self.zoom_animation = QPropertyAnimation(self.mallard_label, b"font")
        self.zoom_animation.setDuration(2000)  # 2 seconds
        
        # Import QFont for font animation
        from PyQt5.QtGui import QFont
        
        # Create font objects for animation
        small_font = QFont("Arial", 24)  # Start small
        large_font = QFont("Arial", 72)  # End large
        
        self.zoom_animation.setStartValue(small_font)
        self.zoom_animation.setEndValue(large_font)
        self.zoom_animation.setEasingCurve(QEasingCurve.OutQuad)
        
        # Fade in animation
        self.fade_in_animation = QPropertyAnimation(self, b"windowOpacity")
        self.fade_in_animation.setDuration(1500)  # 1.5 seconds
        self.fade_in_animation.setStartValue(0.0)
        self.fade_in_animation.setEndValue(1.0)
        self.fade_in_animation.setEasingCurve(QEasingCurve.InOutQuad)
        
        # Connect animations
        self.fade_in_animation.finished.connect(self.start_fade_out)
        
        # Start both animations
        self.fade_in_animation.start()
        self.zoom_animation.start()
    
    def start_fade_out(self):
        """Start the fade out animation after a delay"""
        # Wait for 2 seconds before starting fade out
        QTimer.singleShot(2000, self.fade_out_mallard)
    
    def fade_out_mallard(self):
        """Smoothly fade out the MALLARD text"""
        self.fade_out_animation = QPropertyAnimation(self, b"windowOpacity")
        self.fade_out_animation.setDuration(1500)  # 1.5 seconds for smoother fade
        self.fade_out_animation.setStartValue(1.0)
        self.fade_out_animation.setEndValue(0.0)
        self.fade_out_animation.setEasingCurve(QEasingCurve.InOutQuad)
        
        # Connect fade out completion to main UI transition
        self.fade_out_animation.finished.connect(self.complete_boot_sequence)
        
        # Start the fade out
        self.fade_out_animation.start()
    
    def complete_boot_sequence(self):
        """Complete the boot sequence and signal main UI to show"""
        self.boot_complete.emit()
    
    def fade_to_main_ui(self):
        """Fade transition to main UI"""
        self.boot_complete.emit() 