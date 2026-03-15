from core.interface.dialogs.theme import _table_stylesheet
from PySide6.QtWidgets import QTableWidget
from PySide6 import QtWidgets
from PySide6.QtCore import Qt

def _create_tracker_table(self):
    table = QTableWidget()
    table.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
    table.verticalHeader().setVisible(False)
    table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
    table.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.ExtendedSelection)
    table.setShowGrid(False)
    table.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
    table.viewport().setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
    table.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
    table.horizontalHeader().setHighlightSections(False)
    table.horizontalHeader().setStretchLastSection(False)
    table.setStyleSheet(_table_stylesheet("QTableWidget"))
    table.setMouseTracking(True)
    table.viewport().setMouseTracking(True)
    table.viewport().installEventFilter(self)

    table.setItemDelegateForColumn(0, self._tracker_elided_delegate)

    self._apply_default_headers(table)
    return table
