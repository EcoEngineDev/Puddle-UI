from __future__ import annotations

from typing import Optional

try:
    from PyQt5.QtWidgets import QWidget
    from PyQt5.QtCore import QUrl
except Exception:  # pragma: no cover - typing fallback in non-Qt envs
    QWidget = object  # type: ignore
    class QUrl:  # type: ignore
        def __init__(self, *_):
            pass


class WebEmbedManager:
    """Tracks which web-embedded widget is currently open.

    Exactly one non-map web embed can be visible at a time. The maps widget
    is not tracked here and can be shown independently.
    """

    def __init__(self) -> None:
        self._current_name: Optional[str] = None
        self._current_widget: Optional[QWidget] = None

    def current(self) -> Optional[str]:
        return self._current_name

    def is_open(self, name: str) -> bool:
        return self._current_name == name

    def close_current(self) -> None:
        if self._current_widget is not None:
            w = self._current_widget
            try:
                web_view = getattr(w, 'web_view', None)
                if web_view is not None:
                    try:
                        page = web_view.page()
                        if hasattr(page, 'setAudioMuted'):
                            page.setAudioMuted(True)
                        if hasattr(page, 'triggerAction'):
                            from PyQt5.QtWebEngineWidgets import QWebEnginePage
                            page.triggerAction(QWebEnginePage.Stop)
                    except Exception:
                        pass
                    try:
                        if hasattr(web_view, 'setUrl'):
                            web_view.setUrl(QUrl('about:blank'))
                        elif hasattr(web_view, 'setHtml'):
                            web_view.setHtml('<html><body></body></html>')
                    except Exception:
                        pass
                w.hide()
            except Exception:
                pass
        self._current_name = None
        self._current_widget = None

    def open(self, name: str, widget: QWidget) -> None:
        """Set the given widget as the only open non-map web embed.

        Hides any previously open widget before showing the new one.
        """
        if widget is None:
            return
        if self._current_widget is widget and self._current_name == name:
            try:
                widget.show()
            except Exception:
                pass
            return

        self.close_current()

        try:
            web_view = getattr(widget, 'web_view', None)
            if web_view is not None:
                try:
                    page = web_view.page()
                    if hasattr(page, 'setAudioMuted'):
                        page.setAudioMuted(False)
                except Exception:
                    pass
                try:
                    current_url = ''
                    if hasattr(web_view, 'url'):
                        u = web_view.url()
                        if hasattr(u, 'toString'):
                            current_url = u.toString()
                    if not current_url or current_url == 'about:blank':
                        default = getattr(widget, 'default_url', None) or getattr(widget, 'url', None)
                        if default and hasattr(web_view, 'setUrl'):
                            web_view.setUrl(QUrl(default))
                except Exception:
                    pass
            widget.show()
        except Exception:
            pass

        self._current_name = name
        self._current_widget = widget


web_embed_manager = WebEmbedManager()
