import os
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QFrame, QPushButton, QLabel
from PyQt5.QtCore import Qt, QSize, QTimer, QRectF
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QColor
from PyQt5.QtSvg import QSvgRenderer
from src.style.mini_player import (
    mini_player_container_style,
    mini_player_title_style,
    mini_player_separator_style,
    mini_player_button_style,
)


class YouTubeMusicMiniPlayer(QWidget):

    def __init__(self, yt_music_widget, parent=None):
        super().__init__(parent)
        self.yt_music_widget = yt_music_widget
        self._build_ui()
        self._wire_controls()
        self._start_status_timer()

    def _build_ui(self):
        container = QFrame(self)
        container.setStyleSheet(mini_player_container_style())

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.addWidget(container)

        layout = QVBoxLayout(container)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(6)

        self.lbl_now_playing = QLabel("—", container)
        self.lbl_now_playing.setStyleSheet(mini_player_title_style())
        self.lbl_now_playing.setWordWrap(False)
        self.lbl_now_playing.setMinimumWidth(100)
        self.lbl_now_playing.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        layout.addWidget(self.lbl_now_playing)

        sep = QFrame(container)
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet(mini_player_separator_style())
        layout.addWidget(sep)

        controls = QHBoxLayout()
        controls.setContentsMargins(0, 0, 0, 0)
        controls.setSpacing(10)

        self.btn_prev = QPushButton("", container)
        self.btn_playpause = QPushButton("", container)
        self.btn_next = QPushButton("", container)
        for btn in (self.btn_prev, self.btn_playpause, self.btn_next):
            btn.setFixedSize(QSize(36, 36))
            btn.setStyleSheet(mini_player_button_style())
            btn.setIconSize(QSize(20, 20))

        controls.addStretch(1)
        controls.addWidget(self.btn_prev)
        controls.addWidget(self.btn_playpause)
        controls.addWidget(self.btn_next)
        controls.addStretch(1)
        layout.addLayout(controls)

        self._load_icons()
        self.btn_prev.setIcon(self.icon_prev)
        self.btn_next.setIcon(self.icon_next)
        self.btn_playpause.setIcon(self.icon_play)

    def _wire_controls(self):
        self.btn_prev.clicked.connect(self.youtube_music_prev)
        self.btn_playpause.clicked.connect(self.youtube_music_toggle)
        self.btn_next.clicked.connect(self.youtube_music_next)

    def _start_status_timer(self):
        self.status_timer = QTimer(self)
        self.status_timer.setInterval(1500)
        self.status_timer.timeout.connect(self.update_youtube_music_status)
        self.status_timer.start()

    def _ytmusic_run_js(self, script: str, callback=None):
        try:
            page = self.yt_music_widget.web_view.page()
            if callback:
                page.runJavaScript(script, callback)
            else:
                page.runJavaScript(script)
        except Exception as e:
            print(f"YouTube Music JS error: {e}")

    def youtube_music_prev(self):
        js = (
            "(function(){\n"
            "  function api(){\n"
            "    var app=document.querySelector('ytmusic-app');\n"
            "    return app && (app.playerApi || app.playerApi_);\n"
            "  }\n"
            "  var p=api();\n"
            "  if(p && p.previousTrack){ p.previousTrack(); return 'api'; }\n"
            "  var btn = document.querySelector('ytmusic-player-bar #previous-button') ||\n"
            "            document.querySelector('#left-controls #previous-button');\n"
            "  if(btn){ btn.click(); return 'btn'; }\n"
            "  // fallback to keyboard\n"
            "  var e=new KeyboardEvent('keydown',{key:'P',shiftKey:true,bubbles:true,cancelable:true});\n"
            "  document.body.dispatchEvent(e);\n"
            "  return 'kbd';\n"
            "})()"
        )
        self._ytmusic_run_js(js)

    def youtube_music_next(self):
        js = (
            "(function(){\n"
            "  function api(){\n"
            "    var app=document.querySelector('ytmusic-app');\n"
            "    return app && (app.playerApi || app.playerApi_);\n"
            "  }\n"
            "  var p=api();\n"
            "  if(p && p.nextTrack){ p.nextTrack(); return 'api'; }\n"
            "  var btn = document.querySelector('ytmusic-player-bar #next-button') ||\n"
            "            document.querySelector('#left-controls #next-button');\n"
            "  if(btn){ btn.click(); return 'btn'; }\n"
            "  // fallback to keyboard\n"
            "  var e=new KeyboardEvent('keydown',{key:'N',shiftKey:true,bubbles:true,cancelable:true});\n"
            "  document.body.dispatchEvent(e);\n"
            "  return 'kbd';\n"
            "})()"
        )
        self._ytmusic_run_js(js)

    def youtube_music_toggle(self):
        js = (
            "(function(){\n"
            "  function api(){\n"
            "    var app=document.querySelector('ytmusic-app');\n"
            "    return app && (app.playerApi || app.playerApi_);\n"
            "  }\n"
            "  var p=api();\n"
            "  if(p && p.playPause){ p.playPause(); return 'api'; }\n"
            "  var btn = document.querySelector('ytmusic-player-bar #play-pause-button') ||\n"
            "            document.querySelector('#left-controls #play-pause-button');\n"
            "  if(btn){ btn.click(); return 'btn'; }\n"
            "  // fallback to keyboard\n"
            "  var e=new KeyboardEvent('keydown',{key:' ',bubbles:true,cancelable:true});\n"
            "  document.body.dispatchEvent(e);\n"
            "  return 'kbd';\n"
            "})()"
        )
        self._ytmusic_run_js(js)

    def update_youtube_music_status(self):
        js = (
            "(function(){\n"
            "  function getTitle(){\n"
            "    var bar=document.querySelector('ytmusic-player-bar');\n"
            "    var tEl = (bar && (bar.querySelector('.title') || bar.querySelector('#song-title'))) ||\n"
            "              document.querySelector('ytmusic-player-page #header .title');\n"
            "    var t = tEl ? tEl.textContent.trim() : (document.title || '').replace(/ - You\\u200b?Tube Music$/, '');\n"
            "    return t;\n"
            "  }\n"
            "  function getState(){\n"
            "    var btn = document.querySelector('ytmusic-player-bar #play-pause-button') ||\n"
            "              document.querySelector('#left-controls #play-pause-button') ||\n"
            "              document.querySelector('tp-yt-paper-icon-button#play-pause-button');\n"
            "    if(!btn) return null;\n"
            "    var t = btn.getAttribute('title') || btn.getAttribute('aria-label') || '';\n"
            "    return (/pause/i.test(t)) ? 'playing' : 'paused';\n"
            "  }\n"
            "  return {title:getTitle(), state:getState()};\n"
            "})()"
        )

        def _apply(status):
            try:
                title = ''
                state = 'paused'
                if isinstance(status, dict):
                    title = (status.get('title') or '').strip()
                    state = status.get('state') or 'paused'
                else:
                    title = (status or '').strip()

                if title.endswith(' - YouTube Music'):
                    title = title[:-18]
                if not title:
                    title = '—'
                self.lbl_now_playing.setText(title)

                self.btn_playpause.setIcon(self.icon_pause if state == 'playing' else self.icon_play)
            except Exception:
                pass

        self._ytmusic_run_js(js, _apply)


    def _svg_icon(self, path: str, size: int = 20) -> QIcon:
        mask = QPixmap(size, size)
        mask.fill(Qt.transparent)
        renderer = QSvgRenderer(path)
        p = QPainter(mask)
        try:
            p.setRenderHint(QPainter.Antialiasing)
            renderer.render(p, QRectF(0, 0, size, size))
        finally:
            p.end()

        colored = QPixmap(size, size)
        colored.fill(Qt.transparent)
        p = QPainter(colored)
        try:
            p.fillRect(0, 0, size, size, QColor(255, 255, 255))
            p.setCompositionMode(QPainter.CompositionMode_DestinationIn)
            p.drawPixmap(0, 0, mask)
        finally:
            p.end()
        return QIcon(colored)

    def _load_icons(self):
        base_dir = os.path.dirname(os.path.dirname(__file__))
        media_dir = os.path.join(base_dir, 'Media')
        self.icon_prev = self._svg_icon(os.path.join(media_dir, 'previous.svg'))
        self.icon_next = self._svg_icon(os.path.join(media_dir, 'next.svg'))
        self.icon_play = self._svg_icon(os.path.join(media_dir, 'playing.svg'))
        self.icon_pause = self._svg_icon(os.path.join(media_dir, 'pause.svg'))
