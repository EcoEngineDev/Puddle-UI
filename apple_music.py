from PyQt5.QtWidgets import QWidget, QVBoxLayout, QFrame
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage, QWebEngineSettings, QWebEngineProfile
from PyQt5.QtCore import QUrl, QSize, Qt
from keyboard import VirtualKeyboard

class AppleMusicPage(QWebEnginePage):
    def __init__(self, profile, parent=None):
        super().__init__(profile, parent)
        
        # Enable all settings for music playback
        settings = self.settings()
        settings.setAttribute(QWebEngineSettings.JavascriptEnabled, True)
        settings.setAttribute(QWebEngineSettings.ScrollAnimatorEnabled, True)
        settings.setAttribute(QWebEngineSettings.PluginsEnabled, True)
        settings.setAttribute(QWebEngineSettings.FullScreenSupportEnabled, True)
        settings.setAttribute(QWebEngineSettings.LocalStorageEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebGLEnabled, True)
        settings.setAttribute(QWebEngineSettings.DnsPrefetchEnabled, True)
        settings.setAttribute(QWebEngineSettings.JavascriptCanOpenWindows, True)
        settings.setAttribute(QWebEngineSettings.JavascriptCanAccessClipboard, True)
        
        # Set touch-optimized defaults
        settings.setFontSize(QWebEngineSettings.DefaultFontSize, 16)
        settings.setFontSize(QWebEngineSettings.MinimumFontSize, 14)

class AppleMusicWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        # Create custom profile with modified settings
        self.profile = QWebEngineProfile("applemusic_profile")
        self.profile.setHttpUserAgent("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        self.setup_ui()
        self.hide()  # Hidden by default

    def setup_ui(self):
        # Main layout
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(0)
        
        # Container for web view
        web_container = QFrame()
        web_layout = QVBoxLayout(web_container)
        web_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create web view for Apple Music
        self.web_view = QWebEngineView()
        self.page = AppleMusicPage(self.profile, self.web_view)
        self.web_view.setPage(self.page)
        self.web_view.setUrl(QUrl("https://music.apple.com"))
        self.web_view.setMinimumSize(QSize(1280, 768))
        web_layout.addWidget(self.web_view)
        
        # Add virtual keyboard
        self.keyboard = VirtualKeyboard(self)
        self.keyboard.hide()  # Hidden by default
        
        # Connect keyboard events to web view
        self.keyboard.key_pressed.connect(self.handle_key_press)
        
        # Add web container to main layout
        layout.addWidget(web_container)
        self.setLayout(layout)
        
        # Handle focus changes to show/hide keyboard
        self.web_view.focusProxy().installEventFilter(self)
        
    def handle_key_press(self, key):
        # Handle special keys
        if key == '\b':
            # Simulate backspace
            self.web_view.page().runJavaScript(
                "document.activeElement.value = document.activeElement.value.slice(0, -1);"
            )
        elif key == '\n':
            # Simulate enter
            self.web_view.page().runJavaScript(
                "document.activeElement.form && document.activeElement.form.submit();"
            )
        else:
            # Insert regular text
            self.web_view.page().runJavaScript(
                f"document.activeElement.value += '{key}';"
            )
    
    def eventFilter(self, obj, event):
        if event.type() == event.FocusIn:
            # Show keyboard when a text input is focused
            self.web_view.page().runJavaScript(
                "document.activeElement.tagName === 'INPUT' || document.activeElement.tagName === 'TEXTAREA'",
                lambda result: self.keyboard.setVisible(result)
            )
        return super().eventFilter(obj, event)
        
    def showEvent(self, event):
        super().showEvent(event)
        # Ensure keyboard is properly positioned when widget is shown
        if self.keyboard.isVisible():
            self.keyboard.move(0, self.height() - self.keyboard.height())

    def closeEvent(self, event):
        # Properly cleanup web engine resources
        if self.web_view:
            self.web_view.setPage(None)
            self.web_view.deleteLater()
        if hasattr(self, 'page'):
            self.page.deleteLater()
        super().closeEvent(event) 