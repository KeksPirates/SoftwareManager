from core.interface.dialogs.theme import _theme_colors
from PySide6.QtWidgets import QStyledItemDelegate
from PySide6.QtCore import Qt

class ElidedItemDelegate(QStyledItemDelegate):
    def __init__(self, get_hovered_row, parent=None):
        super().__init__(parent)
        self._get_hovered_row = get_hovered_row

    def initStyleOption(self, option, index):
        super().initStyleOption(option, index)
        if option.text:
            metrics = option.fontMetrics
            text_rect = option.rect.adjusted(14, 0, -14, 0)
            option.text = metrics.elidedText(option.text, Qt.TextElideMode.ElideMiddle, text_rect.width())

    def paint(self, painter, option, index):
        if index.row() == self._get_hovered_row():
            painter.save()
            painter.fillRect(option.rect, _theme_colors()["hover"])
            painter.restore()
        super().paint(painter, option, index)
