from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtWidgets import QFrame, QVBoxLayout
from PyQt5.QtWebEngineWidgets import (
    QWebEngineProfile,
    QWebEnginePage,
    QWebEngineView,
)


class GeoPage(QWebEnginePage):
    def featurePermissionRequested(self, origin, feature):
        if feature == QWebEnginePage.Geolocation:
            self.setFeaturePermission(
                origin, feature, QWebEnginePage.PermissionGrantedByUser
            )
        else:
            super().featurePermissionRequested(origin, feature)


class MiniMapWidget(QFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.setFixedSize(300, 300)
        self.setStyleSheet("background:#000;border:2px solid #444;border-radius:8px;")
        self.setWindowFlags(Qt.Widget | Qt.FramelessWindowHint)

        profile = QWebEngineProfile("mini-map", self)
        profile.setHttpUserAgent(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )

        self.view = QWebEngineView(self)
        self.view.setPage(GeoPage(profile, self.view))
        self.view.setContextMenuPolicy(Qt.NoContextMenu)
        self.view.setFixedSize(296, 296)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(2, 2, 2, 2)
        lay.addWidget(self.view)

        self._load_leaflet()
        parent.installEventFilter(self)
        self._reposition()
        self.show()

    def _load_leaflet(self):
        html = """
        <!DOCTYPE html>
        <html>
        <head>
          <meta charset="utf-8">
          <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
          <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
          <style>html,body,#map{height:100%;margin:0}</style>
        </head>
        <body>
          <div id="map"></div>
          <script>
            const map = L.map('map',{
              zoomControl:false,
              attributionControl:false,
              minZoom:3,maxZoom:18
            }).setView([39.8283,-98.5795],4);

            L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',{
              maxZoom:18
            }).addTo(map);

            if(navigator.geolocation){
              navigator.geolocation.watchPosition(p=>{
                const lat=p.coords.latitude, lon=p.coords.longitude;
                map.setView([lat,lon],14);
              });
            }
          </script>
        </body>
        </html>
        """
        self.view.setHtml(html, QUrl())

    def eventFilter(self, obj, ev):
        if obj is self.parent() and ev.type() == ev.Resize:
            self._reposition()
        return False

    def _reposition(self):
        self.move(12, self.parent().height() - self.height() - 12)
