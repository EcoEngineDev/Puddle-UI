from . import theme


def primary_button_style() -> str:
    return f"""
        QPushButton {{
            background-color: {theme.COLOR_PANEL};
            color: {theme.COLOR_ACCENT};
            border: 2px solid {theme.COLOR_PANEL_BORDER};
            border-radius: 10px;
            padding: 15px;
            font-family: {theme.FONT_FAMILY_BOLD};
            font-size: 18px;
        }}
        QPushButton:hover {{
            background-color: {theme.COLOR_ACCENT};
            color: #000000;
        }}
    """


def nav_button_style() -> str:
    return f"""
        QPushButton {{
            background-color: {theme.COLOR_PANEL};
            border: 2px solid {theme.COLOR_PANEL_BORDER};
            border-radius: 15px;
            padding: 10px;
        }}
        QPushButton:hover {{
            background-color: {theme.COLOR_ACCENT};
            border-color: {theme.COLOR_ACCENT};
        }}
        QPushButton:pressed {{
            background-color: #008060;
            border-color: #008060;
        }}
    """

