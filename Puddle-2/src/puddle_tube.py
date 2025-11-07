"""Standalone PuddleTube viewer for the Puddle 2 application."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, cast
from urllib.parse import quote_plus

from PyQt6 import QtCore, QtGui, QtNetwork, QtWidgets
from PyQt6.QtCore import QUrl

try:  # pragma: no cover - optional dependency
    from PyQt6.QtWebEngineWidgets import QWebEngineView
except ImportError:  # pragma: no cover - optional dependency
    QWebEngineView = None  # type: ignore[assignment]

try:  # pragma: no cover - optional dependency
    from PyQt6.QtWebEngineCore import QWebEnginePage  # PyQt6 >= 6.4
except ImportError:  # pragma: no cover - compatibility for older wheels
    try:
        from PyQt6.QtWebEngineWidgets import QWebEnginePage  # type: ignore[assignment]
    except ImportError:
        QWebEnginePage = None  # type: ignore[assignment]

try:  # pragma: no cover - optional dependency
    from yt_dlp import YoutubeDL
except ImportError:  # pragma: no cover - optional dependency
    YoutubeDL = None  # type: ignore[assignment]

from . import theme
from .ytmusic_backend import Track
from .loader_widget import LoaderWidget


@dataclass
class SearchResult:
    """Minimal representation of a YouTube search result."""

    title: str
    url: str
    channel: str
    duration: str
    description: str
    video_id: Optional[str]
    thumbnail_url: Optional[str]


class _SearchSignals(QtCore.QObject):
    """Signals exposed by the background search runnable."""

    resultsReady = QtCore.pyqtSignal(str, list)
    errorOccurred = QtCore.pyqtSignal(str, str)


class _SearchTask(QtCore.QRunnable):
    """Background worker that resolves YouTube search results through yt-dlp."""

    _YDL_OPTIONS = {
        "format": "bestaudio/best",
        "quiet": True,
        "noplaylist": True,
        "nocheckcertificate": True,
        "skip_download": True,
        "restrictfilenames": True,
        "no_warnings": True,
        "ignoreerrors": True,
    }

    def __init__(self, query: str) -> None:
        super().__init__()
        self.query = query
        self.signals = _SearchSignals()

    @QtCore.pyqtSlot()
    def run(self) -> None:
        if YoutubeDL is None:  # pragma: no cover - safety net
            self.signals.errorOccurred.emit(self.query, "yt-dlp is unavailable.")
            return

        try:
            with YoutubeDL(self._YDL_OPTIONS) as ydl:
                payload = ydl.extract_info(f"ytsearch10:{self.query}", download=False)
        except Exception as exc:  # pragma: no cover - network/runtime failures
            self.signals.errorOccurred.emit(self.query, str(exc))
            return

        entries = payload.get("entries") if isinstance(payload, dict) else None
        results: List[SearchResult] = []
        if entries:
            for entry in entries:
                if not isinstance(entry, dict):
                    continue
                video_id = entry.get("id") or entry.get("video_id")
                url = entry.get("webpage_url") or (
                    f"https://www.youtube.com/watch?v={video_id}" if video_id else ""
                )
                if not url:
                    continue
                title = entry.get("title") or "Untitled"
                channel = entry.get("uploader") or entry.get("channel") or ""
                duration = _format_duration(entry.get("duration"), entry.get("is_live"))
                description = _trim_description(entry.get("description") or "")
                thumbnail_url = entry.get("thumbnail")
                if not thumbnail_url:
                    thumbs = entry.get("thumbnails") or []
                    if thumbs:
                        thumbnail_url = thumbs[-1].get("url")
                results.append(
                    SearchResult(
                        title=title,
                        url=url,
                        channel=channel,
                        duration=duration,
                        description=description,
                        video_id=video_id,
                        thumbnail_url=thumbnail_url,
                    )
                )

        self.signals.resultsReady.emit(self.query, results)


def _format_duration(duration: Optional[int], is_live: Optional[bool]) -> str:
    """Return a compact, human-friendly duration string."""
    if is_live:
        return "Live"
    if duration is None:
        return "Unknown"
    hours, remainder = divmod(int(duration), 3600)
    minutes, seconds = divmod(remainder, 60)
    if hours:
        return f"{hours:d}:{minutes:02d}:{seconds:02d}"
    return f"{minutes:d}:{seconds:02d}"


def _trim_description(description: str, limit: int = 200) -> str:
    """Collapse description text for the compact result cards."""
    collapsed = " ".join(description.split())
    if len(collapsed) <= limit:
        return collapsed
    return f"{collapsed[: limit - 1]}…"

if QWebEnginePage is not None:

    class _PuddleTubeWebPage(QWebEnginePage):
        """Custom WebEngine page that surfaces player configuration issues."""

        configurationError = QtCore.pyqtSignal(str)

        def javaScriptConsoleMessage(self, level, message, line, source_id):  # type: ignore[override]
            if "Player configuration error" in message:
                self.configurationError.emit(message)
            super().javaScriptConsoleMessage(level, message, line, source_id)

else:  # pragma: no cover - WebEngine unavailable
    _PuddleTubeWebPage = None  # type: ignore[assignment]


class SearchResultCard(QtWidgets.QFrame):
    """Visual card that presents a search result with thumbnail and metadata."""

    activated = QtCore.pyqtSignal(object)

    THUMBNAIL_SIZE = QtCore.QSize(144, 81)  # 16:9

    def __init__(self, result: SearchResult, palette: Dict[str, str], parent: Optional[QtWidgets.QWidget] = None) -> None:
        super().__init__(parent)
        self.setObjectName("puddleTubeResultCard")
        self.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        self.setProperty("selected", False)

        self._result = result
        self._palette = palette
        self._placeholder = self._build_placeholder()

        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(18)

        self.thumbnailLabel = QtWidgets.QLabel(self)
        self.thumbnailLabel.setObjectName("puddleTubeResultImage")
        self.thumbnailLabel.setFixedSize(self.THUMBNAIL_SIZE)
        self.thumbnailLabel.setScaledContents(True)
        self.thumbnailLabel.setPixmap(self._placeholder)
        layout.addWidget(self.thumbnailLabel)

        text_layout = QtWidgets.QVBoxLayout()
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(6)

        self.titleLabel = QtWidgets.QLabel(result.title, self)
        self.titleLabel.setObjectName("puddleTubeResultTitle")
        self.titleLabel.setWordWrap(True)
        text_layout.addWidget(self.titleLabel)

        meta_text = " • ".join(filter(None, [result.channel, result.duration]))
        self.metaLabel = QtWidgets.QLabel(meta_text or "YouTube", self)
        self.metaLabel.setObjectName("puddleTubeResultMeta")
        self.metaLabel.setWordWrap(True)
        text_layout.addWidget(self.metaLabel)

        self.descriptionLabel = QtWidgets.QLabel(result.description, self)
        self.descriptionLabel.setObjectName("puddleTubeResultDescription")
        self.descriptionLabel.setWordWrap(True)
        self.descriptionLabel.setVisible(bool(result.description))
        self.descriptionLabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        text_layout.addWidget(self.descriptionLabel, 1)

        layout.addLayout(text_layout, 1)

    # ------------------------------------------------------------------ Card helpers
    @property
    def result(self) -> SearchResult:
        return self._result

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent) -> None:  # noqa: N802
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self.activated.emit(self)
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def set_selected(self, selected: bool) -> None:
        if bool(self.property("selected")) == selected:
            return
        self.setProperty("selected", selected)
        self.style().unpolish(self)
        self.style().polish(self)

    def set_thumbnail(self, pixmap: Optional[QtGui.QPixmap]) -> None:
        if pixmap is None or pixmap.isNull():
            self.thumbnailLabel.setPixmap(self._placeholder)
            return
        scaled = pixmap.scaled(
            self.THUMBNAIL_SIZE,
            QtCore.Qt.AspectRatioMode.KeepAspectRatioByExpanding,
            QtCore.Qt.TransformationMode.SmoothTransformation,
        )
        self.thumbnailLabel.setPixmap(scaled)

    def set_palette(self, palette: Dict[str, str]) -> None:
        self._palette = palette
        self._placeholder = self._build_placeholder()
        if not self.thumbnailLabel.pixmap() or self.thumbnailLabel.pixmap() == self._placeholder:
            self.thumbnailLabel.setPixmap(self._placeholder)

    def _build_placeholder(self) -> QtGui.QPixmap:
        primary = theme.css_to_qcolor(self._palette["primary"])
        hover = theme.css_to_qcolor(self._palette["primary_hover"])
        pixmap = QtGui.QPixmap(self.THUMBNAIL_SIZE)
        pixmap.fill(QtCore.Qt.GlobalColor.transparent)
        painter = QtGui.QPainter(pixmap)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        gradient = QtGui.QLinearGradient(0, 0, self.THUMBNAIL_SIZE.width(), self.THUMBNAIL_SIZE.height())
        gradient.setColorAt(0.0, hover)
        gradient.setColorAt(1.0, primary)
        painter.setBrush(gradient)
        painter.setPen(QtGui.QPen(QtGui.QColor(0, 0, 0, 60), 2))
        rect = QtCore.QRectF(1, 1, self.THUMBNAIL_SIZE.width() - 2, self.THUMBNAIL_SIZE.height() - 2)
        painter.drawRoundedRect(rect, 10, 10)
        painter.end()
        return pixmap


class PuddleTubeView(QtWidgets.QWidget):
    """Full-size PuddleTube surface that mirrors the QtTube-inspired layout."""

    closeRequested = QtCore.pyqtSignal()

    def __init__(
        self,
        color_scheme: Dict[str, str],
        parent: Optional[QtWidgets.QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("puddleTubePage")
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_StyledBackground, True)

        self._colors = theme.puddletube_palette(color_scheme)
        self._current_track: Optional[Track] = None
        self._pending_track: Optional[Track] = None
        self._search_results: List[SearchResult] = []
        self._search_jobs: List[_SearchTask] = []
        self._current_search_query: str = ""
        self._search_busy = False
        self._web_engine_available = QWebEngineView is not None

        self._expanded = False
        self.webPage: Optional[_PuddleTubeWebPage] = None
        self._result_cards: List[SearchResultCard] = []
        self._selected_card: Optional[SearchResultCard] = None

        self._thumb_manager = QtNetwork.QNetworkAccessManager(self)
        self._thumb_requests: Dict[QtNetwork.QNetworkReply, SearchResultCard] = {}

        self._current_video_id: Optional[str] = None
        self._follow_now_playing = False
        self._player_mode: str = "placeholder"
        self._needs_watch_styling = False
        self._manual_video_active = False

        self._build_ui()
        self.apply_scheme(color_scheme)

        self._search_pool = QtCore.QThreadPool(self)

    # ------------------------------------------------------------------ UI construction
    def _build_ui(self) -> None:
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(22)

        header_frame = QtWidgets.QFrame(self)
        header_frame.setObjectName("puddleTubeHeader")
        header_layout = QtWidgets.QHBoxLayout(header_frame)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(12)

        self.backButton = QtWidgets.QToolButton(header_frame)
        self.backButton.setObjectName("puddleTubeBackButton")
        self.backButton.setText("Home")
        self.backButton.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        self.backButton.clicked.connect(self.closeRequested.emit)
        header_layout.addWidget(self.backButton)

        self.titleLabel = QtWidgets.QLabel("PuddleTube", header_frame)
        self.titleLabel.setObjectName("puddleTubeTitle")
        title_font = self.titleLabel.font()
        title_font.setPointSize(24)
        title_font.setBold(True)
        self.titleLabel.setFont(title_font)
        header_layout.addWidget(self.titleLabel)

        header_layout.addStretch(1)

        self.expandButton = QtWidgets.QToolButton(header_frame)
        self.expandButton.setObjectName("puddleTubeExpandButton")
        self.expandButton.setText("Expand")
        self.expandButton.setCheckable(True)
        self.expandButton.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        self.expandButton.setToolTip("Expand video panel")
        self.expandButton.toggled.connect(self._handle_expand_toggled)
        header_layout.addWidget(self.expandButton)

        self.searchField = QtWidgets.QLineEdit(header_frame)
        self.searchField.setObjectName("puddleTubeSearchField")
        self.searchField.setPlaceholderText("Search YouTube…")
        self.searchField.setClearButtonEnabled(True)
        header_layout.addWidget(self.searchField, 1)

        self.searchButton = QtWidgets.QToolButton(header_frame)
        self.searchButton.setObjectName("puddleTubeSearchButton")
        self.searchButton.setText("Search")
        self.searchButton.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        self.searchButton.clicked.connect(self._run_search)
        header_layout.addWidget(self.searchButton)

        self.searchField.returnPressed.connect(self._run_search)

        layout.addWidget(header_frame)

        body_layout = QtWidgets.QHBoxLayout()
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(24)
        self.bodyLayout = body_layout

        # -- Left column: video panel -------------------------------------------------
        self.videoPanel = QtWidgets.QFrame(self)
        self.videoPanel.setObjectName("puddleTubeVideoPanel")
        video_layout = QtWidgets.QVBoxLayout(self.videoPanel)
        video_layout.setContentsMargins(24, 24, 24, 24)
        video_layout.setSpacing(18)

        self.videoStack = QtWidgets.QStackedWidget(self.videoPanel)
        self.videoStack.setObjectName("puddleTubeVideoStack")
        self.videoPlaceholder = QtWidgets.QLabel(
            "Search or pick a track to start watching.",
            self.videoStack,
        )
        self.videoPlaceholder.setObjectName("puddleTubeVideoPlaceholder")
        self.videoPlaceholder.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.videoPlaceholder.setWordWrap(True)
        self.videoStack.addWidget(self.videoPlaceholder)

        if self._web_engine_available:
            web = QWebEngineView(self.videoStack)  # type: ignore[assignment]
            web.setObjectName("puddleTubeWebView")
            if _PuddleTubeWebPage is not None:
                self.webPage = _PuddleTubeWebPage(web)
                self.webPage.configurationError.connect(self._on_embed_configuration_error)
                web.setPage(self.webPage)
            web.setUrl(QUrl("about:blank"))
            web.loadFinished.connect(self._on_web_load_finished)
            self.webView = web
        else:
            fallback = QtWidgets.QTextBrowser(self.videoStack)
            fallback.setObjectName("puddleTubeFallback")
            fallback.setOpenExternalLinks(True)
            fallback.setHtml(
                "<h2>PuddleTube</h2>"
                "<p>PyQt6-WebEngine is required for embedded playback.</p>"
                "<p>After adding <code>PyQt6-WebEngine</code> to requirements.txt "
                "rebuild the Docker image to enable inline video.</p>"
            )
            self.webView = fallback
        self.videoStack.addWidget(self.webView)
        self.videoStack.setCurrentWidget(self.videoPlaceholder)
        video_layout.addWidget(self.videoStack, 1)

        meta_frame = QtWidgets.QFrame(self.videoPanel)
        meta_frame.setObjectName("puddleTubeMetaFrame")
        meta_layout = QtWidgets.QVBoxLayout(meta_frame)
        meta_layout.setContentsMargins(0, 0, 0, 0)
        meta_layout.setSpacing(4)

        self.nowPlayingLabel = QtWidgets.QLabel("Nothing playing", meta_frame)
        self.nowPlayingLabel.setObjectName("puddleTubeNowPlayingTitle")
        self.nowPlayingLabel.setWordWrap(True)
        meta_layout.addWidget(self.nowPlayingLabel)

        self.nowPlayingMeta = QtWidgets.QLabel(
            "Search results or YouTube Music tracks will appear here once selected.",
            meta_frame,
        )
        self.nowPlayingMeta.setObjectName("puddleTubeNowPlayingMeta")
        self.nowPlayingMeta.setWordWrap(True)
        meta_layout.addWidget(self.nowPlayingMeta)

        video_layout.addWidget(meta_frame)

        body_layout.addWidget(self.videoPanel, 3)

        # -- Right column: search results -------------------------------------------
        self.sidePanel = QtWidgets.QFrame(self)
        self.sidePanel.setObjectName("puddleTubeSidePanel")
        side_layout = QtWidgets.QVBoxLayout(self.sidePanel)
        side_layout.setContentsMargins(24, 24, 24, 24)
        side_layout.setSpacing(16)

        self.searchSectionLabel = QtWidgets.QLabel("Search Results", self.sidePanel)
        self.searchSectionLabel.setObjectName("puddleTubeSectionLabel")
        side_layout.addWidget(self.searchSectionLabel)

        self.loadingContainer = QtWidgets.QFrame(self.sidePanel)
        self.loadingContainer.setObjectName("puddleTubeLoadingContainer")
        loading_layout = QtWidgets.QHBoxLayout(self.loadingContainer)
        loading_layout.setContentsMargins(0, 8, 0, 8)
        loading_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        default_scheme = theme.ensure_all_keys(theme.DEFAULT_SCHEME)
        self.searchLoader = LoaderWidget(
            size=QtCore.QSize(220, 220),
            message="SEARCHING…",
            parent=self.loadingContainer,
        )
        self.searchLoader.set_palette(
            primary=theme.css_to_qcolor(default_scheme["primary"]),
            primary_hover=theme.css_to_qcolor(default_scheme["primary_hover"]),
            primary_active=theme.css_to_qcolor(default_scheme["primary_active"]),
            text=theme.css_to_qcolor(default_scheme["text_primary"]),
        )
        loading_layout.addWidget(self.searchLoader, alignment=QtCore.Qt.AlignmentFlag.AlignCenter)
        self.loadingContainer.hide()
        side_layout.addWidget(self.loadingContainer)

        self.resultsScroll = QtWidgets.QScrollArea(self.sidePanel)
        self.resultsScroll.setObjectName("puddleTubeResultsScroll")
        self.resultsScroll.setWidgetResizable(True)
        self.resultsScroll.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.resultsContainer = QtWidgets.QWidget()
        self.resultsContainer.setObjectName("puddleTubeResultsContainer")
        self.resultsLayout = QtWidgets.QVBoxLayout(self.resultsContainer)
        self.resultsLayout.setContentsMargins(0, 0, 0, 0)
        self.resultsLayout.setSpacing(12)
        self.resultsLayout.addStretch(1)

        self.resultsScroll.setWidget(self.resultsContainer)
        side_layout.addWidget(self.resultsScroll, 1)

        body_layout.addWidget(self.sidePanel, 2)
        layout.addLayout(body_layout, 1)
        self.bodyLayout.setStretch(0, 3)
        self.bodyLayout.setStretch(1, 2)

        self.statusLabel = QtWidgets.QLabel(
            "Browse YouTube or pick a track to load its official video.", self
        )
        self.statusLabel.setObjectName("puddleTubeStatusLabel")
        self.statusLabel.setWordWrap(True)
        layout.addWidget(self.statusLabel)

        self._update_expand_button_state()

    # ------------------------------------------------------------------ Actions
    def _run_search(self) -> None:
        query = self.searchField.text().strip()
        if not query:
            return

        if YoutubeDL is None:
            encoded = quote_plus(query)
            url = QUrl(f"https://www.youtube.com/results?search_query={encoded}")
            self._load_url(url)
            self.statusLabel.setText(f"Showing web results for “{query}”.")
            return

        self._current_search_query = query
        self.searchLoader.set_message(f"Searching for “{query}”…")
        self._set_search_busy(True)
        self.statusLabel.setText(f"Searching for “{query}”…")

        task = _SearchTask(query)
        task.signals.resultsReady.connect(self._on_search_results)
        task.signals.errorOccurred.connect(self._on_search_error)
        self._search_jobs.append(task)
        self._search_pool.start(task)

    def _set_search_busy(self, busy: bool) -> None:
        if self._search_busy == busy:
            return
        self._search_busy = busy
        self.searchField.setEnabled(not busy)
        self.searchButton.setEnabled(not busy)
        self.searchButton.setText("Searching…" if busy else "Search")
        self.loadingContainer.setVisible(busy)
        self.resultsScroll.setVisible(not busy)
        if busy:
            self.searchLoader.set_message("SEARCHING…")
            self.searchLoader.start()
        else:
            self.searchLoader.stop()

    def _handle_expand_toggled(self, checked: bool) -> None:
        self._set_expanded(checked)

    def _set_expanded(self, expanded: bool) -> None:
        if self._expanded == expanded:
            return
        self._expanded = expanded
        self.sidePanel.setVisible(not expanded)
        if expanded:
            self.bodyLayout.setStretch(0, 1)
            self.bodyLayout.setStretch(1, 0)
        else:
            self.bodyLayout.setStretch(0, 3)
            self.bodyLayout.setStretch(1, 2)
        self._update_expand_button_state()

    def _update_expand_button_state(self) -> None:
        label = "Collapse" if self._expanded else "Expand"
        tooltip = "Return to split view" if self._expanded else "Expand video panel"
        block = self.expandButton.blockSignals(True)
        self.expandButton.setChecked(self._expanded)
        self.expandButton.blockSignals(block)
        self.expandButton.setText(label)
        self.expandButton.setToolTip(tooltip)

    def _load_url(self, url: QUrl) -> None:
        if self._web_engine_available:
            web = cast(QWebEngineView, self.webView)
            if web.url() != url:
                web.setUrl(url)
        else:
            html = (
                "<h2>PuddleTube</h2>"
                f'<p>Open in your browser: <a href="{url.toString()}">{url.toString()}</a></p>'
            )
            if isinstance(self.webView, QtWidgets.QTextBrowser):
                self.webView.setHtml(html)
        self.videoStack.setCurrentWidget(self.webView)

    def _load_video_id(self, video_id: str) -> None:
        if not video_id:
            return
        self._current_video_id = video_id
        if self._web_engine_available:
            self._load_embed_mode(video_id)
        else:
            self._load_watch_placeholder(video_id)

    def _load_embed_mode(self, video_id: str) -> None:
        if not self._web_engine_available:
            return
        self._player_mode = "embed"
        self._needs_watch_styling = False
        iframe_url = (
            "https://www.youtube-nocookie.com/embed/"
            f"{video_id}?autoplay=1&modestbranding=1&rel=0&playsinline=1"
            "&enablejsapi=1&origin=https://www.youtube-nocookie.com"
        )
        if QWebEngineView is None:
            return
        html = f"""
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <style>
      html, body {{
        margin: 0;
        padding: 0;
        background: transparent;
        overflow: hidden;
        height: 100%;
      }}
      .frame {{
        position: absolute;
        inset: 0;
        border: none;
        width: 100%;
        height: 100%;
        background: transparent;
      }}
    </style>
  </head>
  <body>
    <iframe
      class="frame"
      src="{iframe_url}"
      title="YouTube video player"
      allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
      allowfullscreen
      referrerpolicy="strict-origin-when-cross-origin"
    ></iframe>
  </body>
</html>
"""
        cast(QWebEngineView, self.webView).setHtml(html, QUrl("https://www.youtube-nocookie.com"))
        self.videoStack.setCurrentWidget(self.webView)

    def _load_watch_mode(self, video_id: str) -> None:
        if not self._web_engine_available:
            self._load_watch_placeholder(video_id)
            return
        self._player_mode = "watch"
        self._needs_watch_styling = True
        watch_url = QUrl(
            f"https://www.youtube.com/watch?v={video_id}&bpctr=9999999999&has_verified=1"
        )
        self._load_url(watch_url)

    def _load_watch_placeholder(self, video_id: str) -> None:
        watch_url = QUrl(f"https://www.youtube.com/watch?v={video_id}")
        html = (
            "<h2>PuddleTube</h2>"
            f"<p>Embedded playback requires PyQt6-WebEngine.</p>"
            f'<p>Open in your browser: <a href="{watch_url.toString()}">{watch_url.toString()}</a></p>'
        )
        if isinstance(self.webView, QtWidgets.QTextBrowser):
            self.webView.setHtml(html)
        self.videoStack.setCurrentWidget(self.webView)

    def _on_embed_configuration_error(self, message: str) -> None:
        if self._player_mode != "embed" or not self._current_video_id:
            return
        self.statusLabel.setText("Embedded playback blocked; loading full YouTube player.")
        self._load_watch_mode(self._current_video_id)

    def _on_web_load_finished(self, ok: bool) -> None:
        if not ok or not self._web_engine_available:
            return
        if self._player_mode == "watch" and self._needs_watch_styling:
            self._inject_watch_styles()
            self._needs_watch_styling = False

    def _inject_watch_styles(self) -> None:
        if not self._web_engine_available or QWebEngineView is None:
            return
        web_view = cast(QWebEngineView, self.webView)
        css_rules = """
body, html {
  background: transparent !important;
  overflow: hidden !important;
}
ytd-app, #content, #page-manager {
  background: transparent !important;
}
#masthead-container,
#guide,
#secondary,
#guide-content,
#header,
#footer,
#chat,
#comments,
tp-yt-paper-toast,
ytd-mini-guide-renderer {
  display: none !important;
}
#primary {
  margin: 0 !important;
  width: 100% !important;
}
ytd-watch-flexy {
  --ytd-watch-flexy-sidebar-width: 0px !important;
  --ytd-watch-flexy-masthead-height: 0px !important;
  background: transparent !important;
}
#player-theater-container,
#player-container {
  max-width: 100% !important;
  margin: 0 auto !important;
  box-shadow: none !important;
}
"""
        js = f"""
(function() {{
  const styleId = "puddle-tube-watch-style";
  let style = document.getElementById(styleId);
  if (!style) {{
    style = document.createElement('style');
    style.id = styleId;
    style.textContent = `{css_rules}`;
    document.head.appendChild(style);
  }}
  const app = document.querySelector('ytd-watch-flexy');
  if (app) {{
    app.setAttribute('theater', '');
    app.setAttribute('fullscreen', '');
  }}
}})();
"""
        web_view.page().runJavaScript(js)
    def _on_search_results(self, query: str, results: List[SearchResult]) -> None:
        self._search_jobs = [job for job in self._search_jobs if job.query != query]
        if query != self._current_search_query:
            return  # stale search response
        self._set_search_busy(False)
        self._search_results = results
        self._populate_results(results)

        if not results:
            self.statusLabel.setText(f"No results found for “{query}”.")
        else:
            self.statusLabel.setText(f"Showing results for “{query}”. Click a card to watch.")

    def _on_search_error(self, query: str, message: str) -> None:
        self._search_jobs = [job for job in self._search_jobs if job.query != query]
        if query == self._current_search_query:
            self._set_search_busy(False)
            self.statusLabel.setText(f"Search failed: {message}")

    def _populate_results(self, results: List[SearchResult]) -> None:
        self._clear_results()

        if not results:
            label = QtWidgets.QLabel("No matches. Try a different search term.", self.resultsContainer)
            label.setObjectName("puddleTubeNoResultsLabel")
            label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            label.setWordWrap(True)
            self.resultsLayout.insertWidget(0, label)
            return

        for result in results:
            card = SearchResultCard(result, self._colors, self.resultsContainer)
            card.activated.connect(self._on_result_card_clicked)
            self._result_cards.append(card)
            self.resultsLayout.insertWidget(self.resultsLayout.count() - 1, card)
            if result.thumbnail_url:
                self._fetch_thumbnail(result.thumbnail_url, card)

    def _clear_results(self) -> None:
        for reply, card in list(self._thumb_requests.items()):
            try:
                reply.finished.disconnect(self._handle_thumbnail_reply)
            except TypeError:
                pass
            reply.abort()
            reply.deleteLater()
            if card not in self._result_cards:
                card.deleteLater()
        self._thumb_requests.clear()

        while self.resultsLayout.count():
            item = self.resultsLayout.takeAt(0)
            if item is None:
                continue
            widget = item.widget()
            if widget:
                widget.deleteLater()
        self.resultsLayout.addStretch(1)

        for card in self._result_cards:
            card.deleteLater()
        self._result_cards.clear()
        self._selected_card = None

    def _fetch_thumbnail(self, url: str, card: SearchResultCard) -> None:
        request = QtNetwork.QNetworkRequest(QUrl(url))
        reply = self._thumb_manager.get(request)
        reply.finished.connect(self._handle_thumbnail_reply)
        self._thumb_requests[reply] = card

    def _handle_thumbnail_reply(self) -> None:
        reply = self.sender()
        if not isinstance(reply, QtNetwork.QNetworkReply):  # pragma: no cover - safety net
            return
        card = self._thumb_requests.pop(reply, None)
        if card:
            if reply.error() == QtNetwork.QNetworkReply.NetworkError.NoError:
                data = reply.readAll()
                pixmap = QtGui.QPixmap()
                pixmap.loadFromData(bytes(data))
                card.set_thumbnail(pixmap)
            else:
                card.set_thumbnail(None)
        reply.deleteLater()

    def _on_result_card_clicked(self, card: SearchResultCard) -> None:
        self._select_card(card)
        result = card.result
        if result.video_id:
            self._load_video_id(result.video_id)
        else:
            self._current_video_id = None
            self._load_url(QUrl(result.url))
        self._current_track = None
        self.nowPlayingLabel.setText(result.title)
        meta_bits = [result.channel, result.duration]
        self.nowPlayingMeta.setText(" • ".join(filter(None, meta_bits)) or "YouTube")
        self.statusLabel.setText(f"Playing search result: {result.title}")
        self._enter_manual_video_mode()

    def _select_card(self, card: Optional[SearchResultCard]) -> None:
        if self._selected_card is card:
            return
        if self._selected_card:
            self._selected_card.set_selected(False)
        self._selected_card = card
        if card:
            card.set_selected(True)

    def _enter_manual_video_mode(self) -> None:
        self._manual_video_active = True
        if self._follow_now_playing:
            self.set_follow_now_playing(False)

    def display_track(self, track: Optional[Track]) -> None:
        self._pending_track = track
        if not self._follow_now_playing or self._manual_video_active:
            return

        self._current_track = track
        self._select_card(None)
        if not track or not track.uri:
            self.nowPlayingLabel.setText("Nothing playing")
            self.nowPlayingMeta.setText("Search for a video or choose a track to begin.")
            self.statusLabel.setText("Browse YouTube or pick a track to load its official video.")
            self._reset_video_surface()
            return

        self.nowPlayingLabel.setText(track.name or "Unknown Title")
        self.nowPlayingMeta.setText(track.artist or "Unknown Artist")
        self.statusLabel.setText(f"Now playing: {track.name} — {track.artist}")
        if self._current_video_id == track.uri and self._player_mode != "placeholder":
            return
        self._load_video_id(track.uri)

    # ------------------------------------------------------------------ Theme & content
    def set_follow_now_playing(self, enabled: bool) -> None:
        if self._follow_now_playing == enabled:
            return
        self._follow_now_playing = enabled
        if enabled:
            self._manual_video_active = False
            self._select_card(None)
            if self._pending_track:
                self.display_track(self._pending_track)
        else:
            if not self._manual_video_active:
                self._reset_video_surface()

    def stop_video(self) -> None:
        """Stop any embedded playback (used when leaving the view)."""
        self._manual_video_active = False
        self._reset_video_surface("Video stopped.")

    def _reset_video_surface(self, message: Optional[str] = None) -> None:
        """Clear the video container so hidden widgets do not keep playing audio."""
        if self._web_engine_available and QWebEngineView is not None and isinstance(self.webView, QWebEngineView):
            cast(QWebEngineView, self.webView).setHtml("<html><body></body></html>")
        elif isinstance(self.webView, QtWidgets.QTextBrowser):
            self.webView.clear()
        self.videoStack.setCurrentWidget(self.videoPlaceholder)
        self._player_mode = "placeholder"
        self._current_video_id = None
        if message:
            self.statusLabel.setText(message)
        if not self._manual_video_active:
            self._select_card(None)

    def apply_scheme(self, scheme: Dict[str, str]) -> None:
        self._colors = theme.puddletube_palette(scheme)
        primary = self._colors["primary"]
        primary_hover = self._colors["primary_hover"]
        primary_active = self._colors["primary_active"]
        surface = self._colors["surface"]
        surface_alt = self._colors["surface_alt"]
        text_primary = self._colors["text_primary"]
        text_muted = self._colors["text_muted"]
        stylesheet = f"""
QWidget#puddleTubePage {{
  background: {surface};
  color: {text_primary};
}}

QFrame#puddleTubeHeader {{
  background: transparent;
}}

QLabel#puddleTubeTitle {{
  color: {text_primary};
}}

QFrame#puddleTubeVideoPanel,
QFrame#puddleTubeSidePanel {{
  border-radius: 28px;
  border: 1px solid {primary_hover};
  background: {surface_alt};
}}

QStackedWidget#puddleTubeVideoStack {{
  border-radius: 24px;
  background: {surface};
}}

QLabel#puddleTubeVideoPlaceholder {{
  color: {text_muted};
  padding: 24px;
}}

QLabel#puddleTubeNowPlayingTitle {{
  color: {text_primary};
  font-size: 20px;
  font-weight: 600;
}}

QLabel#puddleTubeNowPlayingMeta {{
  color: {text_muted};
  font-size: 14px;
}}

QLabel#puddleTubeSectionLabel {{
  color: {text_primary};
  font-size: 15px;
  font-weight: 600;
  letter-spacing: 0.4px;
}}

QScrollArea#puddleTubeResultsScroll {{
  border: none;
  background: transparent;
}}

QWidget#puddleTubeResultsContainer {{
  background: transparent;
}}

QToolButton#puddleTubeBackButton,
QToolButton#puddleTubeSearchButton,
QToolButton#puddleTubeExpandButton {{
  background: {primary};
  border-radius: 20px;
  padding: 10px 22px;
  color: {text_primary};
  font-weight: 600;
}}

QToolButton#puddleTubeBackButton:hover,
QToolButton#puddleTubeSearchButton:hover,
QToolButton#puddleTubeExpandButton:hover {{
  background: {primary_hover};
}}

QToolButton#puddleTubeBackButton:pressed,
QToolButton#puddleTubeSearchButton:pressed,
QToolButton#puddleTubeExpandButton:pressed {{
  background: {primary_active};
}}

QToolButton#puddleTubeExpandButton:checked {{
  background: {primary_active};
}}

QFrame#puddleTubeLoadingContainer {{
  border-radius: 18px;
  border: 1px dashed {primary_hover};
  background: {surface};
}}

QLineEdit#puddleTubeSearchField {{
  border-radius: 20px;
  border: 1px solid {primary_hover};
  padding: 8px 16px;
  background: {surface};
  color: {text_primary};
  selection-background-color: {primary};
  selection-color: {text_primary};
}}

QFrame#puddleTubeResultCard {{
  border-radius: 20px;
  border: 1px solid {primary_hover};
  background: {surface};
}}

QFrame#puddleTubeResultCard:hover {{
  border: 1px solid {primary};
  background: {surface_alt};
}}

QFrame#puddleTubeResultCard[selected="true"] {{
  border: 2px solid {primary};
  background: {primary_hover};
}}

QLabel#puddleTubeResultTitle {{
  color: {text_primary};
  font-size: 15px;
  font-weight: 600;
}}

QLabel#puddleTubeResultMeta,
QLabel#puddleTubeResultDescription {{
  color: {text_muted};
  font-size: 13px;
}}

QLabel#puddleTubeStatusLabel {{
  color: {text_muted};
  font-size: 14px;
}}

QLabel#puddleTubeNoResultsLabel {{
  color: {text_muted};
  font-size: 14px;
}}
"""
        self.setStyleSheet(stylesheet)
        for card in self._result_cards:
            card.set_palette(self._colors)
        self._update_loader_palette()

    def set_content(self, current_track: Optional[Track], queue: Sequence[Track]) -> None:  # noqa: D401
        """Refresh the view with the latest queue context (queue currently unused)."""
        del queue
        self.display_track(current_track)

    def _update_loader_palette(self) -> None:
        primary = theme.css_to_qcolor(self._colors["primary"])
        primary_hover = theme.css_to_qcolor(self._colors["primary_hover"])
        primary_active = theme.css_to_qcolor(self._colors["primary_active"])
        text = theme.css_to_qcolor(self._colors["text_primary"])
        self.searchLoader.set_palette(
            primary=primary,
            primary_hover=primary_hover,
            primary_active=primary_active,
            text=text,
        )
