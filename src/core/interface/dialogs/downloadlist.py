from core.interface.dialogs.pauseresumedelegate import PauseResumeDelegate
from core.interface.dialogs.hoverrowdelegate import HoverRowDelegate
from core.interface.dialogs.downloadmodel import DownloadModel
from core.interface.dialogs.theme import _table_stylesheet
from PySide6.QtWidgets import QTableView, QHeaderView
from PySide6 import QtWidgets
from PySide6.QtCore import Qt

def _create_download_list(self) -> QTableView:
    self.download_model = DownloadModel()
    self.downloadList.setModel(self.download_model)
    self.downloadList.horizontalHeader().setStretchLastSection(False)
    self.downloadList.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
    self.downloadList.horizontalHeader().resizeSection(0, 70)
    self.downloadList.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
    self.downloadList.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
    self.downloadList.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
    self.downloadList.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
    self.downloadList.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
    self.downloadList.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)
    self.downloadList.horizontalHeader().setMinimumSectionSize(60)
    self.downloadList.verticalHeader().setDefaultSectionSize(40)
    self.downloadList.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
    self.downloadList.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.ExtendedSelection)
    self.downloadList.verticalHeader().setVisible(False)
    self.downloadList.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
    self.downloadList.horizontalHeader().setHighlightSections(False)
    self.downloadList.setMouseTracking(True)
    self.downloadList.setShowGrid(False)
    self.downloadList.setStyleSheet(_table_stylesheet("QTableView"))
    self.downloadList.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
    self.downloadList.viewport().setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

    download_model = self.download_model

    def on_pause_resume_clicked(row):
        download_model.toggle_pause_resume(row)

    self.downloadList.viewport().setMouseTracking(True)
    hover_delegate = HoverRowDelegate(self.downloadList)
    self.downloadList.setItemDelegate(hover_delegate)

    delegate = PauseResumeDelegate(self.downloadList)
    self.downloadList.setItemDelegateForColumn(0, delegate)
    delegate.clicked.connect(on_pause_resume_clicked)

    return self.downloadList

def download_list_update(self):
    self._update_speed_label()
    if not self.download_model:
        return

    row_count = self.download_model.rowCount()
    col_count = self.download_model.columnCount()

    if row_count > 0 and col_count > 0:
        top_left = self.download_model.index(0, 0)
        bottom_right = self.download_model.index(row_count - 1, col_count - 1)
        if top_left.isValid() and bottom_right.isValid():
            self.download_model.dataChanged.emit(top_left, bottom_right, [Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.UserRole])

    if row_count != self._last_dl_row_count:
        old_count = self._last_dl_row_count
        self._last_dl_row_count = row_count
        if row_count > 0:
            self.download_model.layoutAboutToBeChanged.emit()
            self.download_model.layoutChanged.emit()
            for row in range(row_count):
                idx = self.download_model.index(row, 0)
                if idx.isValid():
                    self.downloadList.closePersistentEditor(idx)
                    self.downloadList.openPersistentEditor(idx)
        elif old_count > 0:
            self.download_model.layoutAboutToBeChanged.emit()
            self.download_model.layoutChanged.emit()
    else:
        if row_count > 0:
            delegate = self.downloadList.itemDelegateForColumn(0)
            for row in range(row_count):
                idx = self.download_model.index(row, 0)
                if idx.isValid():
                    editor = self.downloadList.indexWidget(idx)
                    if editor and delegate:
                        try:
                            delegate.setEditorData(editor, idx)
                        except RuntimeError:
                            pass
