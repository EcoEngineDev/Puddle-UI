"""YouTube Music-backed mini player with a Spot-Thing inspired presentation."""

from __future__ import annotations

import logging
from typing import Dict, List, Optional

from PyQt6 import QtCore, QtGui, QtNetwork, QtWidgets
from PyQt6.QtCore import QRect, Qt, QTimer, QUrl
from PyQt6.QtMultimedia import QMediaPlayer
from PyQt6.QtGui import QGuiApplication
from PyQt6.QtWidgets import QListWidgetItem, QMessageBox

from . import theme
from .color_config_dialog import ColorConfigDialog
from .mini_games import MiniGamesView
from .puddle_tube import PuddleTubeView
from .ytmusic_backend import PlaybackState, Track, YTMusicBackend
from .ui_main_window import Ui_MainWindow


MINI_GAME_LINKS = [
    {
        "name": "Wordle",
        "url": "https://www.nytimes.com/games/wordle/index.html",
        "description": "Guess the five-letter word in six tries using colour-coded hints.",
    },
    {
        "name": "Connections",
        "url": "https://www.nytimes.com/games/connections",
        "description": "Group sixteen words into four themed sets without making too many mistakes.",
    },
    {
        "name": "Spelling Bee",
        "url": "https://www.nytimes.com/puzzles/spelling-bee",
        "description": "Build as many words as you can from seven letters, always using the centre hive.",
    },
    {
        "name": "Strands",
        "url": "https://www.nytimes.com/games/strands",
        "description": "Hunt for connected words hidden in the grid to reveal the daily theme.",
    },
]

LOG = logging.getLogger(__name__)
QUEUE_ART_SIZE = QtCore.QSize(156, 96)
SEEK_SYNC_TOLERANCE_MS = 2000


class QueueItemWidget(QtWidgets.QFrame):
    """Custom widget used for queue entries with album art and metadata."""

    def __init__(
        self,
        track: Track,
        duration_text: str,
        placeholder: QtGui.QPixmap,
        parent: Optional[QtWidgets.QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("queueItem")
        self.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)
        self.setFrameShadow(QtWidgets.QFrame.Shadow.Plain)
        self.setMinimumHeight(110)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self._placeholder = placeholder
        self._has_custom_art = False

        self._art_label = QtWidgets.QLabel(self)
        self._art_label.setFixedSize(QUEUE_ART_SIZE)
        self._art_label.setObjectName("queueArt")
        self._art_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._art_label.setContentsMargins(0, -20, 0, 0)

        self._title_label = QtWidgets.QLabel(self)
        self._title_label.setObjectName("queueTitle")
        self._title_label.setWordWrap(True)

        self._meta_label = QtWidgets.QLabel(self)
        self._meta_label.setObjectName("queueMeta")
        self._meta_label.setWordWrap(True)

        self._album_label = QtWidgets.QLabel(self)
        self._album_label.setObjectName("queueAlbum")
        self._album_label.setWordWrap(True)
        self._album_label.setAlignment(Qt.AlignmentFlag.AlignTop)

        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(18)
        layout.addWidget(self._art_label, alignment=Qt.AlignmentFlag.AlignTop)

        text_layout = QtWidgets.QVBoxLayout()
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(6)
        text_layout.addWidget(self._title_label)
        text_layout.addWidget(self._meta_label)
        text_layout.addWidget(self._album_label, 1)
        layout.addLayout(text_layout)
        layout.addStretch(1)

        self._playing = False
        self.set_playing(False)
        self.update_text(track, duration_text)
        self.set_art(None)

    def update_text(self, track: Track, duration_text: str) -> None:
        self._title_label.setText(track.name or "Unknown Title")
        artist = track.artist or "Unknown Artist"
        self._meta_label.setText(f"{artist} · {duration_text}")
        album = track.album or ""
        if album:
            self._album_label.setText(album)
            self._album_label.setVisible(True)
        else:
            self._album_label.clear()
            self._album_label.setVisible(False)
        tooltip_bits = [track.name or "Unknown Title", artist]
        if album:
            tooltip_bits.append(album)
        self.setToolTip("\n".join(tooltip_bits))

    def set_art(self, pixmap: Optional[QtGui.QPixmap]) -> None:
        if pixmap is None or pixmap.isNull():
            self._has_custom_art = False
            self._art_label.setPixmap(self._prepare_art_pixmap(self._placeholder))
        else:
            self._has_custom_art = True
            self._art_label.setPixmap(self._prepare_art_pixmap(pixmap))

    def set_playing(self, playing: bool) -> None:
        if self._playing == playing:
            return
        self._playing = playing
        self.setProperty("isPlaying", playing)
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()

    def update_placeholder(self, placeholder: QtGui.QPixmap) -> None:
        self._placeholder = placeholder
        if not self._has_custom_art:
            self._art_label.setPixmap(self._prepare_art_pixmap(self._placeholder))

    # ------------------------------------------------------------------ Internal helpers
    def _prepare_art_pixmap(self, pixmap: QtGui.QPixmap) -> QtGui.QPixmap:
        """Scale and crop album art to fill the square label with rounded corners."""
        target = self._art_label.size()
        if target.isEmpty() or pixmap.isNull():
            return pixmap
        scaled = pixmap.scaled(
            target,
            Qt.AspectRatioMode.KeepAspectRatioByExpanding,
            Qt.TransformationMode.SmoothTransformation,
        )
        if scaled.size() != target:
            x_off = max(0, (scaled.width() - target.width()) // 2)
            y_off = max(0, (scaled.height() - target.height()) // 2)
            scaled = scaled.copy(x_off, y_off, target.width(), target.height())

        rounded = QtGui.QPixmap(target)
        rounded.fill(QtCore.Qt.GlobalColor.transparent)
        painter = QtGui.QPainter(rounded)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        path = QtGui.QPainterPath()
        rect = QtCore.QRectF(0, 0, target.width(), target.height())
        path.addRoundedRect(rect, 18, 18)
        painter.setClipPath(path)
        painter.drawPixmap(0, 0, scaled)
        painter.end()
        return rounded


class MiniPlayerWindow(QtWidgets.QMainWindow):
    """Main application window that wires UI controls to YouTube Music playback."""

    POLL_INTERVAL_MS = 1000

    def __init__(self, parent: Optional[QtWidgets.QWidget] = None) -> None:
        super().__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.miniPage.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.ui.themeButton.setAutoRaise(False)
        self.ui.collapseButton.setAutoRaise(False)
        self.ui.queueList.setAlternatingRowColors(False)

        self.backend: Optional[YTMusicBackend] = None
        self.queue: List[Track] = []
        self.queue_widgets: Dict[int, QueueItemWidget] = {}
        self.current_track: Optional[Track] = None
        self.last_playback_state: Optional[PlaybackState] = None
        self.duration_ms: int = 0
        self._resume_after_puddletube = False
        self._user_scrubbing = False
        self._pending_seek_position: Optional[int] = None

        self.network = QtNetwork.QNetworkAccessManager(self)
        self._icon_requests: Dict[QtNetwork.QNetworkReply, int] = {}
        self._album_reply: Optional[QtNetwork.QNetworkReply] = None

        self.mini_poll_timer = QTimer(self)
        self.mini_poll_timer.setInterval(self.POLL_INTERVAL_MS)
        self.mini_poll_timer.timeout.connect(self._poll_playback)

        self.color_scheme = theme.load_scheme()
        self._icons: Dict[str, QtGui.QIcon] = {}
        self._queue_placeholder = QtGui.QPixmap()
        self._build_home_container()
        self._configure_signals()
        self._position_bottom_left()

        self._rebuild_theme_assets()

        try:
            self.backend = YTMusicBackend()
            self._media_player: Optional[QMediaPlayer] = self.backend.player
            self._media_player.mediaStatusChanged.connect(self._on_media_status_changed)
            self._media_player.errorOccurred.connect(self._on_player_error)
            self._media_player.durationChanged.connect(self._on_duration_changed)
            self.mini_poll_timer.start()
            self._set_status("Ready")
        except RuntimeError as exc:
            LOG.error("YouTube Music backend initialisation failed: %s", exc)
            QMessageBox.critical(
                self,
                "YouTube Music Setup",
                (
                    f"{exc}\n\n"
                    "Create a YouTube Music credentials file with `ytmusicapi oauth` "
                    "and set YTMUSIC_AUTH_FILE if you store it elsewhere."
                ),
            )
            self.backend = None
            self._media_player = None
            self._set_status("YouTube Music credentials required")

    # ------------------------------------------------------------------ Qt plumbing / theme
    def closeEvent(self, event: QtGui.QCloseEvent) -> None:  # noqa: N802
        self._cancel_icon_requests()
        self._cancel_album_request()
        if self.backend:
            self.backend.shutdown()
        super().closeEvent(event)

    def _configure_signals(self) -> None:
        self.ui.searchButton.clicked.connect(self._on_search_clicked)
        self.ui.searchField.returnPressed.connect(self._on_search_clicked)
        self.ui.queueList.itemDoubleClicked.connect(self._on_queue_double_clicked)
        self.ui.queueList.itemClicked.connect(self._on_queue_clicked)

        self.ui.playPauseButton.clicked.connect(self._toggle_play_pause)
        self.ui.miniPlayPauseButton.clicked.connect(self._toggle_play_pause)
        self.ui.nextButton.clicked.connect(self._play_next)
        self.ui.previousButton.clicked.connect(self._play_previous)
        self.ui.miniNextButton.clicked.connect(self._play_next)
        self.ui.miniPreviousButton.clicked.connect(self._play_previous)

        self.ui.volumeSlider.valueChanged.connect(self._set_volume)
        self.ui.progressSlider.sliderPressed.connect(self._begin_slider_scrub)
        self.ui.progressSlider.sliderMoved.connect(self._preview_slider_position)
        self.ui.progressSlider.sliderReleased.connect(self._seek_from_slider)

        self.ui.miniExpandButton.clicked.connect(self.expand)
        self.ui.collapseButton.clicked.connect(self.collapse)
        self.ui.themeButton.clicked.connect(self._open_theme_dialog)
        self.puddleTubeAppButton.clicked.connect(self._open_puddletube)

    def _build_home_container(self) -> None:
        """Create the launcher surface and reparent the mini player into it."""
        # Stretch layouts to cover the full window.
        self.ui.centralLayout.setContentsMargins(0, 0, 0, 0)
        self.ui.backgroundLayout.setContentsMargins(0, 0, 0, 0)
        if hasattr(self.ui, "backgroundVerticalSpacer"):
            self.ui.backgroundLayout.removeItem(self.ui.backgroundVerticalSpacer)
        if hasattr(self.ui, "cardPositionSpacer"):
            self.ui.cardPositionLayout.removeItem(self.ui.cardPositionSpacer)

        # Reparent the designer-created stacked widget into a new home page.
        self.ui.cardLayout.removeWidget(self.ui.viewStack)

        self.homeStack = QtWidgets.QStackedWidget(self.ui.mainCard)
        self.homeStack.setObjectName("homeStack")

        self.homePage = QtWidgets.QWidget(self.homeStack)
        self.homePage.setObjectName("homePage")
        self.homeLayout = QtWidgets.QVBoxLayout(self.homePage)
        self.homeLayout.setContentsMargins(0, 0, 0, 0)
        self.homeLayout.setSpacing(24)

        self.appRow = QtWidgets.QHBoxLayout()
        self.appRow.setSpacing(18)
        self.appRow.setContentsMargins(0, 0, 0, 0)

        self.puddleTubeAppWidget = QtWidgets.QWidget(self.homePage)
        self.puddleTubeAppWidget.setObjectName("puddleTubeAppWidget")
        app_layout = QtWidgets.QVBoxLayout(self.puddleTubeAppWidget)
        app_layout.setContentsMargins(0, 0, 0, 0)
        app_layout.setSpacing(8)

        self.puddleTubeAppButton = QtWidgets.QToolButton(self.puddleTubeAppWidget)
        self.puddleTubeAppButton.setObjectName("puddleTubeAppButton")
        self.puddleTubeAppButton.setToolTip("Open PuddleTube")
        self.puddleTubeAppButton.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        self.puddleTubeAppButton.setIconSize(QtCore.QSize(72, 72))
        self.puddleTubeAppButton.setFixedSize(96, 96)
        self.puddleTubeAppButton.setAutoRaise(False)
        self.puddleTubeAppButton.setCheckable(False)
        self.puddleTubeAppButton.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        self.puddleTubeAppLabel = QtWidgets.QLabel("PuddleTube", self.puddleTubeAppWidget)
        self.puddleTubeAppLabel.setObjectName("puddleTubeAppLabel")
        self.puddleTubeAppLabel.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        app_layout.addWidget(self.puddleTubeAppButton, alignment=Qt.AlignmentFlag.AlignHCenter)
        app_layout.addWidget(self.puddleTubeAppLabel)

        self.miniGameWidget = QtWidgets.QWidget(self.homePage)
        self.miniGameWidget.setObjectName("miniGameWidget")
        mini_layout = QtWidgets.QVBoxLayout(self.miniGameWidget)
        mini_layout.setContentsMargins(0, 0, 0, 0)
        mini_layout.setSpacing(8)

        self.miniGameButton = QtWidgets.QToolButton(self.miniGameWidget)
        self.miniGameButton.setObjectName("miniGameButton")
        self.miniGameButton.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        self.miniGameButton.setIconSize(QtCore.QSize(72, 72))
        self.miniGameButton.setFixedSize(96, 96)
        self.miniGameButton.setAutoRaise(False)
        self.miniGameButton.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.miniGameButton.clicked.connect(self._open_mini_games)

        self.miniGameLabel = QtWidgets.QLabel("Mini Games", self.miniGameWidget)
        self.miniGameLabel.setObjectName("miniGameLabel")
        self.miniGameLabel.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        mini_layout.addWidget(self.miniGameButton, alignment=Qt.AlignmentFlag.AlignHCenter)
        mini_layout.addWidget(self.miniGameLabel)

        self.appRow.addWidget(self.puddleTubeAppWidget)
        self.appRow.addWidget(self.miniGameWidget)
        self.appRow.addStretch(1)
        self.homeLayout.addLayout(self.appRow)

        self.ui.viewStack.setParent(self.homePage)
        self.ui.viewStack.setSizePolicy(
            QtWidgets.QSizePolicy(
                QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding
            )
        )

        self.playerHost = QtWidgets.QWidget(self.homePage)
        self.playerHost.setObjectName("playerHost")
        self.playerHostLayout = QtWidgets.QHBoxLayout(self.playerHost)
        self.playerHostLayout.setContentsMargins(0, 0, 0, 0)
        self.playerHostLayout.setSpacing(0)
        self.playerHostLayout.addWidget(self.ui.viewStack)

        self.homeLayout.addWidget(self.playerHost, 1)

        self.homeStack.addWidget(self.homePage)

        self.puddletube_view = PuddleTubeView(self.color_scheme, self.homeStack)
        self.puddletube_view.closeRequested.connect(self._close_puddletube)
        self.homeStack.addWidget(self.puddletube_view)

        self.miniGamesView = MiniGamesView(self.color_scheme, MINI_GAME_LINKS, self.homeStack)
        self.miniGamesView.closeRequested.connect(self._close_minigames)
        self.homeStack.addWidget(self.miniGamesView)

        self.homeStack.setCurrentWidget(self.homePage)

        self.ui.cardLayout.addWidget(self.homeStack)
        self._player_mode = "mini"
        self._set_player_mode("expanded")

    def _position_bottom_left(self) -> None:
        screen = QGuiApplication.primaryScreen()
        self._collapsed_size = QtCore.QSize(520, 260)
        self._expanded_size = QtCore.QSize(1460, 800)
        if not screen:
            self.resize(self._expanded_size)
            return
        available = screen.availableGeometry()
        margin = 40
        target_rect = QRect(
            available.left() + margin,
            available.bottom() - margin - self._expanded_size.height(),
            self._expanded_size.width(),
            self._expanded_size.height(),
        )
        self.setGeometry(target_rect)

    def _set_player_mode(self, mode: str) -> None:
        if mode == getattr(self, "_player_mode", None):
            return
        if mode == "mini":
            self.ui.viewStack.setCurrentWidget(self.ui.miniPage)
            self.ui.viewStack.setMaximumSize(QtCore.QSize(540, 260))
            self.ui.viewStack.setMinimumSize(QtCore.QSize(420, 220))
            self.playerHostLayout.setAlignment(
                self.ui.viewStack, Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignLeft
            )
        else:
            self.ui.viewStack.setCurrentWidget(self.ui.expandedPage)
            self.ui.viewStack.setMaximumSize(
                QtCore.QSize(QtWidgets.QWIDGETSIZE_MAX, QtWidgets.QWIDGETSIZE_MAX)
            )
            self.ui.viewStack.setMinimumSize(QtCore.QSize(1120, 580))
            self.playerHostLayout.setAlignment(self.ui.viewStack, Qt.AlignmentFlag.AlignCenter)
        self._player_mode = mode

    def expand(self) -> None:
        self._set_player_mode("expanded")

    def collapse(self) -> None:
        self._set_player_mode("mini")

    def _open_theme_dialog(self) -> None:
        dialog = ColorConfigDialog(self.color_scheme, self)
        if dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            self.color_scheme = theme.ensure_all_keys(dialog.colors)
            theme.save_scheme(self.color_scheme)
            self._rebuild_theme_assets()
            if self.current_track:
                self._update_album_art(self.current_track.image_url)

    def _open_puddletube(self) -> None:
        if not getattr(self, "puddletube_view", None):
            return
        self._pause_music_for_puddletube()
        self.puddletube_view.set_follow_now_playing(True)
        self._sync_puddletube_view()
        self.homeStack.setCurrentWidget(self.puddletube_view)

    def _open_mini_games(self) -> None:
        if not getattr(self, "miniGamesView", None):
            return
        self.miniGamesView.apply_scheme(self.color_scheme)
        self.miniGamesView.reset()
        self.homeStack.setCurrentWidget(self.miniGamesView)

    def _close_puddletube(self) -> None:
        if getattr(self, "puddletube_view", None):
            self.puddletube_view.set_follow_now_playing(False)
            self.puddletube_view.stop_video()
        self.homeStack.setCurrentWidget(self.homePage)
        self._resume_music_after_puddletube()

    def _pause_music_for_puddletube(self) -> None:
        if not self.backend:
            self._resume_after_puddletube = False
            return
        try:
            state = self.backend.current_playback()
        except Exception as exc:  # pragma: no cover - defensive
            LOG.debug("Unable to inspect playback state: %s", exc)
            state = self.last_playback_state
        should_pause = state.is_playing if state else False
        if should_pause:
            try:
                self.backend.pause()
                self._resume_after_puddletube = True
            except Exception as exc:  # pragma: no cover - backend failure
                LOG.debug("Failed to pause before opening PuddleTube: %s", exc)
                self._resume_after_puddletube = False
        else:
            self._resume_after_puddletube = False

    def _resume_music_after_puddletube(self) -> None:
        if not self.backend or not self._resume_after_puddletube:
            return
        try:
            self.backend.resume()
        except Exception as exc:  # pragma: no cover - backend failure
            LOG.debug("Failed to resume after closing PuddleTube: %s", exc)
        finally:
            self._resume_after_puddletube = False

    def _close_minigames(self) -> None:
        if getattr(self, "miniGamesView", None):
            self.miniGamesView.reset()
        self.homeStack.setCurrentWidget(self.homePage)

    def _rebuild_theme_assets(self) -> None:
        theme.apply(self.color_scheme)
        self._queue_placeholder = self._create_queue_placeholder()
        self._icons = {
            "play": self._build_play_icon(),
            "pause": self._build_pause_icon(),
            "next": self._build_skip_icon(True),
            "previous": self._build_skip_icon(False),
            "theme": self._build_theme_icon(),
            "puddleTubeApp": self._build_puddletube_app_icon(),
            "miniGames": self._build_minigame_icon(),
        }
        self._update_theme_icon()
        self._update_transport_icons()
        self._update_play_buttons(self.last_playback_state.is_playing if self.last_playback_state else False)
        self._update_puddletube_launcher()
        self._update_minigame_launcher()
        for widget in self.queue_widgets.values():
            widget.update_placeholder(self._queue_placeholder)
        self._apply_default_art()
        if self.puddletube_view:
            self.puddletube_view.apply_scheme(self.color_scheme)
            self._sync_puddletube_view()

    def _sync_puddletube_view(self) -> None:
        if not getattr(self, "puddletube_view", None):
            return
        self.puddletube_view.set_content(self.current_track, self.queue)
        self.puddletube_view.display_track(self.current_track)

    def _create_queue_placeholder(self) -> QtGui.QPixmap:
        primary = theme.css_to_qcolor(self.color_scheme["primary"])
        hover = theme.css_to_qcolor(self.color_scheme["primary_hover"])
        pixmap = QtGui.QPixmap(QUEUE_ART_SIZE)
        pixmap.fill(QtCore.Qt.GlobalColor.transparent)
        painter = QtGui.QPainter(pixmap)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        gradient = QtGui.QLinearGradient(0, 0, QUEUE_ART_SIZE.width(), QUEUE_ART_SIZE.height())
        gradient.setColorAt(0.0, primary)
        gradient.setColorAt(1.0, hover)
        painter.setBrush(gradient)
        painter.setPen(QtGui.QPen(QtGui.QColor(0, 0, 0, 60), 2))
        rect = QtCore.QRectF(1, 1, QUEUE_ART_SIZE.width() - 2, QUEUE_ART_SIZE.height() - 2)
        painter.drawRoundedRect(rect, 18, 18)
        painter.end()
        return pixmap

    def _build_play_icon(self) -> QtGui.QIcon:
        background = theme.css_to_qcolor(self.color_scheme["background"])
        accent = theme.css_to_qcolor(self.color_scheme["primary"])
        pixmap = QtGui.QPixmap(64, 64)
        pixmap.fill(QtCore.Qt.GlobalColor.transparent)
        painter = QtGui.QPainter(pixmap)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        painter.setBrush(accent)
        painter.setPen(QtGui.QPen(background, 0))
        path = QtGui.QPainterPath()
        path.moveTo(22, 16)
        path.lineTo(22, 48)
        path.lineTo(48, 32)
        path.closeSubpath()
        painter.drawPath(path)
        painter.end()
        return QtGui.QIcon(pixmap)

    def _build_pause_icon(self) -> QtGui.QIcon:
        background = theme.css_to_qcolor(self.color_scheme["background"])
        accent = theme.css_to_qcolor(self.color_scheme["primary"])
        pixmap = QtGui.QPixmap(64, 64)
        pixmap.fill(QtCore.Qt.GlobalColor.transparent)
        painter = QtGui.QPainter(pixmap)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        painter.setBrush(accent)
        painter.setPen(QtGui.QPen(background, 0))
        painter.drawRoundedRect(QtCore.QRectF(20, 16, 8, 32), 4, 4)
        painter.drawRoundedRect(QtCore.QRectF(34, 16, 8, 32), 4, 4)
        painter.end()
        return QtGui.QIcon(pixmap)

    def _build_skip_icon(self, forward: bool) -> QtGui.QIcon:
        background = theme.css_to_qcolor(self.color_scheme["background"])
        accent = theme.css_to_qcolor(self.color_scheme["primary"])
        pixmap = QtGui.QPixmap(64, 64)
        pixmap.fill(QtCore.Qt.GlobalColor.transparent)
        painter = QtGui.QPainter(pixmap)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        painter.setBrush(accent)
        painter.setPen(QtGui.QPen(background, 0))
        if not forward:
            painter.translate(64, 0)
            painter.scale(-1, 1)
        path = QtGui.QPainterPath()
        path.moveTo(18, 16)
        path.lineTo(18, 48)
        path.lineTo(38, 32)
        path.closeSubpath()
        painter.drawPath(path)
        painter.drawRoundedRect(QtCore.QRectF(40, 16, 6, 32), 3, 3)
        painter.end()
        return QtGui.QIcon(pixmap)

    def _build_theme_icon(self) -> QtGui.QIcon:
        primary = theme.css_to_qcolor(self.color_scheme["primary"])
        hover = theme.css_to_qcolor(self.color_scheme["primary_hover"])
        pixmap = QtGui.QPixmap(48, 48)
        pixmap.fill(QtCore.Qt.GlobalColor.transparent)
        painter = QtGui.QPainter(pixmap)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        gradient = QtGui.QRadialGradient(24, 24, 18)
        gradient.setColorAt(0.0, hover)
        gradient.setColorAt(1.0, primary)
        painter.setBrush(gradient)
        painter.setPen(QtGui.QPen(QtGui.QColor(0, 0, 0, 90), 3))
        painter.drawEllipse(QtCore.QRectF(6, 6, 36, 36))
        painter.end()
        return QtGui.QIcon(pixmap)

    def _build_puddletube_app_icon(self) -> QtGui.QIcon:
        palette = theme.puddletube_palette(self.color_scheme)
        primary = theme.css_to_qcolor(palette["primary"])
        hover = theme.css_to_qcolor(palette["primary_hover"])
        active = theme.css_to_qcolor(palette["primary_active"])
        pixmap = QtGui.QPixmap(72, 72)
        pixmap.fill(QtCore.Qt.GlobalColor.transparent)
        painter = QtGui.QPainter(pixmap)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        gradient = QtGui.QLinearGradient(0, 0, 72, 72)
        gradient.setColorAt(0.0, hover)
        gradient.setColorAt(1.0, primary)
        painter.setBrush(gradient)
        painter.setPen(QtGui.QPen(QtGui.QColor(0, 0, 0, 70), 2))
        painter.drawRoundedRect(QtCore.QRectF(4, 4, 64, 64), 18, 18)

        painter.setBrush(QtGui.QColor("#ffffff"))
        painter.setPen(QtGui.QPen(active, 1))
        painter.drawRoundedRect(QtCore.QRectF(34, 18, 8, 30), 3, 3)
        painter.drawEllipse(QtCore.QRectF(20, 38, 18, 14))
        painter.drawEllipse(QtCore.QRectF(38, 32, 18, 14))

        painter.end()
        return QtGui.QIcon(pixmap)

    def _build_minigame_icon(self) -> QtGui.QIcon:
        palette = theme.ensure_all_keys(self.color_scheme)
        primary = theme.css_to_qcolor(palette["primary"])
        hover = theme.css_to_qcolor(palette["primary_hover"])
        active = theme.css_to_qcolor(palette["primary_active"])
        pixmap = QtGui.QPixmap(72, 72)
        pixmap.fill(QtCore.Qt.GlobalColor.transparent)
        painter = QtGui.QPainter(pixmap)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        painter.setBrush(hover)
        painter.setPen(QtGui.QPen(QtGui.QColor(0, 0, 0, 70), 2))
        painter.drawRoundedRect(QtCore.QRectF(6, 6, 60, 60), 18, 18)

        painter.setPen(QtGui.QPen(active, 3))
        painter.setBrush(primary)
        cell_size = 14
        offsets = [(12, 12), (32, 12), (12, 32), (32, 32)]
        for x, y in offsets:
            painter.drawRoundedRect(QtCore.QRectF(x, y, cell_size, cell_size), 4, 4)

        painter.end()
        return QtGui.QIcon(pixmap)

    def _update_theme_icon(self) -> None:
        self.ui.themeButton.setIcon(self._icons["theme"])
        self.ui.themeButton.setIconSize(QtCore.QSize(24, 24))

    def _update_transport_icons(self) -> None:
        size = QtCore.QSize(26, 26)
        prev = self._icons.get("previous")
        nxt = self._icons.get("next")
        if prev:
            self.ui.previousButton.setIcon(prev)
            self.ui.previousButton.setIconSize(size)
            self.ui.miniPreviousButton.setIcon(prev)
            self.ui.miniPreviousButton.setIconSize(size)
        if nxt:
            self.ui.nextButton.setIcon(nxt)
            self.ui.nextButton.setIconSize(size)
            self.ui.miniNextButton.setIcon(nxt)
            self.ui.miniNextButton.setIconSize(size)

    def _update_puddletube_launcher(self) -> None:
        icon = self._icons.get("puddleTubeApp")
        if not icon:
            return
        palette = theme.puddletube_palette(self.color_scheme)
        self.puddleTubeAppButton.setIcon(icon)
        self.puddleTubeAppButton.setIconSize(QtCore.QSize(72, 72))
        surface = palette["surface"]
        surface_alt = palette["surface_alt"]
        active = palette["primary_hover"]
        self.puddleTubeAppButton.setStyleSheet(
            f"""
QToolButton#puddleTubeAppButton {{
  border: none;
  border-radius: 28px;
  background: {surface};
}}
QToolButton#puddleTubeAppButton:hover {{
  background: {surface_alt};
}}
QToolButton#puddleTubeAppButton:pressed {{
  background: {active};
}}
""".strip()
        )
        self.puddleTubeAppLabel.setStyleSheet(
            f"color: {palette['text_primary']}; font-size: 14px; font-weight: 500;"
        )

    def _update_minigame_launcher(self) -> None:
        if not hasattr(self, "miniGameButton"):
            return
        icon = self._icons.get("miniGames")
        if icon:
            self.miniGameButton.setIcon(icon)
            self.miniGameButton.setIconSize(QtCore.QSize(64, 64))
        self.miniGameButton.setToolTip("Open Mini Games")
        palette = theme.ensure_all_keys(self.color_scheme)
        surface = palette["card_gradient_mid"]
        surface_alt = palette["card_gradient_end"]
        active = palette["primary_hover"]
        text = palette["text_primary"]
        self.miniGameButton.setStyleSheet(
            f"""
QToolButton#miniGameButton {{
  border: none;
  border-radius: 24px;
  background: {surface};
  padding: 12px;
}}
QToolButton#miniGameButton:hover {{
  background: {surface_alt};
}}
QToolButton#miniGameButton:pressed {{
  background: {active};
}}
""".strip()
        )
        self.miniGameLabel.setStyleSheet(
            f"color: {text}; font-size: 14px; font-weight: 500;"
        )

    # ------------------------------------------------------------------ Search & queue
    def _on_search_clicked(self) -> None:
        query = self.ui.searchField.text().strip()
        if not query:
            return
        if not self.backend:
            QMessageBox.warning(self, "YouTube Music Setup", "Backend unavailable.")
            return

        self._set_status("Searching…")

        try:
            tracks = self.backend.search_tracks(query, limit=8)
        except Exception as exc:  # pragma: no cover - network issues
            LOG.exception("YouTube Music search failed: %s", exc)
            QMessageBox.warning(self, "YouTube Music Search", f"Search failed: {exc}")
            self._set_status("Search failed")
            return

        self.queue = tracks
        self.queue_widgets.clear()
        self._cancel_icon_requests()
        self.ui.queueList.clear()

        if not tracks:
            self._set_status("No results found")
            self._sync_puddletube_view()
            return

        for index, track in enumerate(tracks):
            item = QtWidgets.QListWidgetItem()
            widget = QueueItemWidget(
                track,
                self._format_duration(track.duration_ms),
                self._queue_placeholder,
                self,
            )
            item.setSizeHint(widget.sizeHint())
            self.ui.queueList.addItem(item)
            self.ui.queueList.setItemWidget(item, widget)
            self.queue_widgets[index] = widget
            self._ensure_queue_icon(track, index)

        self.ui.queueList.setCurrentRow(0)
        self._set_status("Ready")
        self._sync_puddletube_view()
        self._play_track(self.queue[0])

    def _on_queue_double_clicked(self, item: QListWidgetItem) -> None:
        row = self.ui.queueList.row(item)
        if 0 <= row < len(self.queue):
            self._play_track(self.queue[row])

    def _on_queue_clicked(self, item: QListWidgetItem) -> None:
        row = self.ui.queueList.row(item)
        if not (0 <= row < len(self.queue)):
            return
        track = self.queue[row]
        if self.current_track and self.current_track.uri == track.uri:
            return
        self._play_track(track)

    # ------------------------------------------------------------------ Playback control
    def _play_track(self, track: Track) -> None:
        if not self.backend:
            return
        try:
            self.backend.play_track(track)
            self.current_track = track
            self._update_track_labels(track)
            self._update_album_art(track.image_url)
            self._mark_queue_playing(track.uri)
            self.ui.progressSlider.setValue(0)
            self.ui.miniProgressBar.setValue(0)
            self._pending_seek_position = None
            self._user_scrubbing = False
            self._set_status("Buffering…")
            self._sync_puddletube_view()
        except Exception as exc:
            LOG.exception("Failed to start playback: %s", exc)
            QMessageBox.warning(self, "YouTube Music Playback", f"Unable to play track:\n{exc}")

    def _toggle_play_pause(self) -> None:
        if not self.backend:
            return
        state = self.last_playback_state
        try:
            if state and state.is_playing:
                self.backend.pause()
            else:
                if self.current_track:
                    self.backend.resume()
                elif self.queue:
                    self._play_track(self.queue[0])
        except Exception as exc:
            LOG.exception("Play/pause failed: %s", exc)
            QMessageBox.warning(self, "YouTube Music Playback", f"Unable to toggle playback:\n{exc}")

    def _play_next(self) -> None:
        self._advance_queue(1)

    def _play_previous(self) -> None:
        self._advance_queue(-1)

    def _set_volume(self, value: int) -> None:
        if not self.backend:
            return
        try:
            self.backend.set_volume(value)
        except Exception as exc:
            LOG.debug("Setting volume failed: %s", exc)

    def _begin_slider_scrub(self) -> None:
        self._user_scrubbing = True
        self._pending_seek_position = None

    def _preview_slider_position(self, value: int) -> None:
        if not self._user_scrubbing:
            return
        self.ui.miniProgressBar.setRange(0, self.duration_ms or 1)
        self.ui.miniProgressBar.setValue(value)
        self._update_time_indicators(value)

    def _seek_from_slider(self) -> None:
        position = self.ui.progressSlider.value()
        self._user_scrubbing = False
        self._pending_seek_position = position
        if not self.backend or not self.current_track:
            return
        self.ui.progressSlider.blockSignals(True)
        self.ui.progressSlider.setValue(position)
        self.ui.progressSlider.blockSignals(False)
        try:
            self.backend.seek(position)
            self._update_time_indicators(position)
            self.ui.miniProgressBar.setRange(0, self.duration_ms or 1)
            self.ui.miniProgressBar.setValue(position)
        except Exception as exc:
            LOG.debug("Seek failed: %s", exc)

    # ------------------------------------------------------------------ Polling
    def _poll_playback(self) -> None:
        if not self.backend:
            return
        try:
            state = self.backend.current_playback()
        except Exception as exc:  # pragma: no cover - network failure path
            LOG.debug("Polling playback failed: %s", exc)
            state = None

        self.last_playback_state = state
        if not state:
            self._set_status("Idle")
            self._update_play_buttons(False)
            self.ui.progressSlider.setValue(0)
            self.ui.miniProgressBar.setValue(0)
            return

        self._render_playback_state(state)

    def _render_playback_state(self, state: PlaybackState) -> None:
        self._update_play_buttons(state.is_playing)
        self._set_status("Playing" if state.is_playing else "Paused")

        track = state.track
        if not self.current_track or self.current_track.uri != track.uri:
            self.current_track = track
            self._update_track_labels(track)
            self._update_album_art(track.image_url)
        self._mark_queue_playing(track.uri)
        self._sync_puddletube_view()

        self.duration_ms = track.duration_ms
        max_value = self.duration_ms or 1
        self.ui.progressSlider.blockSignals(True)
        self.ui.progressSlider.setRange(0, max_value)
        self.ui.progressSlider.blockSignals(False)

        display_progress = state.progress_ms
        if self._pending_seek_position is not None:
            if abs(display_progress - self._pending_seek_position) <= SEEK_SYNC_TOLERANCE_MS:
                self._pending_seek_position = None
            else:
                display_progress = self._pending_seek_position

        if not self._user_scrubbing:
            clamped = max(0, min(max_value, display_progress))
            self.ui.progressSlider.blockSignals(True)
            self.ui.progressSlider.setValue(clamped)
            self.ui.progressSlider.blockSignals(False)
            self.ui.miniProgressBar.setRange(0, max_value)
            self.ui.miniProgressBar.setValue(clamped)
            self._update_time_indicators(clamped)

    def _update_track_labels(self, track: Track) -> None:
        self.ui.trackTitleLabel.setText(track.name)
        self.ui.artistLabel.setText(track.artist)
        self.ui.miniTrackLabel.setText(track.name)
        self.ui.miniArtistLabel.setText(track.artist)

    def _update_time_indicators(self, progress_ms: int) -> None:
        self.ui.currentTimeLabel.setText(self._format_time(progress_ms))
        remaining = max(0, (self.duration_ms or 0) - progress_ms)
        self.ui.remainingTimeLabel.setText(f"-{self._format_time(remaining)}")

    def _update_play_buttons(self, playing: bool) -> None:
        icon = self._icons["pause"] if playing else self._icons["play"]
        tooltip = "Pause" if playing else "Play"
        self.ui.playPauseButton.setIcon(icon)
        self.ui.playPauseButton.setIconSize(QtCore.QSize(32, 32))
        self.ui.playPauseButton.setToolTip(tooltip)

        self.ui.miniPlayPauseButton.setIcon(icon)
        self.ui.miniPlayPauseButton.setIconSize(QtCore.QSize(32, 32))
        self.ui.miniPlayPauseButton.setToolTip(tooltip)

    def _set_status(self, message: str) -> None:
        self.ui.connectionStatusLabel.setText(message)
        self.ui.miniStatusLabel.setText(message)

    def _mark_queue_playing(self, track_uri: Optional[str]) -> None:
        current_row = -1
        for index, widget in self.queue_widgets.items():
            match = (
                track_uri
                and index < len(self.queue)
                and self.queue[index].uri == track_uri
            )
            widget.set_playing(bool(match))
            if match:
                current_row = index
        if current_row >= 0:
            self.ui.queueList.setCurrentRow(current_row)

    # ------------------------------------------------------------------ Album art & icons
    def _cancel_album_request(self) -> None:
        if self._album_reply:
            self._album_reply.abort()
            self._album_reply.deleteLater()
            self._album_reply = None

    def _update_album_art(self, url: Optional[str]) -> None:
        self._cancel_album_request()
        if not url:
            self._apply_default_art()
            return

        request = QtNetwork.QNetworkRequest(QUrl(url))
        reply = self.network.get(request)
        reply.finished.connect(lambda r=reply: self._on_album_art_ready(r))
        self._album_reply = reply

    def _on_album_art_ready(self, reply: QtNetwork.QNetworkReply) -> None:
        reply.deleteLater()
        self._album_reply = None
        if reply.error() != QtNetwork.QNetworkReply.NetworkError.NoError:
            LOG.debug("Album art download failed: %s", reply.errorString())
            self._apply_default_art()
            return

        pixmap = QtGui.QPixmap()
        if pixmap.loadFromData(bytes(reply.readAll())):
            self.ui.albumArt.setPixmap(pixmap)
            mini = pixmap.scaled(
                self.ui.miniAlbumArt.size(),
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation,
            )
            self.ui.miniAlbumArt.setPixmap(mini)
        else:
            self._apply_default_art()

    def _apply_default_art(self) -> None:
        start = theme.css_to_qcolor(self.color_scheme["card_gradient_start"])
        end = theme.css_to_qcolor(self.color_scheme["card_gradient_end"])
        pixmap = QtGui.QPixmap(360, 360)
        pixmap.fill(QtCore.Qt.GlobalColor.transparent)
        painter = QtGui.QPainter(pixmap)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        gradient = QtGui.QLinearGradient(0, 0, 360, 360)
        gradient.setColorAt(0, start)
        gradient.setColorAt(1, end)
        painter.setBrush(gradient)
        painter.setPen(QtGui.QPen(QtGui.QColor(0, 0, 0, 90), 4))
        painter.drawRoundedRect(QtCore.QRectF(2, 2, 356, 356), 40, 40)
        painter.end()
        mini = pixmap.scaled(
            self.ui.miniAlbumArt.size(),
            Qt.AspectRatioMode.KeepAspectRatioByExpanding,
            Qt.TransformationMode.SmoothTransformation,
        )
        self.ui.albumArt.setPixmap(pixmap)
        self.ui.miniAlbumArt.setPixmap(mini)

    # ------------------------------------------------------------------ Queue thumbnails
    def _ensure_queue_icon(self, track: Track, index: int) -> None:
        if not track.image_url:
            return
        request = QtNetwork.QNetworkRequest(QUrl(track.image_url))
        reply = self.network.get(request)
        reply.finished.connect(lambda r=reply: self._on_queue_icon_ready(r))
        self._icon_requests[reply] = index

    def _cancel_icon_requests(self) -> None:
        for reply in list(self._icon_requests.keys()):
            reply.abort()
            reply.deleteLater()
        self._icon_requests.clear()

    def _on_queue_icon_ready(self, reply: QtNetwork.QNetworkReply) -> None:
        index = self._icon_requests.pop(reply, None)
        reply.deleteLater()
        if index is None:
            return
        if reply.error() != QtNetwork.QNetworkReply.NetworkError.NoError:
            LOG.debug("Queue icon download failed: %s", reply.errorString())
            return
        pixmap = QtGui.QPixmap()
        if not pixmap.loadFromData(bytes(reply.readAll())):
            return
        widget = self.queue_widgets.get(index)
        if widget:
            widget.set_art(pixmap)

    # ------------------------------------------------------------------ Formatting helpers
    @staticmethod
    def _format_time(milliseconds: int) -> str:
        seconds = max(0, int(milliseconds / 1000))
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        if hours:
            return f"{hours}:{minutes:02d}:{seconds:02d}"
        return f"{minutes}:{seconds:02d}"

    @staticmethod
    def _format_duration(milliseconds: int) -> str:
        return MiniPlayerWindow._format_time(milliseconds)

    # ------------------------------------------------------------------ Queue helpers
    def _advance_queue(self, step: int) -> None:
        if not self.queue:
            return

        current_index = self._current_queue_index()
        if current_index == -1:
            next_index = 0 if step > 0 else len(self.queue) - 1
        else:
            next_index = (current_index + step) % len(self.queue)

        self.ui.queueList.setCurrentRow(next_index)
        self._play_track(self.queue[next_index])

    def _current_queue_index(self) -> int:
        if not self.current_track:
            return -1
        for idx, track in enumerate(self.queue):
            if track.uri == self.current_track.uri:
                return idx
        return -1

    # ------------------------------------------------------------------ Player callbacks
    def _on_media_status_changed(self, status: QMediaPlayer.MediaStatus) -> None:
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            self._advance_queue(1)
        elif status == QMediaPlayer.MediaStatus.InvalidMedia:
            self._set_status("Playback error")

    def _on_player_error(self, error: QMediaPlayer.Error, message: str) -> None:  # pragma: no cover - Qt signal
        if error == QMediaPlayer.Error.NoError:
            return
        LOG.error("QMediaPlayer error: %s", message)
        self._set_status("Playback error")

    def _on_duration_changed(self, duration_ms: int) -> None:
        if self.current_track and duration_ms > 0:
            self.current_track.duration_ms = duration_ms
