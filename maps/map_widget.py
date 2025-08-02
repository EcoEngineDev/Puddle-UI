import os
from typing import Tuple
from PyQt5.QtCore import QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage
# from debug_logger import debug_logger

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
        try:
            # debug_logger.log_function_entry("__init__", "MapsWidget", api_key=api_key, center=center, parent=parent)
            super().__init__(parent)
            key  = api_key or os.getenv("GOOGLE_MAPS_API_KEY", "")
            
            # Debug: Check API key
            if not key:
                # debug_logger.log_warning("No Google Maps API key found! This will cause the map to fail to load", "MapsWidget")
                print("No Google Maps API key found! This will cause the map to fail to load")
            else:
                # debug_logger.log_info(f"MapsWidget: API key loaded (length: {len(key)})", "MapsWidget")
                print(f"MapsWidget: API key loaded (length: {len(key)})")
            here = os.path.dirname(__file__)
            
            # Debug: Check if files exist
            html_path = os.path.join(here, "map.html")
            css_path = os.path.join(here, "map.css")
            js_path = os.path.join(here, "map.js")
            
            if not os.path.exists(html_path):
                # debug_logger.log_error(f"map.html not found at: {html_path}", "MapsWidget")
                print(f"map.html not found at: {html_path}")
                return
            if not os.path.exists(css_path):
                # debug_logger.log_error(f"map.css not found at: {css_path}", "MapsWidget")
                print(f"map.css not found at: {css_path}")
                return
            if not os.path.exists(js_path):
                # debug_logger.log_error(f"map.js not found at: {js_path}", "MapsWidget")
                print(f"map.js not found at: {js_path}")
                return
                
            # debug_logger.log_debug(f"Reading map files from: {here}", "MapsWidget")
            try:
                html = open(html_path, encoding="utf-8").read()
                css  = open(css_path,  encoding="utf-8").read()
                js   = open(js_path,   encoding="utf-8").read()
            except UnicodeDecodeError:
                # Windows fallback: try with different encoding
                # debug_logger.log_warning("Unicode decode error, trying with cp1252 encoding", "MapsWidget")
                print("Unicode decode error, trying with cp1252 encoding")
                html = open(html_path, encoding="cp1252").read()
                css  = open(css_path,  encoding="cp1252").read()
                js   = open(js_path,   encoding="cp1252").read()
            html = (
                html
                .replace("__API_KEY__", key)
                .replace("__MAP_ID__",  VECTOR_MAP_ID)
                .replace("__LAT__",     str(center[0]))
                .replace("__LNG__",     str(center[1]))
                .replace("/*INLINE_CSS*/", css)
                .replace("//INLINE_JS",  js)
            )
            # debug_logger.log_info("Setting up map web page", "MapsWidget")
            self.setPage(_GeoPage(self))
            self.setHtml(html, QUrl("https://localhost/"))
            # debug_logger.log_info("Map widget initialization completed", "MapsWidget")
            # debug_logger.log_function_exit("__init__", "MapsWidget")
        except Exception as e:
            # debug_logger.log_error(f"Error initializing MapsWidget: {str(e)}", "MapsWidget", exc_info=True)
            print(f"Error initializing MapsWidget: {str(e)}")
            # Create a simple fallback widget instead of crashing
            super().__init__(parent)
            self.setHtml("<html><body style='background:#000;color:#fff;text-align:center;padding:50px;'><h2>Map Loading Error</h2><p>Unable to load Google Maps</p></body></html>")



