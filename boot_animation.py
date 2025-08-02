from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt5.QtCore import QTimer, QPropertyAnimation, QEasingCurve, pyqtProperty, Qt, QUrl, pyqtSignal
from PyQt5.QtGui import QPixmap, QPainter, QColor, QFont
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
import os

class BootAnimation(QWidget):
    # Signal emitted when boot animation is complete
    boot_complete = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.setup_audio()
        
    def setup_ui(self):
        # Set up the widget to cover the entire screen
        self.setStyleSheet("background-color: #000000;")
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Create label for the boot image
        self.boot_label = QLabel()
        self.boot_label.setAlignment(Qt.AlignCenter)
        self.boot_label.setStyleSheet("background-color: transparent;")
        
        # Load the boot image
        boot_image_path = os.path.join("Media", "boot.png")
        if os.path.exists(boot_image_path):
            pixmap = QPixmap(boot_image_path)
            # Scale the image to fit the screen while maintaining aspect ratio
            scaled_pixmap = pixmap.scaled(
                self.size(), 
                Qt.KeepAspectRatio, 
                Qt.SmoothTransformation
            )
            self.boot_label.setPixmap(scaled_pixmap)
        else:
            # Fallback if image not found
            self.boot_label.setText("MALLARD MOTORSPORTS")
            self.boot_label.setStyleSheet("""
                QLabel {
                    color: #00FFA3;
                    font-family: 'Lexend Bold';
                    font-size: 48px;
                    background-color: transparent;
                }
            """)
        
        layout.addWidget(self.boot_label)
        
        # Set up opacity for fade animation
        self._opacity = 1.0
        
    def setup_audio(self):
        # Set up audio player for boot sound
        self.audio_player = QMediaPlayer()
        boot_sound_path = os.path.join("Media", "SFX", "boot.wav")
        if os.path.exists(boot_sound_path):
            self.audio_player.setMedia(QMediaContent(QUrl.fromLocalFile(boot_sound_path)))
            self.audio_player.setVolume(50)  # Set volume to 50%
        
    def start_boot_sequence(self):
        """Start the boot animation sequence"""
        print("Starting boot animation sequence...")
        
        # Set initial opacity to 0 for fade-in
        self._opacity = 0.0
        self.update()
        
        # Play boot sound
        if self.audio_player.mediaStatus() != QMediaPlayer.NoMedia:
            self.audio_player.play()
            print("Playing boot sound...")
        
        # Show the boot screen
        self.show()
        self.raise_()
        
        # Start fade in animation immediately
        self.start_fade_in()
        
    def start_fade_in(self):
        """Start the fade in animation"""
        print("Starting fade in animation...")
        
        # Create fade in animation
        self.fade_in_animation = QPropertyAnimation(self, b"opacity")
        self.fade_in_animation.setDuration(1000)  # 1 second
        self.fade_in_animation.setStartValue(0.0)
        self.fade_in_animation.setEndValue(1.0)
        self.fade_in_animation.setEasingCurve(QEasingCurve.OutCubic)
        
        # Connect animation finished signal
        self.fade_in_animation.finished.connect(self.on_fade_in_complete)
        
        # Start the animation
        self.fade_in_animation.start()
        
    def on_fade_in_complete(self):
        """Called when fade in animation is complete"""
        print("Fade in complete, waiting before fade out...")
        # Wait 2 seconds before starting fade out
        QTimer.singleShot(2000, self.start_fade_out)
        
    def start_fade_out(self):
        """Start the fade out animation"""
        print("Starting fade out animation...")
        
        # Create fade out animation
        self.fade_animation = QPropertyAnimation(self, b"opacity")
        self.fade_animation.setDuration(1500)  # 1.5 seconds
        self.fade_animation.setStartValue(1.0)
        self.fade_animation.setEndValue(0.0)
        self.fade_animation.setEasingCurve(QEasingCurve.OutCubic)
        
        # Connect animation finished signal
        self.fade_animation.finished.connect(self.on_fade_complete)
        
        # Start the animation
        self.fade_animation.start()
        
    def on_fade_complete(self):
        """Called when fade out animation is complete"""
        print("Boot animation complete")
        self.hide()
        
        # Emit signal to show main UI
        self.boot_complete.emit()
    
    def get_opacity(self):
        """Get current opacity for animation"""
        return self._opacity
        
    def set_opacity(self, opacity):
        """Set opacity for animation"""
        self._opacity = opacity
        self.update()
        
    # Property for opacity animation
    opacity = pyqtProperty(float, get_opacity, set_opacity)
    
    def paintEvent(self, event):
        """Custom paint event to handle opacity"""
        painter = QPainter(self)
        painter.setOpacity(self._opacity)
        
        # Draw background
        painter.fillRect(self.rect(), QColor(0, 0, 0))
        
        # Draw the boot image with opacity
        if hasattr(self.boot_label, 'pixmap') and self.boot_label.pixmap():
            pixmap = self.boot_label.pixmap()
            # Center the image
            x = (self.width() - pixmap.width()) // 2
            y = (self.height() - pixmap.height()) // 2
            painter.drawPixmap(x, y, pixmap)
        else:
            # Draw fallback text
            painter.setPen(QColor(0, 255, 163))  # #00FFA3
            font = QFont("Lexend Bold", 48)
            painter.setFont(font)
            
            text = "MALLARD MOTORSPORTS"
            text_rect = painter.fontMetrics().boundingRect(text)
            x = (self.width() - text_rect.width()) // 2
            y = (self.height() + text_rect.height()) // 2
            painter.drawText(x, y, text)
    
    def resizeEvent(self, event):
        """Handle resize events to scale the boot image"""
        super().resizeEvent(event)
        
        # Re-scale the boot image if it exists
        boot_image_path = os.path.join("Media", "boot.png")
        if os.path.exists(boot_image_path):
            pixmap = QPixmap(boot_image_path)
            scaled_pixmap = pixmap.scaled(
                self.size(), 
                Qt.KeepAspectRatio, 
                Qt.SmoothTransformation
            )
            self.boot_label.setPixmap(scaled_pixmap) 