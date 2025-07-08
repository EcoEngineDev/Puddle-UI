from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl, QSize
import json
import os

class MapWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 20, 0)  # Add right margin
        layout.setSpacing(0)

        # Map view
        self.web_view = QWebEngineView()
        self.web_view.setMinimumSize(QSize(1360, 780))  # 800 * 1.7 = 1360, 600 * 1.3 = 780
        
        # Load the HTML with OpenStreetMap and Leaflet
        html_content = '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Navigation Map</title>
            <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
            <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
            <style>
                #map {
                    height: 100vh;
                    width: 100%;
                    background: #242f3e;
                }
                html, body {
                    height: 100vh;
                    margin: 0;
                    padding: 0;
                    overflow: hidden;
                }
                .leaflet-control-attribution {
                    display: none !important;
                }
                .leaflet-control-zoom {
                    display: none !important;
                }
            </style>
        </head>
        <body>
            <div id="map"></div>
            <script>
                let map;
                
                function initMap() {
                    // Initialize map centered on United States
                    map = L.map('map', {
                        minZoom: 3,
                        maxZoom: 18,
                        zoomControl: false,
                        attributionControl: false,
                        preferCanvas: true,
                        fadeAnimation: false,
                        zoomAnimation: true,
                        markerZoomAnimation: false,
                        transform3DLimit: 2
                    }).setView([39.8283, -98.5795], 4);
                    
                    // Add dark theme tile layer
                    L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
                        maxZoom: 18,
                        attribution: null,
                        updateWhenIdle: true,
                        updateWhenZooming: false,
                        keepBuffer: 2
                    }).addTo(map);

                    // Only try geolocation if explicitly requested
                    window.tryGeolocation = function() {
                        if (navigator.geolocation) {
                            navigator.geolocation.getCurrentPosition(
                                (position) => {
                                    const pos = [position.coords.latitude, position.coords.longitude];
                                    map.setView(pos, 13);
                                }
                            );
                        }
                    };
                }

                window.onload = initMap;
            </script>
        </body>
        </html>
        '''
        
        self.web_view.setHtml(html_content)
        layout.addWidget(self.web_view)
        
        self.setLayout(layout)
        
    def sizeHint(self):
        return QSize(1360, 780)  # Updated preferred size for the map 