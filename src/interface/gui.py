from interface.dialogs.trackerhoverdelegate import TrackerHoverDelegate
from interface.dialogs.elideditemdelegate import ElidedItemDelegate
from interface.dialogs.trackertable import _create_tracker_table
from interface.dialogs.downloadlist import _create_download_list
from interface.assets.base64_icons import settings_white_base64
from interface.assets.base64_icons import settings_black_base64
from interface.dialogs.downloadlist import download_list_update
from interface.dialogs.update import get_version, UpdateDialog
from interface.dialogs.theme import _accent_selection_color
from utils.logging.logs import consoleLog, flush_log_buffer
from interface.dialogs.downloadmodel import DownloadModel
from interface.dialogs.settings import settings_dialog
from interface.assets.base64_icons import logo_base64
from interface.dialogs.eventfilter import eventFilter
from utils.network.download import download_selected
from interface.utils.searchhelper import run_search
from interface.utils.tabhelper import create_tab
from utils.general.shutdown import closehelper
from utils.general.wrappers import run_thread
from interface.dialogs.image import Image
from utils.data.state import state

import interface.dialogs.contextmenu

from PySide6 import QtWidgets
from PySide6.QtCore import (
    Qt, 
    QTimer, 
    Signal, 
    QSize 
)

from PySide6.QtWidgets import (
    QLineEdit,
    QTableView,
    QWidget,
    QVBoxLayout,
    QLabel,
    QHBoxLayout,
    QComboBox,
    QTabWidget,
    QHeaderView,
    QTableWidgetItem,
    QTextEdit,
    QStatusBar,
    QStyledItemDelegate,
)

from PySide6.QtGui import (
    QIcon, 
    QCloseEvent, 
    QPixmap, 
    QGuiApplication, 
)

import darkdetect
import threading
import platform
import base64

def windowCloseHelper():
    QGuiApplication.quit()

class CenteredDelegate(QStyledItemDelegate):
    def initStyleOption(self, option, index):
        super().initStyleOption(option, index)
        option.displayAlignment = Qt.AlignmentFlag.AlignVCenter

class MainWindow(QtWidgets.QMainWindow, QWidget):
    eventFilter = eventFilter
    log_signal = Signal(str)
    search_results_signal = Signal(list)
    _instance = None

    def __init__(self):
        super().__init__()
        MainWindow._instance = self
        self.log_signal.connect(self._on_log_signal)
        self.search_results_signal.connect(self._on_search_results)

        pixmap = QPixmap()
        image_data = base64.b64decode(logo_base64)
        pixmap.loadFromData(image_data)
        self.setWindowIcon(QIcon(pixmap))

        # Set AppID on Windows
        if platform.system() == "Windows":
            try:
                import ctypes
                appid = 'SoftwareManager'
                ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(appid)
            except Exception as e:
                consoleLog(f"Could not set app ID: {e}")

        # Get current version
        # interface.dialogs.update
        get_version()
        UpdateDialog()

        # Initialize Window
        self.setWindowTitle("Software Manager")
        self.setGeometry(100, 100, 800, 600)

        self.controls = QWidget()
        self.controlsLayout = QVBoxLayout()

        # Searchbar
        self.searchbar = QLineEdit()
        self.searchbar.setPlaceholderText("Search for software...")
        self.searchbar.setClearButtonEnabled(True)
        self.searchbar.setMinimumHeight(30)
        self.searchbar.returnPressed.connect(self._start_search)

        # Download Button
        self.dlbutton = QtWidgets.QPushButton("Download")
        self.dlbutton.setCursor(Qt.CursorShape.PointingHandCursor)

        # Dialog for empty results
        self.emptyResults = QLabel("No Results")
        self.emptyResults.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.emptyResults.hide()

        self.downloadList = QTableView()
        self.downloadList.setMouseTracking(True)
        self._hovered_row = -1
        self._tracker_hovered_row = -1
        self._tracker_hovered_table = None
        self._last_dl_row_count = 0
        self.emptyDownload = QLabel("No items in downloads.")
        self.emptyDownload.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.consoleLog = QTextEdit()
        self.statusbar = QStatusBar()

        flush_log_buffer()

        self._tracker_elided_delegate = ElidedItemDelegate(lambda: self._tracker_hovered_row, self)
        self._tracker_hover_delegate = TrackerHoverDelegate(lambda: self._tracker_hovered_row, self)

        state.trackertable = _create_tracker_table(self)
        state.trackertable.cellDoubleClicked.connect(lambda: run_thread(threading.Thread(target=download_selected, args=(state.trackertable.selectedItems(),))))

        container = QWidget()
        containerLayout = QVBoxLayout()
        containerLayout.addWidget(self.searchbar)
        containerLayout.addWidget(state.trackertable)

        # interface.dialogs.hoverrowdelegate
        self.download_model = DownloadModel()
        self.downloadList = _create_download_list(self)
        self.downloadList.viewport().installEventFilter(self)

        self.dlbutton.clicked.connect(lambda: run_thread(threading.Thread(target=download_selected, args=(state.trackertable.selectedItems(),))))

        container.setLayout(containerLayout)
        self.setCentralWidget(container)

        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabBar::tab {
                font-size: 11px;
                padding: 2px 8px;
                height: 25px;
            }
            QTabWidget::pane {
                margin-top: -20px;
            }
        """)

        self.horizontal_layout = QHBoxLayout()
        self.horizontal_layout.addWidget(self.emptyResults, stretch=3)
        self.horizontal_layout.addWidget(state.trackertable)

        # Tabs
        create_tab("Search", [self.searchbar, self.horizontal_layout, self.dlbutton], tabs=self.tabs, stretch=False)
        create_tab("Downloads", [self.emptyDownload, self.downloadList], tabs=self.tabs, stretch=False)

        # Corner Widget (Settings Button, Tracker list, Tab button container)
        self.corner_widget = QWidget()
        self.corner_layout = QHBoxLayout(self.corner_widget)
        self.corner_layout.setContentsMargins(0, 0, 0, 0)

        # Tracker list
        self.tracker_list = QComboBox()
        self.tracker_list.setContentsMargins(0, 0, 0, 0)
        self.tracker_list.setItemDelegate(CenteredDelegate(self.tracker_list))
        self.tracker_list.addItems(list(state.trackers.keys()))
        self.tracker_list.setCursor(Qt.CursorShape.PointingHandCursor)
        self.tracker_list.activated.connect(self.set_tracker)
        if state.accent_color:
            self.tracker_list.setStyleSheet(
                f"QComboBox QAbstractItemView::item:selected {{ background: {_accent_selection_color()}; }}"
            )
        self.corner_layout.addWidget(self.tracker_list)

        # Settings button
        self.settings_btn = QtWidgets.QToolButton()
        self.settings_btn.setIconSize(QSize(21, 21))
        self.settings_btn.setStyleSheet("background: transparent;")
        self.settings_btn.setToolTip("Settings")
        self.settings_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.settings_btn.clicked.connect(lambda: settings_dialog(self))
        self.corner_layout.addWidget(self.settings_btn)

        # Adjust theme based on system preferences
        if darkdetect.isDark():
            settings_white_pixmap = QPixmap()
            settings_white = base64.b64decode(settings_white_base64)
            settings_white_pixmap.loadFromData(settings_white)
            self.settings_btn.setIcon(QIcon(settings_white_pixmap))
        else:
            settings_black_pixmap = QPixmap()
            settings_black = base64.b64decode(settings_black_base64)
            settings_black_pixmap.loadFromData(settings_black)
            self.settings_btn.setIcon(QIcon(settings_black_pixmap))

        self.tab_wrapper = QWidget()
        self.tab_layout = QVBoxLayout()
        self.tab_layout.setContentsMargins(0, 0, 0, 0)
        self.tab_layout.setSpacing(0)

        self.tab_bar_layout = QHBoxLayout()
        self.tab_bar_layout.setContentsMargins(0, 0, 0, 0)
        self.tab_bar_layout.setSpacing(0)

        self.tab_bar_layout.addWidget(self.tabs.tabBar(), stretch=0)
        self.tab_bar_layout.addStretch()
        self.tab_bar_layout.addWidget(self.corner_widget, stretch=0)

        self.tab_layout.addLayout(self.tab_bar_layout)
        self.tab_layout.addWidget(self.tabs)
        self.tab_wrapper.setLayout(self.tab_layout)

        containerLayout.addWidget(self.tab_wrapper)
        containerLayout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.consoleLog.setReadOnly(True)
        self.consoleLog.setFixedHeight(150)
        self.consoleLog.setStyleSheet("margin-bottom: 0px; background: transparent;")
        containerLayout.addWidget(self.consoleLog)

        self.statusbar.show()
        self.statusbar.setStyleSheet("background: transparent; border: none; padding-right: 1px; padding-left: 6px; padding-bottom: 1px; margin-top: -8px")

        self.version = QLabel(f"Version: {state.version}")
        self.statusbar.addPermanentWidget(self.version, Qt.AlignmentFlag.AlignLeft)

        # (\u2193) Arrow down, (\u2191) Arrow up
        self.speed_label = QLabel("↓ 0.0 kB/s  ↑ 0.0 kB/s")
        self.speed_label.setStyleSheet("padding-right: 6px;")
        self.statusbar.addPermanentWidget(self.speed_label)

        self.setStatusBar(self.statusbar)

        self.download_timer = QTimer()
        self.download_timer.timeout.connect(lambda: download_list_update(self))
        self.download_timer.start(500)

        self.active_timer = QTimer()
        self.active_timer.timeout.connect(self.show_empty_downloads)
        self.active_timer.start(500)

        self._context_menu_downloads = interface.dialogs.contextmenu.ContextMenu_Downloads(self)
        self._context_menu_trackertable = interface.dialogs.contextmenu.ContextMenu_TrackerTable(self)
        self.image_overlay = Image(self)

    def _apply_default_headers(self, table):
        tracker_name = state.currenttracker if hasattr(state, 'currenttracker') and state.currenttracker else None
        if tracker_name is None:
            keys = list(state.trackers.keys())
            tracker_name = keys[0] if keys else None

        headers = []
        if tracker_name and tracker_name in state.trackers:
            tracker_mod = state.trackers[tracker_name]
            if hasattr(tracker_mod, 'headers'):
                headers = tracker_mod.headers
            elif hasattr(tracker_mod, 'HEADERS'):
                headers = tracker_mod.HEADERS

        if not headers:
            if state.currenttracker == "rutracker":
                headers = ["Post Title", "Author", "Seeders", "Leechers"]
            elif state.currenttracker == "steamrip":
                headers = ["Game"]
            else: 
                headers = ["Post Title", "Author"] # i know this makes it less "modular", but its qol

        table.setRowCount(0)

        col_count = table.columnCount()
        if col_count != len(headers):
            for i in range(col_count):
                table.setItemDelegateForColumn(i, None)
            table.setColumnCount(len(headers))

        table.setHorizontalHeaderLabels(headers)
        self._apply_tracker_column_modes(table, len(headers))

    def _apply_tracker_column_modes(self, table, col_count):
        header = table.horizontalHeader()
        if col_count > 0:
            header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
            table.setItemDelegateForColumn(0, self._tracker_elided_delegate)
        for i in range(1, col_count):
            header.setSectionResizeMode(i, QHeaderView.ResizeMode.ResizeToContents)
            table.setItemDelegateForColumn(i, self._tracker_hover_delegate)

    def _start_search(self):
        self.searchbar.setEnabled(False)
        state.trackertable.setRowCount(0)
        self.show_empty_results(False)

        def _search_thread():
            try:
                run_search(self)
            except Exception as e:
                consoleLog(f"Search error: {e}", True)
                self.search_results_signal.emit([])
        run_thread(threading.Thread(target=_search_thread))

    @staticmethod
    def add_log(text):
        if hasattr(MainWindow, "_instance") and MainWindow._instance:
            MainWindow._instance.log_signal.emit(text)
            return True
        return False

    def _on_log_signal(self, text):
        if hasattr(self, 'consoleLog'):
            self.consoleLog.append(text)
            # Delete lines if exceeding 500
            doc = self.consoleLog.document()
            if doc.blockCount() > 500:
                cursor = self.consoleLog.textCursor()
                cursor.movePosition(cursor.MoveOperation.Start)
                cursor.movePosition(cursor.MoveOperation.Down, cursor.MoveMode.KeepAnchor, doc.blockCount() - 500)
                cursor.removeSelectedText()
                cursor.deleteChar()
                
            self.consoleLog.verticalScrollBar().setValue(
                self.consoleLog.verticalScrollBar().maximum()
            )

    def _on_search_results(self, headers):
        if state.posts is None or state.posts == []:
            self.show_empty_results(True)
            self.searchbar.setEnabled(True)
            self.searchbar.setFocus()
            return

        table = state.trackertable
        table.setRowCount(0)

        col_count = table.columnCount()
        need_reconfig = col_count != len(headers)

        if need_reconfig:
            for i in range(col_count):
                table.setItemDelegateForColumn(i, None)
            table.setColumnCount(len(headers))
            table.setHorizontalHeaderLabels(headers)
            self._apply_tracker_column_modes(table, len(headers))
        else:
            table.setHorizontalHeaderLabels(headers)

        table.setRowCount(len(state.posts))
        for x, rowdata in enumerate(state.posts):
            for y, (_, data) in enumerate(rowdata.items()):
                item = QTableWidgetItem(str(data))
                item.setData(Qt.ItemDataRole.UserRole, x)
                table.setItem(x, y, item)

        self.show_empty_results(False)
        self.searchbar.setEnabled(True)
        self.searchbar.setFocus()

        self._update_speed_label()


    def _update_speed_label(self):
        total_down = 0
        total_up = 0
        with state.downloads_lock:
            active_items = list(state.active_downloads.values())
        
        for handle in active_items:
            try:
                s = handle.status()
                total_down += s.download_rate
                total_up += s.upload_rate
            except Exception as e:
                consoleLog(f"Exception while updating speed label: {e}")
        down_kb = total_down / 1024
        up_kb = total_up / 1024
        down_text = f"{down_kb / 1024:.1f} MB/s" if down_kb > 1024 else f"{down_kb:.1f} kB/s"
        up_text = f"{up_kb / 1024:.1f} MB/s" if up_kb > 1024 else f"{up_kb:.1f} kB/s"
        
            
        if hasattr(self, 'speed_label'):
            self.speed_label.setText(f"↓ {down_text}  ↑ {up_text}")

    def mousePressEvent(self, event):
        state.trackertable.clearSelection()
        self.downloadList.clearSelection()
        super().mousePressEvent(event)

    def changeEvent(self, event):
        super().changeEvent(event)

    def closeEvent(self, event: QCloseEvent):
        if state.close_to_tray is True:
            event.ignore()
            self.hide()
            return
        else:
            self.shutdown(event)

    def shutdown(self, event: QCloseEvent):
        closehelper()
        event.accept()
        from utils.general.shutdown import force_exit
        force_exit()

    def _invalidate_hover_row(self, row):
        if row >= 0 and self.download_model:
            self.downloadList.viewport().update()

    def set_tracker(self, _):
        state.currenttracker = self.tracker_list.currentText()
        self._apply_default_headers(state.trackertable)

    def show_empty_results(self, show: bool):
        if show:
            state.trackertable.hide()
            self.emptyResults.show()
        else:
            state.trackertable.show()
            self.emptyResults.hide()

    def show_empty_downloads(self):
        with state.downloads_lock:
            has_downloads = len(state.active_downloads) > 0
        if has_downloads:
            self.emptyDownload.hide()
            self.downloadList.show()
        else:
            self.emptyDownload.show()
            self.downloadList.hide()
