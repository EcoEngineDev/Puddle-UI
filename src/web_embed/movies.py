from PyQt5.QtWidgets import QWidget, QVBoxLayout, QFrame
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage, QWebEngineProfile, QWebEngineSettings
from PyQt5.QtCore import QUrl, QSize, Qt
from src.keyboard import VirtualKeyboard
# from src.debug_logger import debug_logger
from src.web_embed.web_view import WebAppWidget
from src.widget_config import WIDGET_WIDTH, WIDGET_HEIGHT

class MoviesPage(QWebEnginePage):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Enable all settings that might help bypass restrictions
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

    def acceptNavigationRequest(self, url, _type, isMainFrame):
        # Inject anti-frame-busting code
        if isMainFrame:
            script = """
                // Override properties that could detect framing
                try {
                    Object.defineProperty(window, 'self', {
                        get: function() { return window.top; }
                    });
                    Object.defineProperty(window, 'top', {
                        get: function() { return window.self; }
                    });
                    Object.defineProperty(window, 'parent', {
                        get: function() { return window.self; }
                    });
                    Object.defineProperty(window, 'frameElement', {
                        get: function() { return null; }
                    });
                } catch(e) {}
            """
            self.runJavaScript(script)
        return super().acceptNavigationRequest(url, _type, isMainFrame)

    def javaScriptConsoleMessage(self, level, message, lineNumber, sourceID):
        msg = str(message)
        noisy = (
            'preloaded using link preload but not used' in msg or
            'blocked by CORS policy' in msg or
            'generate_204' in msg
        )
        if noisy:
            return
        # Uncomment for debugging
        # print(f"Console: {message} at line {lineNumber} in {sourceID}")
        return super().javaScriptConsoleMessage(level, message, lineNumber, sourceID)

class MoviesWidget(WebAppWidget):
    def __init__(self, parent=None):
        # debug_logger.log_function_entry("__init__", "MoviesWidget", parent=parent)
        super().__init__("https://rivestream.org", parent)
        # debug_logger.log_info("Creating movie web engine profile", "MoviesWidget")
        # debug_logger.log_function_exit("__init__", "MoviesWidget")

    def setup_ui(self):
        # debug_logger.log_function_entry("setup_ui", "MoviesWidget")
        # Main layout
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(0)
        
        # Container for web view
        web_container = QFrame()
        self._web_container = web_container
        web_layout = QVBoxLayout(web_container)
        web_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create web view for Movies with touch-optimized page
        # debug_logger.log_info("Creating movie web view", "MoviesWidget")
        self.web_view = QWebEngineView()
        self.page = MoviesPage(self.web_view)
        self.web_view.setPage(self.page)
        # debug_logger.log_info("Loading movie website: https://rivestream.org", "MoviesWidget")
        self.web_view.setUrl(QUrl(self.url))
        # Uses WIDGET_WIDTH x WIDGET_HEIGHT from configuration for consistent sizing
        self.web_view.setMinimumSize(QSize(WIDGET_WIDTH, WIDGET_HEIGHT))
        web_layout.addWidget(self.web_view)
        
        # Add virtual keyboard
        self.keyboard = VirtualKeyboard(self)
        self.keyboard.hide()  # Hidden by default
        
        # Connect keyboard events to web view
        self.keyboard.key_pressed.connect(self.handle_key_press)
        
        # Add web container to main layout
        layout.addWidget(web_container)
        self.setLayout(layout)
        # debug_logger.log_function_exit("setup_ui", "MoviesWidget")
        
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
