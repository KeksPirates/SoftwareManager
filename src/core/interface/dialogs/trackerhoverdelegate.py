from core.interface.dialogs.theme import _theme_colors
from PySide6.QtWidgets import QStyledItemDelegate

class TrackerHoverDelegate(QStyledItemDelegate):
    def __init__(self, get_hovered_row, parent=None):
        super().__init__(parent)
        self._get_hovered_row = get_hovered_row

    def paint(self, painter, option, index):
        if index.row() == self._get_hovered_row():
            painter.save()
            painter.fillRect(option.rect, _theme_colors()["hover"])
            painter.restore()
        super().paint(painter, option, index)
