from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl
import json
import os

class MapWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        # Map view
        self.web_view = QWebEngineView()
        
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
                    height: 100%;
                    width: 100%;
                    background: #242f3e;
                }
                html, body {
                    height: 100%;
                    margin: 0;
                    padding: 0;
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
                    // Initialize map
                    map = L.map('map', {
                        minZoom: 3,
                        maxZoom: 18,
                        zoomControl: false,
                        attributionControl: false,
                        preferCanvas: true,  // Use canvas renderer for better performance
                        fadeAnimation: false, // Disable fade animations
                        zoomAnimation: true,  // Keep zoom animations but they'll be faster
                        markerZoomAnimation: false, // Disable marker zoom animations
                        transform3DLimit: 2  // Reduce 3D transform precision for better performance
                    }).setView([51.505, -0.09], 13);
                    
                    // Add dark theme tile layer
                    L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
                        maxZoom: 18,
                        attribution: null,
                        updateWhenIdle: true,  // Only update when user stops moving
                        updateWhenZooming: false,  // Don't update while zooming
                        keepBuffer: 2  // Reduce tile buffer size
                    }).addTo(map);

                    // Try HTML5 geolocation
                    if (navigator.geolocation) {
                        navigator.geolocation.getCurrentPosition(
                            (position) => {
                                const pos = [position.coords.latitude, position.coords.longitude];
                                map.setView(pos, 13);
                            }
                        );
                    }
                }

                window.onload = initMap;
            </script>
        </body>
        </html>
        '''
        
        self.web_view.setHtml(html_content)
        layout.addWidget(self.web_view)
        
        self.setLayout(layout) 