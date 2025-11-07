"""Mini Games hub view for launching web-based puzzles."""

from __future__ import annotations

from typing import Dict, Iterable, Optional, cast

from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import QUrl

try:  # pragma: no cover - optional dependency
    from PyQt6.QtWebEngineWidgets import QWebEngineView
except ImportError:  # pragma: no cover - optional dependency
    QWebEngineView = None  # type: ignore[assignment]

from . import theme
from .loader_widget import LoaderWidget


class MiniGamesView(QtWidgets.QWidget):
    """Dedicated surface for browsing and launching mini games."""

    closeRequested = QtCore.pyqtSignal()

    def __init__(
        self,
        color_scheme: Dict[str, str],
        games: Iterable[Dict[str, str]],
        parent: Optional[QtWidgets.QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("miniGamesPage")
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_StyledBackground, True)

        self._scheme = theme.ensure_all_keys(color_scheme)
        self._games: Dict[str, Dict[str, str]] = {entry["name"]: entry for entry in games}
        self._web_engine_available = QWebEngineView is not None
        self._current_game: Optional[str] = None

        self._build_ui()
        self.apply_scheme(self._scheme)

    # ------------------------------------------------------------------ UI construction
    def _build_ui(self) -> None:
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(22)

        header = QtWidgets.QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)
        header.setSpacing(12)

        self.backButton = QtWidgets.QToolButton(self)
        self.backButton.setObjectName("miniGamesBackButton")
        self.backButton.setText("Home")
        self.backButton.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        self.backButton.clicked.connect(self.closeRequested.emit)
        header.addWidget(self.backButton)

        self.titleLabel = QtWidgets.QLabel("Mini Games", self)
        self.titleLabel.setObjectName("miniGamesTitle")
        title_font = self.titleLabel.font()
        title_font.setPointSize(24)
        title_font.setBold(True)
        self.titleLabel.setFont(title_font)
        header.addWidget(self.titleLabel)

        header.addStretch(1)
        layout.addLayout(header)

        body_layout = QtWidgets.QHBoxLayout()
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(24)

        # Left side: game player + loader
        self.gamePanel = QtWidgets.QFrame(self)
        self.gamePanel.setObjectName("miniGamesPlayerPanel")
        game_panel_layout = QtWidgets.QVBoxLayout(self.gamePanel)
        game_panel_layout.setContentsMargins(24, 24, 24, 24)
        game_panel_layout.setSpacing(18)

        self.gameStack = QtWidgets.QStackedWidget(self.gamePanel)
        self.gameStack.setObjectName("miniGamesStack")

        self.loaderWidget = LoaderWidget(message="SELECT A GAME", parent=self.gameStack)
        self.gameStack.addWidget(self.loaderWidget)

        if self._web_engine_available:
            self.webView = QWebEngineView(self.gameStack)  # type: ignore[assignment]
            self.webView.setObjectName("miniGamesWebView")
            self.webView.loadFinished.connect(self._on_load_finished)
            self.webView.loadStarted.connect(self._on_load_started)
        else:
            browser = QtWidgets.QTextBrowser(self.gameStack)
            browser.setObjectName("miniGamesFallback")
            browser.setOpenExternalLinks(True)
            self.webView = browser
        self.gameStack.addWidget(self.webView)
        self.gameStack.setCurrentWidget(self.loaderWidget)
        game_panel_layout.addWidget(self.gameStack, 1)

        self.statusLabel = QtWidgets.QLabel("Pick a game on the right to begin.", self.gamePanel)
        self.statusLabel.setObjectName("miniGamesStatusLabel")
        self.statusLabel.setWordWrap(True)
        game_panel_layout.addWidget(self.statusLabel)

        body_layout.addWidget(self.gamePanel, 3)

        # Right side: game selection
        self.sidePanel = QtWidgets.QFrame(self)
        self.sidePanel.setObjectName("miniGamesSidePanel")
        side_layout = QtWidgets.QVBoxLayout(self.sidePanel)
        side_layout.setContentsMargins(24, 24, 24, 24)
        side_layout.setSpacing(16)

        self.listLabel = QtWidgets.QLabel("Available Games", self.sidePanel)
        self.listLabel.setObjectName("miniGamesListLabel")
        side_layout.addWidget(self.listLabel)

        self.gameList = QtWidgets.QListWidget(self.sidePanel)
        self.gameList.setObjectName("miniGamesList")
        self.gameList.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        self.gameList.itemActivated.connect(self._activate_selected_game)
        self.gameList.currentItemChanged.connect(self._update_game_details)
        side_layout.addWidget(self.gameList, 1)

        self.descriptionLabel = QtWidgets.QLabel("Select a game to view its description.", self.sidePanel)
        self.descriptionLabel.setObjectName("miniGamesDescription")
        self.descriptionLabel.setWordWrap(True)
        self.descriptionLabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        side_layout.addWidget(self.descriptionLabel)

        body_layout.addWidget(self.sidePanel, 2)
        layout.addLayout(body_layout, 1)

        self._populate_game_list()
        self.loaderWidget.start()

    # ------------------------------------------------------------------ Public API
    def apply_scheme(self, scheme: Dict[str, str]) -> None:
        self._scheme = theme.ensure_all_keys(scheme)
        primary = self._scheme["primary"]
        primary_hover = self._scheme["primary_hover"]
        primary_active = self._scheme["primary_active"]
        surface = self._scheme["card_gradient_mid"]
        surface_alt = self._scheme["card_gradient_end"]
        text_primary = self._scheme["text_primary"]
        text_muted = self._scheme["text_muted"]

        stylesheet = f"""
QWidget#miniGamesPage {{
  background: {self._scheme["background"]};
  color: {text_primary};
}}

QFrame#miniGamesPlayerPanel,
QFrame#miniGamesSidePanel {{
  border-radius: 28px;
  border: 1px solid {primary_hover};
  background: {surface};
}}

QStackedWidget#miniGamesStack {{
  border-radius: 24px;
  background: {self._scheme["tube_surface"]};
}}

QLabel#miniGamesTitle {{
  color: {text_primary};
}}

QLabel#miniGamesStatusLabel,
QLabel#miniGamesDescription {{
  color: {text_muted};
  font-size: 14px;
}}

QLabel#miniGamesListLabel {{
  color: {text_primary};
  font-size: 15px;
  font-weight: 600;
  letter-spacing: 0.4px;
}}

QListWidget#miniGamesList {{
  background: transparent;
  border: 1px solid {primary_hover};
  border-radius: 18px;
  padding: 6px;
}}

QListWidget#miniGamesList::item {{
  padding: 10px 12px;
  border-radius: 14px;
}}

QListWidget#miniGamesList::item:selected {{
  background: {primary};
  color: {text_primary};
}}

QToolButton#miniGamesBackButton {{
  background: {primary};
  border-radius: 20px;
  padding: 10px 22px;
  color: {text_primary};
  font-weight: 600;
}}

QToolButton#miniGamesBackButton:hover {{
  background: {primary_hover};
}}

QToolButton#miniGamesBackButton:pressed {{
  background: {primary_active};
}}
"""
        self.setStyleSheet(stylesheet)
        self.loaderWidget.set_palette(
            primary=theme.css_to_qcolor(primary),
            primary_hover=theme.css_to_qcolor(primary_hover),
            primary_active=theme.css_to_qcolor(primary_active),
            text=theme.css_to_qcolor(text_primary),
        )

    def reset(self) -> None:
        """Return to the loader state with no game selected."""
        self.gameList.clearSelection()
        self.descriptionLabel.setText("Select a game to view its description.")
        self.loaderWidget.set_message("SELECT A GAME")
        self.loaderWidget.start()
        self.gameStack.setCurrentWidget(self.loaderWidget)
        self.statusLabel.setText("Pick a game on the right to begin.")
        self._current_game = None

    # ------------------------------------------------------------------ Internal helpers
    def _populate_game_list(self) -> None:
        self.gameList.clear()
        for name, info in self._games.items():
            item = QtWidgets.QListWidgetItem(name)
            item.setData(QtCore.Qt.ItemDataRole.UserRole, info)
            self.gameList.addItem(item)

    def _activate_selected_game(self, item: QtWidgets.QListWidgetItem) -> None:
        info = item.data(QtCore.Qt.ItemDataRole.UserRole)
        if not isinstance(info, dict):
            return
        self._launch_game(info)

    def _update_game_details(
        self,
        current: Optional[QtWidgets.QListWidgetItem],
        _: Optional[QtWidgets.QListWidgetItem],
    ) -> None:
        if current is None:
            self.descriptionLabel.setText("Select a game to view its description.")
            return
        info = current.data(QtCore.Qt.ItemDataRole.UserRole)
        if not isinstance(info, dict):
            return
        description = info.get("description") or "Click to launch this game."
        self.descriptionLabel.setText(description)

    def _launch_game(self, info: Dict[str, str]) -> None:
        name = info.get("name", "Mini Game")
        url = info.get("url")
        if not url:
            return
        self._current_game = name
        self.loaderWidget.set_message(f"Loading {name}…")
        self.loaderWidget.start()
        self.gameStack.setCurrentWidget(self.loaderWidget)
        self.statusLabel.setText(f"Loading {name}…")

        if self._web_engine_available and isinstance(self.webView, QWebEngineView):
            self.webView.setUrl(QUrl(url))
        else:
            notice = (
                f"<h2>{name}</h2>"
                "<p>Embedded browsing requires PyQt6-WebEngine.</p>"
                f'<p>Open in your browser: <a href="{url}">{url}</a></p>'
            )
            browser = cast(QtWidgets.QTextBrowser, self.webView)
            browser.setHtml(notice)
            self.loaderWidget.stop()
            self.gameStack.setCurrentWidget(self.webView)
            self.statusLabel.setText(f"Open {name} in your default browser.")

    def _on_load_started(self) -> None:
        self.loaderWidget.start()
        self.gameStack.setCurrentWidget(self.loaderWidget)

    def _on_load_finished(self, ok: bool) -> None:
        if ok:
            self.loaderWidget.stop()
            self.gameStack.setCurrentWidget(self.webView)
            if self._current_game:
                self.statusLabel.setText(f"Enjoy playing {self._current_game}!")
        else:
            self.loaderWidget.stop()
            self.statusLabel.setText("Unable to load the selected game. Check your connection.")
            self.gameStack.setCurrentWidget(self.loaderWidget)
