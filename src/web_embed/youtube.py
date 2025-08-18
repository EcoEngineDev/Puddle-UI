from PyQt5.QtWidgets import QWidget, QVBoxLayout, QFrame
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage, QWebEngineSettings, QWebEngineProfile
from PyQt5.QtCore import QUrl, QSize, Qt
from src.keyboard import VirtualKeyboard
from src.web_embed.web_view import WebAppWidget
from src.web_embed.adblock import enable_adblock


class YouTubePage(QWebEnginePage):
    def __init__(self, profile, parent=None):
        super().__init__(profile, parent)
        s = self.settings()
        s.setAttribute(QWebEngineSettings.JavascriptEnabled, True)
        s.setAttribute(QWebEngineSettings.ScrollAnimatorEnabled, True)
        s.setAttribute(QWebEngineSettings.PluginsEnabled, True)
        s.setAttribute(QWebEngineSettings.FullScreenSupportEnabled, True)
        # Disable WebGL to avoid GPU-related black/dim overlays on some drivers
        s.setAttribute(QWebEngineSettings.WebGLEnabled, False)

    def javaScriptConsoleMessage(self, level, message, lineNumber, sourceID):
        msg = str(message)
        if ('TrustedScript' in msg or
            'preloaded using link preload but not used' in msg or
            'generate_204' in msg):
            return
        return super().javaScriptConsoleMessage(level, message, lineNumber, sourceID)


class YouTubeWidget(WebAppWidget):
    def __init__(self, parent=None):
        super().__init__("https://www.youtube.com", parent)
        # Use a dedicated profile with Safari UA to prefer H.264 over VP9/AV1
        profile = self.web_view.page().profile()
        try:
            profile.setHttpUserAgent(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.4 Safari/605.1.15"
            )
        except Exception:
            pass
        # Swap in custom page with adjusted settings
        self.page = YouTubePage(profile, self.web_view)
        self.web_view.setPage(self.page)
        # Enable original adblock injection for YouTube
        enable_adblock(self.web_view, target="youtube")
        
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
