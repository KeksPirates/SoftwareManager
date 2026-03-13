from PySide6.QtGui import QColor
import darkdetect

def _is_dark_mode():
    return darkdetect.isDark()


def _theme_colors():
    dark = _is_dark_mode()
    if dark:
        return {
            "text": "rgba(255, 255, 255, 0.9)",
            "border": "rgba(255, 255, 255, 0.06)",
            "selected": "rgba(255, 255, 255, 0.04)",
            "header_text": "rgba(255, 255, 255, 0.5)",
            "header_border": "rgba(255, 255, 255, 0.1)",
            "hover": QColor(255, 255, 255, 15),
        }
    else:
        return {
            "text": "rgba(0, 0, 0, 0.87)",
            "border": "rgba(0, 0, 0, 0.08)",
            "selected": "rgba(0, 0, 0, 0.06)",
            "header_text": "rgba(0, 0, 0, 0.6)",
            "header_border": "rgba(0, 0, 0, 0.12)",
            "hover": QColor(0, 0, 0, 15),
        }


def _table_stylesheet(view_type="QTableWidget"):
    c = _theme_colors()
    dark = _is_dark_mode()
    color_rule = "" if dark else f"color: {c['text']};"
    return f"""
        {view_type} {{
            border: none;
            outline: 0;
            font-size: 13px;
            {color_rule}
        }}
        {view_type}::item {{
            border-bottom: 1px solid {c["border"]};
            padding: 6px 14px;
            outline: none;
            {color_rule}
        }}
        {view_type}::item:selected {{
            background: {c["selected"]};
            outline: none;
            border: none;
            border-bottom: 1px solid {c["border"]};
        }}
        {view_type}::item:focus {{
            outline: none;
            border: none;
            border-bottom: 1px solid {c["border"]};
        }}
        QHeaderView {{
            background: transparent;
        }}
        QHeaderView::section {{
            background: transparent;
            color: {c["header_text"]};
            font-weight: normal;
            border: none;
            border-bottom: 1px solid {c["header_border"]};
            padding: 6px 14px;
        }}
        QHeaderView::section:checked {{
            background: transparent;
            color: {c["header_text"]};
            font-weight: normal;
        }}
    """


SVG_PLAY = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><polygon points="6,3 20,12 6,21" fill="{color}"/></svg>'
SVG_PAUSE = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><rect x="5" y="3" width="4" height="18" rx="1" fill="{color}"/><rect x="15" y="3" width="4" height="18" rx="1" fill="{color}"/></svg>'
SVG_FOLDER = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M2 6c0-1.1.9-2 2-2h5l2 2h7c1.1 0 2 .9 2 2v10c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6z" fill="{color}"/></svg>'
