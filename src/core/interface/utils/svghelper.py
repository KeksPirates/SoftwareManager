

from PySide6 import QtWidgets
from PySide6.QtCore import Qt, QByteArray
from PySide6.QtGui import QIcon, QPixmap, QPainter
from PySide6.QtSvg import QSvgRenderer
import darkdetect

# Check if darkmode is enabled
def _is_dark_mode():
    return darkdetect.isDark()

def svg_icon(svg_str, size=20):
    app = QtWidgets.QApplication.instance()
    if app:
        if _is_dark_mode():
            color = "white"
        else:
            color = "#555555"
    else:
        color = "white"
    svg = svg_str.replace("{color}", color)
    renderer = QSvgRenderer(QByteArray(svg.encode()))
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    renderer.render(painter)
    painter.end()
    return QIcon(pixmap)