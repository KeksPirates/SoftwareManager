from core.interface.dialogs.theme import _theme_colors
from PySide6.QtWidgets import QStyledItemDelegate
from PySide6 import QtWidgets

class HoverRowDelegate(QStyledItemDelegate):

    def paint(self, painter, option, index):
        from core.interface.gui import MainWindow

        opt = QtWidgets.QStyleOptionViewItem(option)
        option.state &= ~QtWidgets.QStyle.StateFlag.State_HasFocus
        option.state &= ~QtWidgets.QStyle.StateFlag.State_Selected

        hovered_row = MainWindow._instance._hovered_row if MainWindow._instance else -1
        if index.row() == hovered_row:
            painter.save()
            painter.fillRect(option.rect, _theme_colors()["hover"])
            painter.restore()
        super().paint(painter, opt, index)
