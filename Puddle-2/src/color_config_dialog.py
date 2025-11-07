"""Dialog for editing the theme colour palette."""

from __future__ import annotations

from typing import Dict

from PyQt6 import QtCore, QtGui, QtWidgets

from . import theme


class ColorConfigDialog(QtWidgets.QDialog):
    """Allow the user to edit the core colours used by the UI."""

    def __init__(self, colors: Dict[str, str], parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Theme Colours")
        self.setModal(True)
        self.resize(420, 380)

        self._colors = theme.ensure_all_keys(colors)
        self._samples: Dict[str, QtWidgets.QLabel] = {}
        self._alpha_support: Dict[str, bool] = {}

        layout = QtWidgets.QVBoxLayout(self)
        description = QtWidgets.QLabel(
            "Adjust the core palette used across the UI. Colours are saved to "
            "`json_styles/style.json` and re-applied immediately."
        )
        description.setWordWrap(True)
        layout.addWidget(description)

        grid = QtWidgets.QGridLayout()
        grid.setColumnStretch(2, 1)
        for row, (key, label, allow_alpha) in enumerate(theme.COLOR_ROLES):
            sample = QtWidgets.QLabel()
            sample.setFixedSize(64, 24)
            sample.setFrameShape(QtWidgets.QFrame.Shape.Panel)
            sample.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
            sample.setStyleSheet(self._sample_stylesheet(self._colors[key]))
            self._samples[key] = sample
            self._alpha_support[key] = allow_alpha

            button = QtWidgets.QPushButton("Change")
            button.clicked.connect(lambda _=False, k=key: self._select_colour(k))

            grid.addWidget(QtWidgets.QLabel(label), row, 0)
            grid.addWidget(sample, row, 1)
            grid.addWidget(button, row, 2)

        layout.addLayout(grid)
        self._sync_primary_variants(update_samples=True)
        self._sync_tube_variants(update_samples=True)
        layout.addStretch()

        button_box = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.StandardButton.Cancel
            | QtWidgets.QDialogButtonBox.StandardButton.Save
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    @property
    def colors(self) -> Dict[str, str]:
        return self._colors

    def _sample_stylesheet(self, color: str) -> str:
        return (
            f"background: {color}; border-radius: 6px; border: 1px solid rgba(0,0,0,0.25);"
        )

    def _select_colour(self, key: str) -> None:
        initial = theme.css_to_qcolor(self._colors[key])
        if self._alpha_support.get(key, False):
            options = QtWidgets.QColorDialog.ColorDialogOption.ShowAlphaChannel
        else:
            options = QtWidgets.QColorDialog.ColorDialogOption(0)
        color = QtWidgets.QColorDialog.getColor(
            initial, self, f"Select colour for {key}", options=options
        )
        if not color.isValid():
            return
        self._colors[key] = theme.qcolor_to_css(color, self._alpha_support.get(key, False))
        self._samples[key].setStyleSheet(self._sample_stylesheet(self._colors[key]))
        if key == "primary":
            self._sync_primary_variants(update_samples=True)
        elif key == "tube_primary":
            self._sync_tube_variants(update_samples=True)

    def _sync_primary_variants(self, update_samples: bool = False) -> None:
        primary = theme.css_to_qcolor(self._colors["primary"])
        hover = primary.lighter(112)
        active = primary.darker(112)
        self._colors["primary_hover"] = theme.qcolor_to_css(hover, False)
        self._colors["primary_active"] = theme.qcolor_to_css(active, False)
        if update_samples:
            for key in ("primary_hover", "primary_active"):
                sample = self._samples.get(key)
                if sample is not None:
                    sample.setStyleSheet(self._sample_stylesheet(self._colors[key]))

    def _sync_tube_variants(self, update_samples: bool = False) -> None:
        tube_primary = theme.css_to_qcolor(self._colors["tube_primary"])
        hover = tube_primary.lighter(112)
        active = tube_primary.darker(112)
        self._colors["tube_primary_hover"] = theme.qcolor_to_css(hover, False)
        self._colors["tube_primary_active"] = theme.qcolor_to_css(active, False)
        if update_samples:
            for key in ("tube_primary_hover", "tube_primary_active"):
                sample = self._samples.get(key)
                if sample is not None:
                    sample.setStyleSheet(self._sample_stylesheet(self._colors[key]))
