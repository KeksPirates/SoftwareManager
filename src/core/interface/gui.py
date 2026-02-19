from PySide6 import QtWidgets, QtCore, QtGui
from PySide6.QtCore import Qt, QTimer, QModelIndex, QAbstractTableModel, Signal, QEvent, QSize
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
    QProgressBar,
    QHeaderView,
    QMessageBox,
    QTableWidget,
    QTextEdit,
    QStyledItemDelegate,
)

from PySide6.QtGui import QIcon, QCloseEvent, QImage, QPixmap, QContextMenuEvent
import darkdetect
import threading
import platform
import requests as r
import os
import subprocess
import libtorrent as lt
import time
import sys
import json
import base64
from core.utils.general.logs import consoleLog, remove_download_log, flush_log_buffer
from core.utils.general.wrappers import run_thread
from core.utils.data.state import state
from core.utils.network.download import download_selected
from core.utils.network.update_checker import check_for_updates
from core.interface.utils.tabhelper import create_tab
from core.interface.utils.searchhelper import return_pressed
from core.interface.dialogs.settings import settings_dialog
from core.interface.assets.base64_icons import settings_black_base64
from core.interface.assets.base64_icons import settings_white_base64
from core.interface.assets.base64_icons import logo_base64
from core.network.libtorrent_misc import cleanup_session
from core.utils.general.shutdown import closehelper


def download_update(latest_version):
    new_filename = f"SoftwareManager-dev-{latest_version.replace('-dev', '')}-windows.exe"
    url = f"https://github.com/KeksPirates/SoftwareManager/releases/latest/download/SoftwareManager-dev-{latest_version.replace('-dev', '')}-windows.exe"

    print("Downloading update...", True)
    response = r.get(url, allow_redirects=True)
    with open(new_filename, "wb") as f:
        f.write(response.content)
    if not os.path.exists(new_filename):
        raise FileNotFoundError("Executable not found")
    subprocess.Popen([new_filename], shell=True)
    time.sleep(0.5)

    msg = QMessageBox()
    msg.setIcon(QMessageBox.Icon.Information)
    msg.setWindowTitle("New Version")
    msg.setText("New version installed.")
    msg.setInformativeText("Please remove the old exe.")
    msg.setStandardButtons(QMessageBox.StandardButton.Ok)

    sys.exit(0)


class MainWindow(QtWidgets.QMainWindow, QWidget):
    log_signal = Signal(str)  # Thread-safe signal for logging
    
    def __init__(self):
        super().__init__()
        MainWindow._instance = self
        self.log_signal.connect(self._on_log_signal)

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

        # Check for updates on Windows
        if state.ignore_updates is False and platform.system() == "Windows":
            result = check_for_updates()
            if result != (None, None):
                assets, latest_version = result

                if assets:
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Icon.Information)
                    msg.setWindowTitle("Update Available")
                    msg.setText("A new version is available.")
                    msg.setInformativeText("Press Ok to download the update.")
                    msg.setStandardButtons(QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Ignore)

                    response = msg.exec_()
                    if response == QMessageBox.StandardButton.Ok:
                        download_update(latest_version)

        self.setWindowTitle("Software Manager")
        self.setGeometry(100, 100, 800, 600)

        self.controls = QWidget()
        self.controlsLayout = QVBoxLayout()

        # Widgets
        self.searchbar = QLineEdit()
        self.searchbar.setPlaceholderText("Search for software...")
        self.searchbar.setClearButtonEnabled(True)
        self.searchbar.setMinimumHeight(30)
        self.searchbar.returnPressed.connect(lambda: run_thread(threading.Thread(target=return_pressed, args=(self,)))) # Triggers data function thread on enter

        self.dlbutton = QtWidgets.QPushButton("Download")
        self.dlbutton.setCursor(Qt.CursorShape.PointingHandCursor)
        self.libraryList = QListWidget()

        self.emptyResults = QLabel("No Results")
        self.emptyResults.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.emptyResults.hide()

        self.download_model = None
        self.downloadList = QTableView()
        self.emptyLibrary = QLabel("No items in library.")
        self.emptyDownload = QLabel("No items in downloads.")
        self.emptyDownload.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.consoleLog = QTextEdit()
        self.progressbar = QProgressBar()

        flush_log_buffer()

        # Table Widget for Item List
        self.qtablewidget = QTableWidget()
        
        self.qtablewidget.setColumnCount(4)
        self.qtablewidget.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.qtablewidget.verticalHeader().setVisible(False)
        self.qtablewidget.setHorizontalHeaderLabels(["Post Title", "Author", "Seeders", "Leechers"])

        

        header = self.qtablewidget.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch) 
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)   
        header.setStretchLastSection(False)

        self.qtablewidget.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.qtablewidget.viewport().setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground) 

        header = self.qtablewidget.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed) 
        header.resizeSection(1, 500)

        container = QWidget()
        containerLayout = QVBoxLayout()
        containerLayout.addWidget(self.searchbar)
        containerLayout.addWidget(self.qtablewidget)

        class DownloadModel(QAbstractTableModel):
            def __init__(self):
                super().__init__()
                self.headers = ["Action", "Name", "Status", "Progress", "Speed", "Size", "Total Size"]

            def rowCount(self, parent=QModelIndex()):
                return len(state.active_downloads)
            
            def columnCount(self, parent=QModelIndex()):
                return len(self.headers)

            def headerData(self, section, orientation, role=Qt.DisplayRole): 
                if role == Qt.DisplayRole and orientation == Qt.Horizontal: 
                    return self.headers[section]
                return None

            def data(self, index, role=Qt.DisplayRole): 
                if role == Qt.DisplayRole: 
                    col = index.column()

                    if index.row() >= len(state.active_downloads) or index.row() < 0:
                        return None
                    
                    magnet_link = list(state.active_downloads.keys())[index.row()] 
                    magnetdl = state.active_downloads[magnet_link]
                    
                    status = magnetdl.status()
                    
                    if col == 0:
                        pass
                    elif col == 1:
                        return status.name if status.has_metadata else "Fetching metadata..."
                    elif col == 2:
                        if status.state == lt.torrent_status.downloading: 
                            return "Downloading"
                        elif status.state == lt.torrent_status.seeding: 
                            return "Seeding"
                        elif status.paused:
                            return "Paused"
                        else:
                            return "Queued"
                    elif col == 3:
                        return f"{status.progress * 100:.1f}%"
                    elif col == 4:
                        speed_kbs = status.download_rate / 1024
                        if speed_kbs > 1024:
                            return f"{speed_kbs / 1024:.1f} MB/s"
                        else:
                            return f"{speed_kbs:.1f} kB/s"
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
                
                if role == Qt.UserRole and index.column() == 0: 
                    magnet_link = list(state.active_downloads.keys())[index.row()] 
                    magnetdl = state.active_downloads[magnet_link]
                    return magnetdl.status().paused
                
                return None

            def toggle_pause_resume(self, row):

                if row >= len(state.active_downloads) or row < 0:
                    return
                    
                magnet_link = list(state.active_downloads.keys())[row] 
                magnetdl = state.active_downloads[magnet_link]
                status = magnetdl.status()
                
                if status.state == lt.torrent_status.seeding: 
                    save_path = magnetdl.save_path()
                    if save_path and os.path.exists(save_path):
                        if platform.system() == "Windows":
                            os.startfile(os.path.normpath(save_path))
                        elif platform.system() == "Linux":
                            subprocess.Popen(["xdg-open", save_path])
                        elif platform.system() == "Darwin":
                            subprocess.Popen(["open", save_path])
                    return
                
                is_paused = bool(magnetdl.flags() & lt.torrent_flags.paused)
                if is_paused:
                    magnetdl.set_flags(lt.torrent_flags.auto_managed)
                    magnetdl.resume()
                    consoleLog(f"Resumed download: {status.name}", True)
                else:
                    magnetdl.unset_flags(lt.torrent_flags.auto_managed)
                    magnetdl.pause()
                    consoleLog(f"Paused download: {status.name}", True)
                
                idx = self.index(row, 0)
                self.dataChanged.emit(idx, idx, [Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.UserRole])

        class PauseResumeDelegate(QStyledItemDelegate):
            clicked = Signal(int)

            def setEditorData(self, editor, index):
                button = editor.findChild(QtWidgets.QPushButton)
                
                magnet_link = list(state.active_downloads.keys())[index.row()] 
                magnetdl = state.active_downloads[magnet_link]
                status = magnetdl.status()

                if button:
                    if status.state == lt.torrent_status.seeding: 
                        button.setText("📁")
                    else:
                        button.setText("▶︎" if status.paused else "⏸︎")

            def createEditor(self, parent, option, index):
                magnet_link = list(state.active_downloads.keys())[index.row()] 
                magnetdl = state.active_downloads[magnet_link]
                status = magnetdl.status()

                widget = QWidget(parent)
                widget.setStyleSheet("border: none;")
                layout = QHBoxLayout(widget)
                layout.setContentsMargins(0, 0, 0, 0)
                if status.state == lt.torrent_status.seeding: 
                    btnPause = QtWidgets.QPushButton("📁")
                else:
                    btnPause = QtWidgets.QPushButton("▶︎" if status.paused else "⏸︎")
                btnPause.setFixedSize(40, 30)
                btnPause.clicked.connect(lambda: self.clicked.emit(index.row()))
                layout.addStretch()
                layout.addWidget(btnPause)
                layout.addStretch()
                widget.setLayout(layout)
                return widget
            def editorEvent(self, event, model, option, index):
                if index.column() == 0 and event.type() == QEvent.Type.MouseButtonPress:
                    self.clicked.emit(index.row())
                    return True
                return False

        self.download_model = DownloadModel()
        self.downloadList.setModel(self.download_model)
        self.downloadList.horizontalHeader().setStretchLastSection(False)
        self.downloadList.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.downloadList.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.downloadList.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.downloadList.viewport().setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        download_model = self.download_model

        def on_pause_resume_clicked(row):
            download_model.toggle_pause_resume(row)

        delegate = PauseResumeDelegate(self.downloadList)
        self.downloadList.setItemDelegateForColumn(0, delegate)
        delegate.clicked.connect(on_pause_resume_clicked)

        # download button triggers
        self.dlbutton.clicked.connect(lambda: run_thread(threading.Thread(target=download_selected, args=(self.qtablewidget.currentItem(), state.posts, state.post_titles))))

        container.setLayout(containerLayout)
        self.setCentralWidget(container)

        # Tabs
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
        self.horizontal_layout.addWidget(self.qtablewidget)

        self.tab1 = create_tab("Search", self.searchbar, self.qtablewidget, self.tabs, self.dlbutton, self.horizontal_layout)
        # self.tab2 = create_tab("Library", self.emptyLibrary, self.libraryList, self.tabs, None, None)
        self.tab3 = create_tab("Downloads", self.emptyDownload, self.downloadList, self.tabs, None, None)

        if state.image_path is not None and os.path.exists(state.image_path):
            self.image = QImage(state.image_path)
            self.image = self.image.scaledToWidth(300, Qt.SmoothTransformation)
            self.pixmap = QPixmap.fromImage(self.image)
            self.overlay_label = QLabel(self)
            self.overlay_label.setPixmap(self.pixmap)
            self.overlay_label.adjustSize()
            self.overlay_label.raise_()

            # offset_x = -1350
            # offset_y = -550
            x = self.width() - self.overlay_label.width() # - offset_x
            y = self.height() - self.overlay_label.height() # - offset_y
            self.overlay_label.move(x, y)
        
        # temporarily disabled
        # state.image_changed.connect(self.update_image_overlay)

        
        self.corner_widget = QWidget()
        self.corner_layout = QHBoxLayout(self.corner_widget)
        self.corner_layout.setContentsMargins(0, 0, 0, 0)


        self.tracker_list = QComboBox()
        self.tracker_list.addItems(["rutracker", "uztracker", "m0nkrus"])
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
        containerLayout.addWidget(self.consoleLog)

        self.download_timer = QTimer()
        self.download_timer.timeout.connect(self.download_list_update)
        self.download_timer.start(500)

        self.active_timer = QTimer()
        self.active_timer.timeout.connect(self.show_empty_downloads)
        self.active_timer.start(500)

        self.context_menu = QtWidgets.QMenu(self)
        self.context_menu.addAction("Open Containing Folder", self.openFolderAction)
        self.context_menu.addAction("Copy Magnet URI", self.copyMagnetURIAction)
        self.context_menu.addAction("Cancel Download", self.cancelDownloadAction)
        self.context_menu.addAction("Delete File", self.deleteFileAction)

    @staticmethod
    def add_log(text):
        if MainWindow._instance:
            MainWindow._instance.log_signal.emit(text)
    
    def _on_log_signal(self, text):
        if hasattr(self, 'consoleLog'):
            self.consoleLog.append(text)
            self.consoleLog.verticalScrollBar().setValue(
                self.consoleLog.verticalScrollBar().maximum()
            )

    def update_image_overlay(self, new_image_path):
        self.image = QImage(new_image_path)
        self.pixmap = QPixmap.fromImage(self.image)

        self.overlay_label.setPixmap(self.pixmap)
        self.overlay_label.adjustSize()

    def download_list_update(self):
        if self.download_model:
            self.download_model.layoutAboutToBeChanged.emit()
            self.download_model.layoutChanged.emit()
            for row in range(self.download_model.rowCount()):
                idx = self.download_model.index(row, 0)
                self.downloadList.closePersistentEditor(idx)
                self.downloadList.openPersistentEditor(idx)
        

    def closeEvent(self, event: QCloseEvent):
        closehelper()
        event.accept()

    def set_tracker(self, _):
        state.tracker = self.tracker_list.currentText()

    def show_empty_results(self, show: bool):
        if show:
            self.qtablewidget.hide()
            self.emptyResults.show()
        else:
            self.qtablewidget.show()
            self.emptyResults.hide()

    def show_empty_downloads(self):
        if len(state.active_downloads) > 0:
            self.emptyDownload.hide()
            self.downloadList.show()
        else:
            self.emptyDownload.show()
            self.downloadList.hide()

    # thank you claude
    def resizeEvent(self, event):
        super().resizeEvent(event)
        table_width = self.qtablewidget.viewport().width()
        self.qtablewidget.setColumnWidth(1, int(table_width * 0.3))

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
            if download_path and os.path.exists(download_path):
                try:
                    if os.path.isfile(download_path):
                        os.remove(download_path)
                        del state.active_downloads[magnet_link]
                        remove_download_log(magnet_link)
                        consoleLog(f"Deleted files for: {magnetdl.status().name}", True)
                    else:
                        import shutil
                        shutil.rmtree(download_path)
                        del state.active_downloads[magnet_link]
                        remove_download_log(magnet_link)
                        consoleLog(f"Deleted files for: {magnetdl.status().name}", True)
                except Exception as e:
                    consoleLog(f"Error deleting files: {e}", True)
