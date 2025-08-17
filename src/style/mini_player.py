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

