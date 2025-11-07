"""Application bootstrap for the redesigned Puddle 2 UI."""

from __future__ import annotations

import logging
import sys

from PyQt6 import QtCore, QtWidgets

from .mini_player import MiniPlayerWindow


def build_main_window() -> QtWidgets.QMainWindow:
    """Instantiate the main window and apply the designer UI."""
    window = MiniPlayerWindow()
    return window


def run() -> None:
    """Start the Qt application with the main window."""
    logging.basicConfig(
        level=logging.DEBUG,
        format="Puddle2 [%(levelname)s] %(name)s: %(message)s",
    )

    QtWidgets.QApplication.setAttribute(
        QtCore.Qt.ApplicationAttribute.AA_UseStyleSheetPropagationInWidgetStyles, True
    )

    app = QtWidgets.QApplication(sys.argv)
    window = build_main_window()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    run()
