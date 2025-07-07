from PyQt5.QtWidgets import QWidget, QVBoxLayout, QGraphicsView, QGraphicsScene, QGraphicsOpacityEffect
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, pyqtSignal, QParallelAnimationGroup, QUrl
from PyQt5.QtSvg import QGraphicsSvgItem
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
import os

class BootSequence(QWidget):
    boot_complete = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.setup_audio()

    def setup_audio(self):
        self.player = QMediaPlayer()
        sound_path = os.path.join("Media", "SFX", "boot.wav")
        url = QUrl.fromLocalFile(os.path.abspath(sound_path))
        self.player.setMedia(QMediaContent(url))
        self.player.setVolume(100)

    def setup_ui(self):
        self.setStyleSheet("background-color: #000;")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignCenter)

        # Graphics scene/view for SVG
        self.scene = QGraphicsScene(self)
        self.view = QGraphicsView(self.scene, self)
        self.view.setStyleSheet("background: transparent; border: none;")
        self.view.setAlignment(Qt.AlignCenter)
        self.view.setFixedSize(1600, 600)  # Adjust as needed
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # SVG item
        svg_path = os.path.join("Media", "mallard.svg")
        self.svg_item = QGraphicsSvgItem(svg_path)
        self.svg_item.setFlags(self.svg_item.ItemClipsToShape)
        self.svg_item.setCacheMode(self.svg_item.NoCache)
        self.svg_item.setZValue(0)
        
        # Center the SVG in the view
        self.svg_item.setTransformOriginPoint(self.svg_item.boundingRect().center())
        self.svg_item.setScale(4.0)
        self.scene.addItem(self.svg_item)
        
        # Center the scene on the SVG
        self.scene.setSceneRect(self.svg_item.boundingRect())
        self.view.centerOn(self.svg_item.boundingRect().center())

        # Opacity effect for fade in/out
        self.opacity_effect = QGraphicsOpacityEffect()
        self.view.setGraphicsEffect(self.opacity_effect)
        self.opacity_effect.setOpacity(0.0)

        layout.addWidget(self.view)

    def start_boot_sequence(self):
        # Play boot sound
        self.player.play()

        # Create parallel animation group for fade-in and zoom
        self.parallel_group = QParallelAnimationGroup()

        # 1. Fade in animation (700ms)
        self.fade_in = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_in.setDuration(700)
        self.fade_in.setStartValue(0.0)
        self.fade_in.setEndValue(1.0)
        self.fade_in.setEasingCurve(QEasingCurve.InOutQuad)

        # 2. Zoom animation (2500ms - covers both fade-in and continued zoom)
        self.zoom_anim = QPropertyAnimation(self.svg_item, b"scale")
        self.zoom_anim.setDuration(2500)
        self.zoom_anim.setStartValue(4.0)
        self.zoom_anim.setEndValue(4.8)
        self.zoom_anim.setEasingCurve(QEasingCurve.OutCubic)

        # Add both animations to parallel group
        self.parallel_group.addAnimation(self.fade_in)
        self.parallel_group.addAnimation(self.zoom_anim)
        
        # Connect to start fade out after parallel animations complete
        self.parallel_group.finished.connect(self.start_fade_out)
        self.parallel_group.start()

    def start_fade_out(self):
        # 3. Fade out
        self.fade_out = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_out.setDuration(900)
        self.fade_out.setStartValue(1.0)
        self.fade_out.setEndValue(0.0)
        self.fade_out.setEasingCurve(QEasingCurve.InOutQuad)
        self.fade_out.finished.connect(self.complete_boot_sequence)
        self.fade_out.start()

    def complete_boot_sequence(self):
        self.boot_complete.emit()