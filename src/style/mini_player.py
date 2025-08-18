from . import theme


def mini_player_container_style() -> str:
    return (
        f"background:{theme.COLOR_PANEL};"
        f"border:2px solid {theme.COLOR_PANEL_BORDER};"
        f"border-radius:10px;"
    )


def mini_player_title_style() -> str:
    return (
        f"color:{theme.COLOR_TEXT};font-weight:600;"
        f"font-family:{theme.FONT_FAMILY_BOLD};font-size:14px;"
    )


def mini_player_separator_style() -> str:
    return f"background:{theme.COLOR_PANEL_BORDER};min-height:1px;max-height:1px;"


def mini_player_button_style() -> str:
    return (
        f"QPushButton{{background:{theme.COLOR_BG};color:{theme.COLOR_TEXT};"
        f"border:1px solid {theme.COLOR_PANEL_BORDER};border-radius:18px;}}"
        f"QPushButton:hover{{background:{theme.COLOR_PANEL};border-color:{theme.COLOR_ACCENT};color:{theme.COLOR_ACCENT};}}"
        f"QPushButton:pressed{{background:#0d0d0d;border-color:{theme.COLOR_ACCENT};}}"
    )


def mini_player_slider_style() -> str:
    return (
        "QSlider::groove:horizontal{height:6px;background:#333;border-radius:3px;margin:8px 10px;}"
        f"QSlider::sub-page:horizontal{{background:{theme.COLOR_ACCENT};border-radius:3px;}}"
        "QSlider::add-page:horizontal{background:#222;border-radius:3px;}"
        f"QSlider::handle:horizontal{{background:{theme.COLOR_TEXT};border:1px solid {theme.COLOR_PANEL_BORDER};"
        "width:14px;height:14px;margin:-7px -7px;-qt-background-role:dark;border-radius:7px;}}"
        f"QSlider::handle:horizontal:hover{{background:{theme.COLOR_ACCENT};}}"
    )
