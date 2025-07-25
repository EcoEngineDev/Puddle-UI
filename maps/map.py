from __future__ import annotations
import os
from typing import Tuple
from PyQt5.QtCore import QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage

VECTOR_MAP_ID = "gmapid-xxxxxxxxxxxxxxxx"

class _GeoPage(QWebEnginePage):
    def featurePermissionRequested(self, origin, feature):
        if feature == QWebEnginePage.Geolocation:
            self.setFeaturePermission(origin, feature, QWebEnginePage.PermissionGrantedByUser)
        else:
            self.setFeaturePermission(origin, feature, QWebEnginePage.PermissionDeniedByUser)

class MapsWidget(QWebEngineView):
    def __init__(
        self,
        api_key: str | None = None,
        center: Tuple[float, float] = (40.758, -73.9855),
        parent=None
    ) -> None:
        super().__init__(parent)
        key = api_key or os.getenv("GOOGLE_MAPS_API_KEY", "")
        if not key:
            raise ValueError("Set GOOGLE_MAPS_API_KEY in env or pass api_key")
        if not VECTOR_MAP_ID.startswith("gmapid-"):
            raise ValueError("Replace VECTOR_MAP_ID with your Vector Map ID")

        tmpl_path = os.path.join(os.path.dirname(__file__), "map.html")
        with open(tmpl_path, "r", encoding="utf-8") as f:
            html = f.read()

        html = html.replace("__API_KEY__", key)
        html = html.replace("__MAP_ID__", VECTOR_MAP_ID)
        html = html.replace("__LAT__", str(center[0]))
        html = html.replace("__LNG__", str(center[1]))

        self.setPage(_GeoPage(self))
        self.setHtml(html, QUrl("https://localhost/"))
