"""Theme management and stylesheet generation for the Puddle 2 UI."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Iterable, Tuple

from PyQt6 import QtGui, QtWidgets

THEME_PATH = Path(__file__).resolve().parent.parent / "json_styles" / "style.json"

COLOR_ROLES = [
    ("background", "Window Background", False),
    ("surface_gradient_start", "Backdrop Gradient Start", False),
    ("surface_gradient_mid", "Backdrop Gradient Mid", False),
    ("surface_gradient_end", "Backdrop Gradient End", False),
    ("card_gradient_start", "Card Gradient Start", False),
    ("card_gradient_mid", "Card Gradient Mid", False),
    ("card_gradient_end", "Card Gradient End", False),
    ("mini_gradient_start", "Mini Player Gradient Start", False),
    ("mini_gradient_mid", "Mini Player Gradient Mid", False),
    ("mini_gradient_end", "Mini Player Gradient End", False),
    ("primary", "Primary Accent", False),
    ("status_text", "Status Text", False),
    ("text_primary", "Primary Text", False),
    ("text_muted", "Muted Text", True),
    ("text_soft", "Soft Text", True),
    ("tube_primary", "PuddleTube Primary Accent", False),
    ("tube_surface", "PuddleTube Surface", False),
    ("tube_surface_alt", "PuddleTube Secondary Surface", False),
]

DEFAULT_SCHEME: Dict[str, str] = {
    "background": "#0d0f14",
    "surface_gradient_start": "#111622",
    "surface_gradient_mid": "#151a27",
    "surface_gradient_end": "#10141d",
    "card_gradient_start": "#141821",
    "card_gradient_mid": "#1a1f2c",
    "card_gradient_end": "#10141d",
    "mini_gradient_start": "#1e1627",
    "mini_gradient_mid": "#2a1f3a",
    "mini_gradient_end": "#181221",
    "primary": "#ff7f32",
    "primary_hover": "#ff944f",
    "primary_active": "#f0701d",
    "status_text": "#ffb877",
    "text_primary": "#ffffff",
    "text_muted": "rgba(255, 231, 208, 0.75)",
    "text_soft": "rgba(255, 231, 208, 0.6)",
    "tube_primary": "#ff375f",
    "tube_primary_hover": "#ff5173",
    "tube_primary_active": "#e22d55",
    "tube_surface": "#18121f",
    "tube_surface_alt": "#211628",
}


def load_scheme() -> Dict[str, str]:
    """Load the colour scheme from disk, falling back to DEFAULT_SCHEME."""
    scheme = DEFAULT_SCHEME.copy()
    if THEME_PATH.exists():
        try:
            data = json.loads(THEME_PATH.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return scheme

        # Support either {"colors": {...}} or a raw dict.
        if isinstance(data, dict):
            colors = data.get("colors") if "colors" in data else data
            if isinstance(colors, dict):
                for key, value in colors.items():
                    if isinstance(key, str) and isinstance(value, str):
                        scheme[key] = value
    return ensure_all_keys(scheme)


def save_scheme(scheme: Dict[str, str]) -> None:
    """Persist the colour scheme to disk."""
    scheme = ensure_all_keys(scheme)
    payload_scheme = {k: v for k, v in scheme.items() if k not in {"primary_hover", "primary_active"}}
    payload = {"name": "custom", "colors": payload_scheme}
    THEME_PATH.parent.mkdir(parents=True, exist_ok=True)
    THEME_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def ensure_all_keys(scheme: Dict[str, str]) -> Dict[str, str]:
    """Ensure every expected key exists."""
    merged = DEFAULT_SCHEME.copy()
    merged.update({k: v for k, v in scheme.items() if v})
    primary = css_to_qcolor(merged["primary"])
    merged["primary_hover"] = qcolor_to_css(primary.lighter(112), False)
    merged["primary_active"] = qcolor_to_css(primary.darker(112), False)
    tube_primary = css_to_qcolor(merged["tube_primary"])
    merged["tube_primary_hover"] = qcolor_to_css(tube_primary.lighter(112), False)
    merged["tube_primary_active"] = qcolor_to_css(tube_primary.darker(112), False)
    return merged


def puddletube_palette(scheme: Dict[str, str]) -> Dict[str, str]:
    """Return colours dedicated to the PuddleTube view."""
    merged = ensure_all_keys(scheme)
    return {
        "primary": merged["tube_primary"],
        "primary_hover": merged["tube_primary_hover"],
        "primary_active": merged["tube_primary_active"],
        "surface": merged["tube_surface"],
        "surface_alt": merged["tube_surface_alt"],
        "text_primary": merged["text_primary"],
        "text_muted": merged["text_muted"],
    }


# Backwards compatibility for older modules referencing the former helper.
qttube_palette = puddletube_palette


def css_to_qcolor(value: str) -> QtGui.QColor:
    """Convert a CSS colour string (#rrggbb or rgba) to QColor."""
    value = value.strip()
    if value.startswith("#"):
        return QtGui.QColor(value)
    if value.startswith("rgba"):
        inside = value[value.find("(") + 1 : value.rfind(")")]
        parts = [x.strip() for x in inside.split(",")]
        if len(parts) == 4:
            r, g, b = (int(float(parts[i])) for i in range(3))
            alpha = float(parts[3])
            a = int(max(0, min(1, alpha)) * 255)
            return QtGui.QColor(r, g, b, a)
    if value.startswith("rgb"):
        inside = value[value.find("(") + 1 : value.rfind(")")]
        parts = [x.strip() for x in inside.split(",")]
        if len(parts) == 3:
            r, g, b = (int(float(parts[i])) for i in range(3))
            return QtGui.QColor(r, g, b)
    return QtGui.QColor(value)


def qcolor_to_css(color: QtGui.QColor, allow_alpha: bool) -> str:
    """Convert QColor to a CSS colour string."""
    if allow_alpha:
        return rgba_string(color.red(), color.green(), color.blue(), color.alpha() / 255.0)
    if color.alpha() < 255:
        return color.name(QColor.NameFormat.HexArgb)
    return color.name(QtGui.QColor.NameFormat.HexRgb)


def rgba_string(r: int, g: int, b: int, alpha: float) -> str:
    alpha = max(0.0, min(1.0, alpha))
    return f"rgba({r}, {g}, {b}, {alpha:.2f})"


def derived_soft_colours(primary: QtGui.QColor) -> Tuple[str, str, str]:
    """Produce translucent variants of the primary colour for button states."""
    return (
        rgba_string(primary.red(), primary.green(), primary.blue(), 0.18),
        rgba_string(primary.red(), primary.green(), primary.blue(), 0.28),
        rgba_string(primary.red(), primary.green(), primary.blue(), 0.38),
    )


def queue_highlight(primary: QtGui.QColor) -> Tuple[str, str]:
    """Return colours used when the queue item is marked as playing."""
    title = rgba_string(primary.red(), primary.green(), primary.blue(), 0.9)
    meta = rgba_string(primary.red(), primary.green(), primary.blue(), 0.65)
    return title, meta


def build_stylesheet(scheme: Dict[str, str]) -> str:
    """Generate the application stylesheet based on the current scheme."""
    scheme = ensure_all_keys(scheme)
    primary_qcolor = css_to_qcolor(scheme["primary"])
    soft, soft_hover, soft_pressed = derived_soft_colours(primary_qcolor)
    queue_title, queue_meta = queue_highlight(primary_qcolor)
    surface_border = rgba_string(primary_qcolor.red(), primary_qcolor.green(), primary_qcolor.blue(), 0.18)
    card_border = rgba_string(primary_qcolor.red(), primary_qcolor.green(), primary_qcolor.blue(), 0.10)
    mini_border = rgba_string(primary_qcolor.red(), primary_qcolor.green(), primary_qcolor.blue(), 0.22)

    return f"""
QMainWindow {{
  background: {scheme["background"]};
  color: {scheme["text_primary"]};
}}

QWidget#centralwidget {{
  background: {scheme["background"]};
}}

QFrame#backgroundFrame {{
  background: qlineargradient(
    x1: 0, y1: 0, x2: 1, y2: 1,
    stop: 0 {scheme["surface_gradient_start"]},
    stop: 0.5 {scheme["surface_gradient_mid"]},
    stop: 1 {scheme["surface_gradient_end"]}
  );
  border-radius: 32px;
  border: 1px solid {surface_border};
}}

QFrame#mainCard {{
  border-radius: 24px;
  background: qlineargradient(
    x1: 0, y1: 0, x2: 1, y2: 1,
    stop: 0 {scheme["card_gradient_start"]},
    stop: 0.5 {scheme["card_gradient_mid"]},
    stop: 1 {scheme["card_gradient_end"]}
  );
  border: 1px solid {card_border};
}}

QWidget#miniPage {{
  border-radius: 20px;
  background: qlineargradient(
    x1: 0, y1: 0, x2: 1, y2: 1,
    stop: 0 {scheme["mini_gradient_start"]},
    stop: 0.45 {scheme["mini_gradient_mid"]},
    stop: 1 {scheme["mini_gradient_end"]}
  );
  border: 1px solid {mini_border};
}}

QWidget#expandedPage {{
  border-radius: 24px;
  background: qlineargradient(
    x1: 0, y1: 0, x2: 1, y2: 1,
    stop: 0 {scheme["mini_gradient_start"]},
    stop: 0.45 {scheme["mini_gradient_mid"]},
    stop: 1 {scheme["mini_gradient_end"]}
  );
  border: 1px solid {mini_border};
}}

QLabel#miniStatusLabel,
QLabel#connectionStatusLabel {{
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: {scheme["status_text"]};
}}

QLabel#miniTrackLabel,
QLabel#trackTitleLabel {{
  font-size: 22px;
  font-weight: 700;
  color: {scheme["text_primary"]};
}}

QLabel#miniArtistLabel,
QLabel#artistLabel {{
  font-size: 15px;
  color: {scheme["text_muted"]};
}}

QLabel#currentTimeLabel,
QLabel#remainingTimeLabel {{
  font-size: 13px;
  color: {scheme["text_soft"]};
}}

QProgressBar#miniProgressBar {{
  background: {rgba_string(primary_qcolor.red(), primary_qcolor.green(), primary_qcolor.blue(), 0.15)};
  border-radius: 6px;
  padding: 0;
  height: 6px;
}}

QProgressBar#miniProgressBar::chunk {{
  background: {scheme["primary"]};
  border-radius: 6px;
}}

QSlider#progressSlider::groove:horizontal,
QSlider#volumeSlider::groove:horizontal {{
  height: 6px;
  border-radius: 3px;
  background: {rgba_string(primary_qcolor.red(), primary_qcolor.green(), primary_qcolor.blue(), 0.18)};
}}

QSlider#progressSlider::handle:horizontal,
QSlider#volumeSlider::handle:horizontal {{
  width: 16px;
  height: 16px;
  margin: -5px 0;
  border-radius: 8px;
  background: {scheme["primary_hover"]};
  border: 1px solid {rgba_string(0, 0, 0, 0.2)};
}}

QSlider#progressSlider::sub-page:horizontal {{
  background: {scheme["primary"]};
  border-radius: 3px;
}}

QSlider#volumeSlider::sub-page:horizontal {{
  background: {scheme["primary_hover"]};
  border-radius: 3px;
}}

QToolButton,
QPushButton {{
  background: {soft};
  border-radius: 18px;
  border: 1px solid {rgba_string(primary_qcolor.red(), primary_qcolor.green(), primary_qcolor.blue(), 0.12)};
  padding: 12px;
}}

QToolButton:hover,
QPushButton:hover {{
  background: {soft_hover};
}}

QToolButton:pressed,
QPushButton:pressed {{
  background: {soft_pressed};
}}

QToolButton#miniPlayPauseButton,
QToolButton#playPauseButton {{
  border-radius: 28px;
  padding: 18px;
  background: {scheme["primary"]};
  border: 1px solid {rgba_string(0, 0, 0, 0.15)};
}}

QToolButton#miniPlayPauseButton:hover,
QToolButton#playPauseButton:hover {{
  background: {scheme["primary_hover"]};
}}

QToolButton#miniPlayPauseButton:pressed,
QToolButton#playPauseButton:pressed {{
  background: {scheme["primary_active"]};
}}

QToolButton#miniExpandButton,
QToolButton#collapseButton,
QToolButton#themeButton {{
  border-radius: 16px;
  padding: 10px;
  background: {soft};
  border: 1px solid {rgba_string(primary_qcolor.red(), primary_qcolor.green(), primary_qcolor.blue(), 0.1)};
}}

QToolButton#miniExpandButton:hover,
QToolButton#collapseButton:hover,
QToolButton#themeButton:hover {{
  background: {soft_hover};
}}

QToolButton#miniExpandButton:pressed,
QToolButton#collapseButton:pressed,
QToolButton#themeButton:pressed {{
  background: {soft_pressed};
}}

QLineEdit#searchField {{
  padding: 12px 16px;
  border-radius: 14px;
  border: 1px solid {rgba_string(primary_qcolor.red(), primary_qcolor.green(), primary_qcolor.blue(), 0.2)};
  background: rgba(14, 18, 26, 0.75);
  color: {scheme["text_primary"]};
  font-size: 16px;
}}

QLineEdit#searchField:focus {{
  border: 1px solid {scheme["primary"]};
  background: rgba(14, 18, 26, 0.95);
}}

QPushButton#searchButton {{
  padding: 12px 20px;
  border-radius: 16px;
  background: {scheme["primary"]};
  color: {scheme["background"]};
  font-weight: 600;
}}

QPushButton#searchButton:hover {{
  background: {scheme["primary_hover"]};
}}

QPushButton#searchButton:pressed {{
  background: {scheme["primary_active"]};
}}

QListWidget#queueList {{
  border: none;
  border-radius: 18px;
  background: transparent;
  color: {scheme["text_primary"]};
  padding: 12px;
  font-size: 15px;
}}

QListWidget#queueList::item {{
  margin: 6px 0;
  padding: 12px;
  border-radius: 16px;
  background: transparent;
  color: {scheme["text_muted"]};
}}

QWidget#queueItem {{
  border-radius: 22px;
  border: 1px solid {rgba_string(primary_qcolor.red(), primary_qcolor.green(), primary_qcolor.blue(), 0.18)};
  background: qlineargradient(
    x1: 0, y1: 0, x2: 1, y2: 1,
    stop: 0 {scheme["card_gradient_start"]},
    stop: 0.6 {scheme["card_gradient_mid"]},
    stop: 1 {scheme["card_gradient_end"]}
  );
  padding: 4px;
}}

QWidget#queueItem QLabel#queueTitle {{
  font-size: 17px;
  font-weight: 600;
  color: {scheme["text_primary"]};
}}

QWidget#queueItem QLabel#queueMeta {{
  font-size: 13px;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  color: {scheme["text_muted"]};
}}

QWidget#queueItem QLabel#queueAlbum {{
  font-size: 13px;
  color: {scheme["text_soft"]};
}}

QLabel#queueArt {{
  border-radius: 18px;
  background: {rgba_string(0, 0, 0, 0.1)};
}}

QWidget#queueItem[isPlaying="true"] QLabel#queueTitle {{
  color: {queue_title};
}}

QWidget#queueItem[isPlaying="true"] QLabel#queueMeta {{
  color: {queue_meta};
}}

QWidget#queueItem[isPlaying="true"] {{
  border: 1px solid {scheme["primary"]};
  background: {rgba_string(primary_qcolor.red(), primary_qcolor.green(), primary_qcolor.blue(), 0.22)};
}}

QScrollBar:vertical {{
  background: transparent;
  width: 10px;
  margin: 12px 0 12px 0;
}}

QScrollBar::handle:vertical {{
  background: {soft_hover};
  border-radius: 5px;
}}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {{
  height: 0;
}}

QScrollBar:horizontal {{
  background: transparent;
  height: 10px;
  margin: 0 12px 0 12px;
}}

QScrollBar::handle:horizontal {{
  background: {soft_hover};
  border-radius: 5px;
}}

QScrollBar::add-line:horizontal,
QScrollBar::sub-line:horizontal {{
  width: 0;
}}
""".strip()


def apply(scheme: Dict[str, str]) -> None:
    """Apply the stylesheet to the QApplication."""
    stylesheet = build_stylesheet(scheme)
    QtWidgets.QApplication.instance().setStyleSheet(stylesheet)
