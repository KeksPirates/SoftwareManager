from core.utils.logging.logs import consoleLog, remove_download_log, flush_log_buffer
from core.utils.general.wrappers import run_thread
from core.utils.data.state import state
from core.utils.network.download import download_selected
from core.utils.network.update_checker import get_updates
from core.interface.utils.tabhelper import create_tab
from core.interface.utils.searchhelper import return_pressed
from core.interface.utils.svghelper import svg_icon
from core.interface.dialogs.settings import settings_dialog
from core.interface.assets.base64_icons import settings_black_base64
from core.interface.assets.base64_icons import settings_white_base64
from core.interface.assets.base64_icons import logo_base64
from core.utils.general.shutdown import closehelper

from PySide6 import QtWidgets
from PySide6.QtCore import (
    Qt, 
    QTimer, 
    QModelIndex, 
    QAbstractTableModel, 
    Signal, 
    QEvent, 
    QSize 
)

from PySide6.QtWidgets import (
    QLineEdit,
    QTableView,
    QWidget,
    QVBoxLayout,
    QListWidget,
    QLabel,
    QHBoxLayout,
    QComboBox,
    QTabWidget,
    QHeaderView,
    QMessageBox,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QStyledItemDelegate,
    QStatusBar
)

from PySide6.QtGui import (
    QIcon, 
    QCloseEvent, 
    QImage, 
    QPixmap, 
    QContextMenuEvent, 
    QGuiApplication, 
    QColor, 
)

import darkdetect
import threading
import platform
import requests as r
import os
import subprocess
import libtorrent as lt
import sys
import json
import base64


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


def _verify_hash(file_path, expected_hash):
    import hashlib
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    return f"sha256:{sha256.hexdigest()}" == expected_hash


def _download_update(assets):
    import tempfile
    import time
    for asset in assets:
        if "-windows-setup.exe" in asset["name"]:
            filename = asset["name"]
            setup_hash = asset["hash"]
            url = asset["url"]
            break

    if not filename:
        consoleLog("Error: No Windows installer found in release assets")
        return

    installer_path = os.path.join(tempfile.gettempdir(), filename)
    progress = QtWidgets.QProgressDialog("Downloading installer...", None, 0, 0)
    progress.setWindowTitle("Updating")
    progress.setWindowModality(Qt.WindowModality.ApplicationModal)
    progress.setCancelButton(None)
    progress.setMinimumDuration(0)
    progress.setAutoClose(False)
    progress.setAutoReset(False)
    progress.setRange(0, 100)
    progress.setValue(0)
    progress.show()
    QtWidgets.QApplication.processEvents()
    response = r.get(url, allow_redirects=True, stream=True)
    total = int(response.headers.get("content-length", 0))
    downloaded = 0
    with open(installer_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=65536):
            f.write(chunk)
            downloaded += len(chunk)
            if total > 0:
                progress.setValue(int(downloaded * 100 / total))
            QtWidgets.QApplication.processEvents()
    if not os.path.exists(installer_path):
        progress.close()
        raise FileNotFoundError("Executable not found")
    if setup_hash:
        if _verify_hash(installer_path, setup_hash):
            consoleLog(f"Sucessfully validated installer hash ({setup_hash})")
        else:
            consoleLog("Error: Invalid Filehash, file may be corrupted")
            sys.exit(0)
    else:
        consoleLog("Skipping Hash Verification (no hash found for release)")
    progress.setLabelText("Installing update...")
    progress.setValue(100)
    QtWidgets.QApplication.processEvents()
    subprocess.Popen([installer_path, "/VERYSILENT", "/SUPPRESSMSGBOXES", "/SP-", "/CLOSEAPPLICATIONS"])
    time.sleep(1)
    sys.exit(0)


def windowCloseHelper():
    QGuiApplication.quit()


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


class MainWindow(QtWidgets.QMainWindow, QWidget):
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

        if platform.system() == "Windows":
            try:
                import ctypes
                appid = 'SoftwareManager'
                ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(appid)
            except Exception as e:
                consoleLog(f"Could not set app ID: {e}")

        build_info_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "build_info.json")
        if os.path.exists(build_info_path):
            with open(build_info_path, "r") as f:
                build_info = json.load(f)
                state.version = build_info.get("version")

        if state.ignore_updates is False and platform.system() == "Windows":
            assets = get_updates()
            if assets != None:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Icon.Information)
                msg.setWindowTitle("Update Available")
                msg.setText("A new version is available.")
                msg.setInformativeText("Press Ok to download the update.")
                msg.setStandardButtons(QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Ignore)
                response = msg.exec_()
                if response == QMessageBox.StandardButton.Ok:
                    _download_update(assets)

        self.setWindowTitle("Software Manager")
        self.setGeometry(100, 100, 800, 600)

        self.controls = QWidget()
        self.controlsLayout = QVBoxLayout()

        self.searchbar = QLineEdit()
        self.searchbar.setPlaceholderText("Search for software...")
        self.searchbar.setClearButtonEnabled(True)
        self.searchbar.setMinimumHeight(30)
        self.searchbar.returnPressed.connect(self._start_search)

        self.dlbutton = QtWidgets.QPushButton("Download")
        self.dlbutton.setCursor(Qt.CursorShape.PointingHandCursor)
        self.libraryList = QListWidget()

        self.emptyResults = QLabel("No Results")
        self.emptyResults.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.emptyResults.hide()

        self.download_model = None
        self.downloadList = QTableView()
        self.downloadList.setMouseTracking(True)
        self._hovered_row = -1
        self._tracker_hovered_row = -1
        self._tracker_hovered_table = None
        self._last_dl_row_count = 0
        self.downloadList.viewport().installEventFilter(self)
        self.emptyLibrary = QLabel("No items in library.")
        self.emptyDownload = QLabel("No items in downloads.")
        self.emptyDownload.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.consoleLog = QTextEdit()
        self.statusbar = QStatusBar()

        flush_log_buffer()

        self._tracker_elided_delegate = ElidedItemDelegate(lambda: self._tracker_hovered_row, self)
        self._tracker_hover_delegate = TrackerHoverDelegate(lambda: self._tracker_hovered_row, self)

        state.trackertable = self._create_tracker_table()

        container = QWidget()
        containerLayout = QVBoxLayout()
        containerLayout.addWidget(self.searchbar)
        containerLayout.addWidget(state.trackertable)

        class DownloadModel(QAbstractTableModel):
            def __init__(self):
                super().__init__()
                self.headers = ["Action", "Name", "Status", "Progress", "Speed", "Size", "Total Size"]

            def rowCount(self, parent=QModelIndex()):
                if parent.isValid():
                    return 0
                with state.downloads_lock:
                    return len(state.active_downloads)

            def columnCount(self, parent=QModelIndex()):
                return len(self.headers)

            def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
                if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
                    return self.headers[section]
                return None

            def data(self, index, role=Qt.ItemDataRole.DisplayRole):
                if not index.isValid():
                    return None

                with state.downloads_lock:
                    if index.row() >= len(state.active_downloads) or index.row() < 0:
                        return None
                    
                    try:
                        magnet_link = list(state.active_downloads.keys())[index.row()]
                        magnetdl = state.active_downloads[magnet_link]
                        status = magnetdl.status()
                    except (IndexError, KeyError, RuntimeError):
                        return None

                if role == Qt.ItemDataRole.DisplayRole:
                    col = index.column()
                    if col == 0:
                        pass
                    elif col == 1:
                        return status.name if status.has_metadata else "Fetching metadata..."
                    elif col == 2:
                        if status.paused:
                            is_auto = getattr(status, 'auto_managed', True)
                            return "Queued" if is_auto else "Paused"
                        elif status.state == lt.torrent_status.downloading:
                            return "Downloading"
                        elif status.state == lt.torrent_status.seeding:
                            return "Seeding"
                        else:
                            return "Queued"
                    elif col == 3:
                        return f"{status.progress * 100:.1f}%"
                    elif col == 4:
                        down_kb = status.download_rate / 1024
                        up_kb = status.upload_rate / 1024
                        down_text = f"{down_kb / 1024:.1f} MB/s" if down_kb > 1024 else f"{down_kb:.1f} kB/s"
                        up_text = f"{up_kb / 1024:.1f} MB/s" if up_kb > 1024 else f"{up_kb:.1f} kB/s"
                        return f"↓ {down_text} ↑ {up_text}"
                    elif col == 5:
                        downloaded_mb = status.total_wanted_done / (1024 * 1024)
                        if downloaded_mb > 1024:
                            return f"{downloaded_mb / 1024:.2f} GB"
                        else:
                            return f"{downloaded_mb:.1f} MB"
                    elif col == 6:
                        total_mb = status.total_wanted / (1024 * 1024)
                        if total_mb > 1024:
                            return f"{total_mb / 1024:.2f} GB"
                        else:
                            return f"{total_mb:.1f} MB"
                    elif col == 7:
                        if status.download_rate > 0:
                            bytes_left = status.total_wanted - status.total_wanted_done
                            eta_seconds = bytes_left / status.download_rate
                            if eta_seconds < 60:
                                return f"{int(eta_seconds)}s"
                            elif eta_seconds < 3600:
                                minutes = int(eta_seconds / 60)
                                seconds = int(eta_seconds % 60)
                                return f"{minutes}m {seconds}s"
                            else:
                                hours = int(eta_seconds / 3600)
                                minutes = int((eta_seconds % 3600) / 60)
                                return f"{hours}h {minutes}m"
                        else:
                            return "∞" if status.paused else "Stalled"
                if role == Qt.ItemDataRole.UserRole and index.column() == 0:
                    return status.paused
                return None

            def toggle_pause_resume(self, row):
                with state.downloads_lock:
                    if row >= len(state.active_downloads) or row < 0:
                        return
                    try:
                        magnet_link = list(state.active_downloads.keys())[row]
                        magnetdl = state.active_downloads[magnet_link]
                        status = magnetdl.status()
                    except (IndexError, KeyError, RuntimeError):
                        return

                if status.state == lt.torrent_status.seeding:
                    try:
                        save_path = magnetdl.save_path()
                        if save_path and os.path.exists(save_path):
                            if platform.system() == "Windows":
                                os.startfile(os.path.normpath(save_path))
                            elif platform.system() == "Linux":
                                subprocess.Popen(["xdg-open", save_path])
                            elif platform.system() == "Darwin":
                                subprocess.Popen(["open", save_path])
                    except Exception:
                        pass
                    return

                is_paused = status.paused
                if is_paused:
                    if hasattr(magnetdl, 'set_flags'):
                        magnetdl.set_flags(lt.torrent_flags.auto_managed)
                    magnetdl.resume()
                    consoleLog(f"Resumed download: {status.name}", True)
                else:
                    if hasattr(magnetdl, 'unset_flags'):
                        magnetdl.unset_flags(lt.torrent_flags.auto_managed)
                    magnetdl.pause()
                    consoleLog(f"Paused download: {status.name}", True)
                idx = self.index(row, 0)
                self.dataChanged.emit(idx, idx, [Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.UserRole])

        class HoverRowDelegate(QStyledItemDelegate):
            def paint(self, painter, option, index):
                opt = QtWidgets.QStyleOptionViewItem(option)
                opt.state &= ~QtWidgets.QStyle.StateFlag.State_HasFocus
                opt.state &= ~QtWidgets.QStyle.StateFlag.State_Selected
                if index.row() == MainWindow._instance._hovered_row:
                    painter.save()
                    painter.fillRect(opt.rect, _theme_colors()["hover"])
                    painter.restore()
                super().paint(painter, opt, index)

        class PauseResumeDelegate(QStyledItemDelegate):
            clicked = Signal(int)

            def paint(self, painter, option, index):
                opt = QtWidgets.QStyleOptionViewItem(option)
                opt.state &= ~QtWidgets.QStyle.StateFlag.State_HasFocus
                opt.state &= ~QtWidgets.QStyle.StateFlag.State_Selected
                if index.row() == MainWindow._instance._hovered_row:
                    painter.save()
                    painter.fillRect(opt.rect, _theme_colors()["hover"])
                    painter.restore()
                super().paint(painter, opt, index)

            def setEditorData(self, editor, index):
                button = editor.findChild(QtWidgets.QPushButton)
                magnet_link = list(state.active_downloads.keys())[index.row()]
                magnetdl = state.active_downloads[magnet_link]
                status = magnetdl.status()
                if button:
                    if status.state == lt.torrent_status.seeding:
                        button.setIcon(svg_icon(SVG_FOLDER, 18))
                        button.setText("")
                    else:
                        is_user_paused = status.paused and not status.auto_managed
                        button.setIcon(svg_icon(SVG_PLAY if is_user_paused else SVG_PAUSE, 18))
                        button.setText("")

            def createEditor(self, parent, option, index):
                magnet_link = list(state.active_downloads.keys())[index.row()]
                magnetdl = state.active_downloads[magnet_link]
                status = magnetdl.status()
                widget = QWidget(parent)
                widget.setStyleSheet("border: none; background: transparent;")
                layout = QHBoxLayout(widget)
                layout.setContentsMargins(0, 0, 0, 0)
                if status.state == lt.torrent_status.seeding:
                    btnPause = QtWidgets.QPushButton()
                    btnPause.setIcon(svg_icon(SVG_FOLDER, 18))
                else:
                    btnPause = QtWidgets.QPushButton()
                    is_user_paused = status.paused and not status.auto_managed
                    btnPause.setIcon(svg_icon(SVG_PLAY if is_user_paused else SVG_PAUSE, 18))
                btnPause.setIconSize(QSize(18, 18))
                btnPause.setFixedSize(30, 30)
                btnPause.setCursor(Qt.CursorShape.PointingHandCursor)
                btnPause.setStyleSheet("QPushButton { border: none; background: transparent; padding: 0px; }")
                btnPause.clicked.connect(lambda: self.clicked.emit(index.row()))
                layout.addStretch()
                layout.addWidget(btnPause)
                layout.addStretch()
                widget.setLayout(layout)
                return widget

            def editorEvent(self, event, model, option, index):
                return False

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

        self.tab1 = create_tab("Search", self.searchbar, state.trackertable, self.tabs, self.dlbutton, self.horizontal_layout)
        self.tab3 = create_tab("Downloads", self.emptyDownload, self.downloadList, self.tabs, None, None)

        if state.image_path is not None and os.path.exists(state.image_path):
            self.image = QImage(state.image_path)
            self.image = self.image.scaledToWidth(300, Qt.TransformationMode.SmoothTransformation)
            self.pixmap = QPixmap.fromImage(self.image)
            self.overlay_label = QLabel(self)
            self.overlay_label.setPixmap(self.pixmap)
            self.overlay_label.adjustSize()
            self.overlay_label.raise_()
            x = self.width() - self.overlay_label.width()
            y = self.height() - self.overlay_label.height()
            self.overlay_label.move(x, y)

        self.corner_widget = QWidget()
        self.corner_layout = QHBoxLayout(self.corner_widget)
        self.corner_layout.setContentsMargins(0, 0, 0, 0)

        self.tracker_list = QComboBox()
        self.tracker_list.addItems(list(state.trackers.keys()))
        self.tracker_list.setCursor(Qt.CursorShape.PointingHandCursor)
        self.tracker_list.activated.connect(self.set_tracker)
        self.corner_layout.addWidget(self.tracker_list)

        self.settings_btn = QtWidgets.QToolButton()
        self.settings_btn.setIconSize(QSize(21, 21))
        self.settings_btn.setStyleSheet("background: transparent;")

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

        self.settings_btn.setToolTip("Settings")
        self.settings_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.settings_btn.clicked.connect(lambda: settings_dialog(self))
        self.corner_layout.addWidget(self.settings_btn)

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

        self.speed_label = QLabel("\u2193 0.0 kB/s  \u2191 0.0 kB/s")
        self.speed_label.setStyleSheet("padding-right: 6px;")
        self.statusbar.addPermanentWidget(self.speed_label)

        self.setStatusBar(self.statusbar)

        self.download_timer = QTimer()
        self.download_timer.timeout.connect(self.download_list_update)
        self.download_timer.start(500)

        self.active_timer = QTimer()
        self.active_timer.timeout.connect(self.show_empty_downloads)
        self.active_timer.start(500)

        self.context_menu = QtWidgets.QMenu(self)
        self.context_menu.addAction("Open Containing Folder", self.openFolderAction)
        self.context_menu.addAction("Copy Magnet URI", self.copyMagnetURIAction)
        self.context_menu.addAction("Remove from list", self.cancelDownloadAction)
        self.context_menu.addAction("Delete File", self.deleteFileAction)

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
        def _search_thread():
            try:
                return_pressed(self)
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
            for y, (key, data) in enumerate(rowdata.items()):
                item = QTableWidgetItem(str(data))
                item.setData(Qt.ItemDataRole.UserRole, x)
                table.setItem(x, y, item)

        self.show_empty_results(False)
        self.searchbar.setEnabled(True)
        self.searchbar.setFocus()

    def update_image_overlay(self, new_image_path):
        self.image = QImage(new_image_path)
        self.pixmap = QPixmap.fromImage(self.image)
        self.overlay_label.setPixmap(self.pixmap)
        self.overlay_label.adjustSize()

    def download_list_update(self):
        if not self.download_model:
            self._update_speed_label()
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
                            delegate.setEditorData(editor, idx)

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
            except Exception:
                pass
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
        closehelper()
        event.accept()
        from core.utils.general.shutdown import force_exit
        force_exit()

    def eventFilter(self, obj, event):
        try:
            if hasattr(self, 'speed_label') and obj == self.speed_label:
                if event.type() == QEvent.Type.MouseButtonRelease:
                    settings_dialog(self)
                    return True
            if obj == state.trackertable.viewport():
                if event.type() == QEvent.Type.MouseMove:
                    pos = event.position().toPoint() if hasattr(event, 'position') else event.pos()
                    idx = state.trackertable.indexAt(pos)
                    new_row = idx.row() if idx.isValid() else -1
                    if new_row != self._tracker_hovered_row or state.trackertable is not self._tracker_hovered_table:
                        self._tracker_hovered_row = new_row
                        self._tracker_hovered_table = state.trackertable
                        state.trackertable.viewport().update()
                elif event.type() == QEvent.Type.Leave:
                    self._tracker_hovered_row = -1
                    self._tracker_hovered_table = None
                    state.trackertable.viewport().update()
            if obj == self.downloadList.viewport():
                if event.type() == QEvent.Type.MouseMove:
                    pos = event.position().toPoint() if hasattr(event, 'position') else event.pos()
                    idx = self.downloadList.indexAt(pos)
                    new_row = idx.row() if idx.isValid() else -1
                    if new_row != self._hovered_row:
                        old_row = self._hovered_row
                        self._hovered_row = new_row
                        self._invalidate_hover_row(old_row)
                        self._invalidate_hover_row(new_row)
                elif event.type() == QEvent.Type.Leave:
                    old_row = self._hovered_row
                    self._hovered_row = -1
                    self._invalidate_hover_row(old_row)
        except (RuntimeError, AttributeError):
            pass
        return super().eventFilter(obj, event)

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

    def contextMenuEvent(self, event: QContextMenuEvent):
        if self.downloadList.underMouse():
            pos = self.downloadList.viewport().mapFromGlobal(event.globalPos())
            index = self.downloadList.indexAt(pos)
            if index.isValid():
                row = index.row()
                self._context_menu_row = row
                self.context_menu.exec(event.globalPos())
        else:
            super().contextMenuEvent(event)

    def openFolderAction(self):
        if not hasattr(self, '_context_menu_row'):
            return
        row = self._context_menu_row
        if row < 0 or row >= len(state.active_downloads):
            return
        magnet_link = list(state.active_downloads.keys())[row]
        magnetdl = state.active_downloads[magnet_link]
        download_path = magnetdl.save_path()
        if download_path and os.path.exists(download_path):
            if platform.system() == "Windows":
                os.startfile(os.path.normpath(download_path))
            elif platform.system() == "Linux":
                subprocess.Popen(["xdg-open", download_path])
            elif platform.system() == "Darwin":
                subprocess.Popen(["open", download_path])

    def copyMagnetURIAction(self):
        if not hasattr(self, '_context_menu_row'):
            return
        row = self._context_menu_row
        if row < 0 or row >= len(state.active_downloads):
            return
        magnet_link = list(state.active_downloads.keys())[row]
        clipboard = QtWidgets.QApplication.clipboard()
        clipboard.setText(magnet_link)

    def cancelDownloadAction(self):
        if not hasattr(self, '_context_menu_row'):
            return
        row = self._context_menu_row
        if row < 0 or row >= len(state.active_downloads):
            return
        magnet_link = list(state.active_downloads.keys())[row]
        magnetdl = state.active_downloads[magnet_link]
        confirm = QMessageBox.question(self, "Cancel Download", f"Are you sure you want to cancel the download of '{magnetdl.status().name}'?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if confirm == QMessageBox.StandardButton.Yes:
            if hasattr(magnetdl, 'stop'):
                magnetdl.stop()
            elif state.dl_session:
                try:
                    state.dl_session.remove_torrent(magnetdl)
                except Exception:
                    pass
            del state.active_downloads[magnet_link]
            remove_download_log(magnet_link)
            consoleLog(f"Cancelled download: {magnetdl.status().name}", True)

    def deleteFileAction(self):
        if not hasattr(self, '_context_menu_row'):
            return
        row = self._context_menu_row
        if row < 0 or row >= len(state.active_downloads):
            return
        magnet_link = list(state.active_downloads.keys())[row]
        magnetdl = state.active_downloads[magnet_link]
        status = magnetdl.status()
        save_path = status.save_path
        torrent_name = status.name
        download_path = os.path.join(save_path, torrent_name)
        confirm = QMessageBox.question(self, "Delete Files", f"Are you sure you want to delete the downloaded files of '{magnetdl.status().name}'? This action cannot be undone.", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if confirm == QMessageBox.StandardButton.Yes:
            if hasattr(magnetdl, 'stop'):
                magnetdl.stop()
            elif state.dl_session:
                try:
                    state.dl_session.remove_torrent(magnetdl)
                except Exception:
                    pass
            if download_path and os.path.exists(download_path):
                try:
                    if os.path.isfile(download_path):
                        remove_download_log(magnet_link)
                        os.remove(download_path)
                        del state.active_downloads[magnet_link]
                        consoleLog(f"Deleted files for: {magnetdl.status().name}", True)
                    else:
                        import shutil
                        remove_download_log(magnet_link)
                        shutil.rmtree(download_path)
                        del state.active_downloads[magnet_link]
                        consoleLog(f"Deleted files for: {magnetdl.status().name}", True)
                except Exception as e:
                    consoleLog(f"Error deleting files: {e}", True)
            else:
                del state.active_downloads[magnet_link]
                remove_download_log(magnet_link)
                consoleLog(f"Removed entry (files not found): {magnetdl.status().name}", True)
