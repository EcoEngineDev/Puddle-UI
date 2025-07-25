import os
from typing import Tuple
from PyQt5.QtCore import QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage

VECTOR_MAP_ID = "8ffd5464ed7851a4af500474"

class _GeoPage(QWebEnginePage):
    def featurePermissionRequested(self, origin, feature):
        self.setFeaturePermission(
            origin, feature,
            QWebEnginePage.PermissionGrantedByUser
            if feature == QWebEnginePage.Geolocation
            else QWebEnginePage.PermissionDeniedByUser
        )

class MapsWidget(QWebEngineView):
    def __init__(
        self,
        api_key: str | None = None,
        center: Tuple[float, float] = (40.758, -73.9855),
        parent=None
    ):
        super().__init__(parent)
        key  = api_key or os.getenv("GOOGLE_MAPS_API_KEY", "")
        here = os.path.dirname(__file__)
        html = open(os.path.join(here, "map.html"), encoding="utf-8").read()
        css  = open(os.path.join(here, "map.css"),  encoding="utf-8").read()
        js   = open(os.path.join(here, "map.js"),   encoding="utf-8").read()
        html = (
            html
            .replace("__API_KEY__", key)
            .replace("__MAP_ID__",  VECTOR_MAP_ID)
            .replace("__LAT__",     str(center[0]))
            .replace("__LNG__",     str(center[1]))
            .replace("/*INLINE_CSS*/", css)
            .replace("//INLINE_JS",  js)
        )
        self.setPage(_GeoPage(self))
        self.setHtml(html, QUrl("https://localhost/"))
