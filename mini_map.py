import os
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QFrame
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage, QWebEngineProfile, QWebEngineSettings
from PyQt5.QtCore import QUrl, QSize, Qt
from PyQt5.QtGui import QFont
# from debug_logger import debug_logger

class MiniMapPage(QWebEnginePage):
    def __init__(self, profile, parent=None):
        super().__init__(profile, parent)
        # Enable touch-friendly settings
        settings = self.settings()
        settings.setAttribute(QWebEngineSettings.JavascriptEnabled, True)
        settings.setAttribute(QWebEngineSettings.ScrollAnimatorEnabled, True)
        settings.setAttribute(QWebEngineSettings.PluginsEnabled, True)
        settings.setAttribute(QWebEngineSettings.FullScreenSupportEnabled, True)
        # Set touch-optimized defaults
        settings.setFontSize(QWebEngineSettings.DefaultFontSize, 16)
        settings.setFontSize(QWebEngineSettings.MinimumFontSize, 14)

class MiniMapWidget(QWidget):
    def __init__(self, parent=None):
        try:
            # debug_logger.log_function_entry("__init__", "MiniMapWidget", parent=parent)
            super().__init__(parent)
            # Create custom profile with modified settings
            # debug_logger.log_info("Creating mini map web engine profile", "MiniMapWidget")
            self.profile = QWebEngineProfile("minimap_profile")
            self.profile.setHttpUserAgent("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
            self.setup_ui()
            self.hide()  # Hidden by default
            # debug_logger.log_function_exit("__init__", "MiniMapWidget")
        except Exception as e:
            # debug_logger.log_error(f"Error initializing MiniMapWidget: {str(e)}", "MiniMapWidget", exc_info=True)
            print(f"Error initializing MiniMapWidget: {str(e)}")
            # Create a simple fallback widget instead of crashing
            super().__init__(parent)
            self.setStyleSheet("background:#000;color:#666;text-align:center;border:2px solid #444;border-radius:8px;")
            self.setFixedSize(300, 300)
            self.hide()

    def setup_ui(self):
        # Main layout
        layout = QVBoxLayout()
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(0)
        
        # Container for web view
        web_container = QFrame()
        web_layout = QVBoxLayout(web_container)
        web_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create web view for Mini Map with touch-optimized page
        # debug_logger.log_info("Creating mini map web view", "MiniMapWidget")
        self.web_view = QWebEngineView()
        self.page = MiniMapPage(self.profile, self.web_view)
        self.web_view.setPage(self.page)
        # debug_logger.log_info("Loading Leaflet map", "MiniMapWidget")
        self._load_leaflet()
        self.web_view.setMinimumSize(QSize(296, 296))  # Slightly smaller than container
        web_layout.addWidget(self.web_view)
        
        # Add web container to main layout
        layout.addWidget(web_container)
        self.setLayout(layout)
        
    def _load_leaflet(self):
        # debug_logger.log_function_entry("_load_leaflet", "MiniMapWidget")
        # Create a simple Leaflet map HTML
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
            <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
            <style>
                body { margin: 0; padding: 0; }
                #map { height: 100vh; width: 100vw; }
            </style>
        </head>
        <body>
            <div id="map"></div>
            <script>
                // Initialize the map
                var map = L.map('map').setView([40.758, -73.9855], 13);
                
                // Add OpenStreetMap tiles
                L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                    maxZoom: 19,
                    attribution: '© OpenStreetMap contributors'
                }).addTo(map);
                
                // Add a marker for current location (placeholder)
                var marker = L.marker([40.758, -73.9855]).addTo(map);
                marker.bindPopup("<b>Current Location</b><br>New York, NY").openPopup();
                
                // Disable scroll wheel zoom to prevent accidental zooming
                map.scrollWheelZoom.disable();
                
                // Disable dragging to prevent map movement
                map.dragging.disable();
            </script>
        </body>
        </html>
        """
        
        self.web_view.setHtml(html, QUrl("https://localhost/"))
        # debug_logger.log_function_exit("_load_leaflet", "MiniMapWidget")
