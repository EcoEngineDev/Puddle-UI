import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl

class BrowserWindow(QMainWindow):
    def __init__(self, url):
        super().__init__()
        self.setWindowTitle("PyQt5 Web Browser")
        self.setGeometry(100, 100, 1200, 800)

        # Create web view
        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl(url))

        # Set central widget
        self.setCentralWidget(self.browser)

def main():
    app = QApplication(sys.argv)
    window = BrowserWindow("https://tidal.com")  # Change to your desired URL
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
