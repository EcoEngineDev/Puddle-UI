from PyQt5.QtWidgets import QWidget, QVBoxLayout, QFrame
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage, QWebEngineSettings
from PyQt5.QtCore import QUrl, QSize, Qt
from keyboard import VirtualKeyboard

class DarkModePage(QWebEnginePage):
    def __init__(self, parent=None):
        super().__init__(parent)
        # Enable touch-friendly settings
        settings = self.settings()
        settings.setAttribute(QWebEngineSettings.JavascriptEnabled, True)
        settings.setAttribute(QWebEngineSettings.ScrollAnimatorEnabled, True)
        settings.setAttribute(QWebEngineSettings.PluginsEnabled, True)
        settings.setAttribute(QWebEngineSettings.FullScreenSupportEnabled, True)
        # Set touch-optimized defaults
        settings.setFontSize(QWebEngineSettings.DefaultFontSize, 16)
        settings.setFontSize(QWebEngineSettings.MinimumFontSize, 14)

    def acceptNavigationRequest(self, url, _type, isMainFrame):
        if isMainFrame:
            # Inject dark mode CSS when page loads
            self.runJavaScript("""
                (function() {
                    const style = document.createElement('style');
                    style.textContent = `
                        html { background: #1a1a1a !important; }
                        body { background: #1a1a1a !important; color: #ffffff !important; }
                        * { color: #ffffff !important; background-color: #1a1a1a !important; }
                        a { color: #00FFA3 !important; }
                        input, textarea { background: #2d2d2d !important; border-color: #404040 !important; }
                    `;
                    document.head.appendChild(style);
                })();
            """)
        return super().acceptNavigationRequest(url, _type, isMainFrame)

class WebAppWidget(QWidget):
    def __init__(self, url, parent=None):
        super().__init__(parent)
        self.url = url
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
        
        # Create web view with dark mode page
        self.web_view = QWebEngineView()
        self.page = DarkModePage(self.web_view)
        self.web_view.setPage(self.page)
        self.web_view.setUrl(QUrl(self.url))
        self.web_view.setMinimumSize(QSize(1280, 768))  # 1600*0.8 = 1280, 960*0.8 = 768
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