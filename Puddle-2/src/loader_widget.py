"""Shared loading indicator helpers for Puddle 2 views."""

from __future__ import annotations

from typing import Optional

from PyQt6 import QtCore, QtGui, QtWidgets

try:  # pragma: no cover - optional dependency
    from Custom_Widgets.LoadingIndicators.QCustomPerlinLoader import QCustomPerlinLoader
except ImportError:  # pragma: no cover - optional dependency
    QCustomPerlinLoader = None  # type: ignore[assignment]


class _ArcSpinner(QtWidgets.QWidget):
    """Fallback arc spinner used when the Perlin loader is unavailable."""

    def __init__(self, parent: Optional[QtWidgets.QWidget] = None) -> None:
        super().__init__(parent)
        self._pen_width = 4
        self._color = QtGui.QColor("#ffffff")
        self._angle = 0.0
        self._speed = 6.0
        self._timer = QtCore.QTimer(self)
        self._timer.setInterval(16)
        self._timer.timeout.connect(self._advance)
        self.setMinimumSize(32, 32)

    def sizeHint(self) -> QtCore.QSize:  # noqa: D401
        return QtCore.QSize(48, 48)

    def set_color(self, color: QtGui.QColor) -> None:
        self._color = color
        self.update()

    def start(self) -> None:
        if not self._timer.isActive():
            self._timer.start()

    def stop(self) -> None:
        if self._timer.isActive():
            self._timer.stop()
        self.update()

    def paintEvent(self, event: QtGui.QPaintEvent) -> None:  # noqa: N802
        del event
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        pen = QtGui.QPen(self._color, self._pen_width)
        pen.setCapStyle(QtCore.Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        inset = self._pen_width
        rect = QtCore.QRectF(
            inset,
            inset,
            self.width() - inset * 2,
            self.height() - inset * 2,
        )
        start_angle = int(self._angle * 16)
        span_angle = -240 * 16
        painter.drawArc(rect, start_angle, span_angle)
        painter.end()

    def _advance(self) -> None:
        self._angle = (self._angle + self._speed) % 360
        self.update()


if QCustomPerlinLoader is not None:

    class _PerlinLoaderWrapper(QCustomPerlinLoader):
        """Adapter that exposes start/stop hooks for the Perlin loader."""

        def start(self) -> None:  # type: ignore[override]
            animation = getattr(self, "animation", None)
            if animation is not None and animation.state() != QtCore.QAbstractAnimation.State.Running:
                animation.start()

        def stop(self) -> None:  # type: ignore[override]
            animation = getattr(self, "animation", None)
            if animation is not None:
                animation.stop()
            self.update()

else:  # pragma: no cover - optional dependency missing
    _PerlinLoaderWrapper = None  # type: ignore[assignment]


class LoaderWidget(QtWidgets.QFrame):
    """Unified loading widget that favours the Perlin loader when available."""

    def __init__(
        self,
        *,
        size: QtCore.QSize = QtCore.QSize(220, 220),
        message: str = "LOADING…",
        parent: Optional[QtWidgets.QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("puddleLoaderWidget")
        self.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        if _PerlinLoaderWrapper is not None:
            self._loader = _PerlinLoaderWrapper(
                parent=self,
                size=size,
                message=message,
                color=QtGui.QColor("#ffffff"),
                backgroundColor=QtGui.QColor(0, 0, 0, 0),
            )
        else:
            self._loader = _ArcSpinner(self)

        layout.addWidget(self._loader, alignment=QtCore.Qt.AlignmentFlag.AlignCenter)
        self._message = message

    def start(self) -> None:
        if hasattr(self._loader, "start"):
            self._loader.start()

    def stop(self) -> None:
        if hasattr(self._loader, "stop"):
            self._loader.stop()

    def set_message(self, text: str) -> None:
        self._message = text
        if hasattr(self._loader, "message"):
            self._loader.message = text
            self._loader.update()

    def set_palette(
        self,
        *,
        primary: QtGui.QColor,
        primary_hover: QtGui.QColor,
        primary_active: QtGui.QColor,
        text: QtGui.QColor,
    ) -> None:
        if isinstance(self._loader, _ArcSpinner):
            self._loader.set_color(primary)
        elif hasattr(self._loader, "circleColor1"):
            self._loader.circleColor1 = primary
            self._loader.circleColor2 = primary_hover
            self._loader.circleColor3 = primary_active
            self._loader.color = text
            self._loader.update()
