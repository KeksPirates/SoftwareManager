from PySide6 import QtWidgets
from PySide6.QtCore import Qt, QTimer, QModelIndex, QAbstractTableModel, Signal, QEvent
from PySide6.QtWidgets import (
    QLineEdit,
    QTableView,
    QWidget,
    QVBoxLayout,
    QListWidget,
    QToolBar,
    QLabel,
    QHBoxLayout,
    QComboBox,
    QTabWidget,
    QProgressBar,
    QHeaderView,
    QMessageBox,
    QTableWidget,
    QTextEdit,
    QStyle,
    QStyleOptionButton,
    QStyledItemDelegate,
    QApplication,
    )

from PySide6.QtGui import QIcon, QAction, QCloseEvent, QImage, QPixmap
import darkdetect
import threading
import platform
import requests as r
import os
import subprocess
import time
import sys
import json
from core.utils.general.logs import consoleLog
from core.utils.general.wrappers import run_thread
from core.utils.data.state import state
from core.utils.network.download import download_selected
from core.utils.network.update_checker import check_for_updates
from core.utils.general.shutdown import closehelper
from core.interface.utils.tabhelper import create_tab
from core.interface.utils.searchhelper import return_pressed
from core.interface.dialogs.settings import settings_dialog
from core.network.aria2_integration import dlprogress


def download_update(latest_version):
    new_filename = f"SoftwareManager-dev-{latest_version.replace('-dev', '')}-windows.exe"
    url = f"https://github.com/KeksPirates/SoftwareManager/releases/latest/download/SoftwareManager-dev-{latest_version.replace('-dev', '')}-windows.exe"

    consoleLog("Downloading update...", True)
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

        def get_asset_path(filename):
            if getattr(sys, 'frozen', False):
                base_path = sys._MEIPASS
            else:
                base_path = os.path.dirname(__file__)

            asset_path = os.path.join(base_path, 'core', 'interface', 'assets', filename)
            if os.path.exists(asset_path):
                return asset_path

            return os.path.join('core', 'interface', 'assets', filename)
        
        self.setWindowIcon(QIcon(get_asset_path("logo.png")))


        if platform.system() == "Windows":
            try:
                import ctypes
                myappid = 'SoftwareManager.App.1'
                ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
            except Exception as e:
                consoleLog(f"Could not set app ID: {e}")

        build_info_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "build_info.json")
        if os.path.exists(build_info_path):
            with open(build_info_path, "r") as f:
                build_info = json.load(f)
                state.version = build_info.get("version")

        # Check for updates on Windows
        if state.ignore_updates is False:
            if platform.system() == "Windows":
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
        self.libraryList = QListWidget()

        self.emptyResults = QLabel("No Results")
        self.emptyResults.setAlignment(Qt.AlignCenter)
        self.emptyResults.hide()

        self.download_model = None
        self.downloadList = QTableView()
        self.emptyLibrary = QLabel("No items in library.")
        self.emptyDownload = QLabel("No items in downloads.")
        self.emptyDownload.setAlignment(Qt.AlignCenter)

        self.consoleLog = QTextEdit()
        self.progressbar = QProgressBar()

        # Table Widget for Item List
        self.qtablewidget = QTableWidget()

        self.qtablewidget.setColumnCount(2)
        self.qtablewidget.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.qtablewidget.verticalHeader().setVisible(False)
        self.qtablewidget.setHorizontalHeaderLabels(["Post Title", "Author"])

        header = self.qtablewidget.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch) 
        header.setSectionResizeMode(1, QHeaderView.Fixed)   
        header.setStretchLastSection(False)

        self.qtablewidget.setAttribute(Qt.WA_TranslucentBackground)
        self.qtablewidget.viewport().setAttribute(Qt.WA_TranslucentBackground)

        header = self.qtablewidget.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.Fixed)
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
                return len(state.downloads)
            
            def columnCount(self, parent=QModelIndex()):
                return len(self.headers)

            def headerData(self, section, orientation, role=Qt.DisplayRole):
                if role == Qt.DisplayRole and orientation == Qt.Horizontal:
                    return self.headers[section]
                return None

            def data(self, index, role=Qt.DisplayRole):
                col = index.column()
                download = state.downloads[index.row()]
                if role == Qt.DisplayRole:
                    col = index.column()

                    if col == 0:
                        return "▶︎" if download.is_paused else "⏸︎"
                    elif col == 1:
                        return download.name
                    elif col == 2:
                        return getattr(download, 'status', 'Downloading')
                    elif col == 3:
                        return f"{int(download.progress)}%"
                    elif col == 4:
                        return f"{download.download_speed_string()}"
                    elif col == 5:
                        pass
                    elif col == 6:
                        return f"{download.total_length_string()}"
                
                if role == Qt.UserRole and col == 0:
                    return download.is_paused

                return None

            def toggle_pause_resume(self, row):
                download = state.downloads[row]
                if download.is_paused:
                    download.resume()
                else:
                    download.pause()
                idx = self.index(row, 0)
                self.dataChanged.emit(idx, idx, [Qt.DisplayRole, Qt.UserRole])

        class PauseResumeDelegate(QStyledItemDelegate):
            clicked = Signal(int)

            def paint(self, painter, option, index):
                if index.column() != 0:
                    super().paint(painter, option, index)
                    return

                paused = index.data(Qt.UserRole)

                button = QStyleOptionButton()
                button.rect = option.rect
                button.text = "▶︎" if paused else "⏸︎"
                button.state = QStyle.State_Enabled

                QApplication.style().drawControl(
                    QStyle.CE_PushButton, button, painter
                )

            def editorEvent(self, event, model, option, index):
                if index.column() == 0 and event.type() == QEvent.Type.MouseButtonPress:
                    self.clicked.emit(index.row())
                    return True
                return False

        self.download_model = DownloadModel()
        self.downloadList.setModel(self.download_model)
        self.downloadList.horizontalHeader().setStretchLastSection(False)
        self.downloadList.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.downloadList.setSelectionBehavior(QTableView.SelectRows)
        self.downloadList.setAttribute(Qt.WA_TranslucentBackground)
        self.downloadList.viewport().setAttribute(Qt.WA_TranslucentBackground)

        download_model = self.download_model

        def on_pause_resume_clicked(row):
            download_model.toggle_pause_resume(row)

            download = state.downloads[row]
            if download.is_paused:
                download.pause()
            else:
                download.resume() 

        delegate = PauseResumeDelegate(self.downloadList)
        self.downloadList.setItemDelegateForColumn(0, delegate)
        delegate.clicked.connect(on_pause_resume_clicked)

        # download button triggers
        self.dlbutton.clicked.connect(lambda: run_thread(threading.Thread(target=download_selected, args=(self.qtablewidget.currentItem(), state.posts, state.post_titles))))

        container.setLayout(containerLayout)
        self.setCentralWidget(container)

        # Tabs
        self.tabs = QTabWidget()

        self.horizontal_layout = QHBoxLayout()
        self.horizontal_layout.addWidget(self.emptyResults, stretch=3)
        self.horizontal_layout.addWidget(self.qtablewidget)

        self.tab1 = create_tab("Search", self.searchbar, self.qtablewidget, self.tabs, self.dlbutton, self.horizontal_layout)
        self.tab2 = create_tab("Library", self.emptyLibrary, self.libraryList, self.tabs, None, None)
        self.tab3 = create_tab("Downloads", self.emptyDownload, self.downloadList, self.tabs, None, None)

        if state.image_path is not None and os.path.exists(state.image_path):
            self.image = QImage(state.image_path)
            self.pixmap = QPixmap.fromImage(self.image)
            self.overlay_label = QLabel(self)
            self.overlay_label.setPixmap(self.pixmap)
            self.overlay_label.adjustSize()
            self.overlay_label.raise_()

            offset_x = -1350
            offset_y = -550
            x = self.width() - self.overlay_label.width() - offset_x
            y = self.height() - self.overlay_label.height() - offset_y
            self.overlay_label.move(x, y)
        

        # temporarily disabled
        # state.image_changed.connect(self.update_image_overlay)

        containerLayout.addWidget(self.tabs)

        containerLayout.setAlignment(Qt.AlignmentFlag.AlignBottom)
        toolbar = QToolBar("Main Toolbar")
        self.addToolBar(toolbar)
        toolbar.setLayoutDirection(Qt.RightToLeft)

        self.tracker_list = QComboBox()
        self.tracker_list.addItems(["rutracker", "uztracker", "m0nkrus"])
        self.tracker_list.activated.connect(self.set_tracker)

        if darkdetect.isDark():
            settings_action = QAction(QIcon(get_asset_path("settings_white.png")), "Settings", self)
        else:
            settings_action = QAction(QIcon(get_asset_path("settings_black.png")), "Settings", self)

        settings_action.triggered.connect(lambda: settings_dialog(self))
        toolbar.addAction(settings_action)
        toolbar.addWidget(self.tracker_list)

        toolbar.setMovable(False)

        # self.progressbar.setValue(0)
        self.consoleLog.setReadOnly(True)
        self.consoleLog.setFixedHeight(150)
        containerLayout.addWidget(self.consoleLog)

        self.progress_timer = QTimer()
        self.progress_timer.timeout.connect(lambda: run_thread(threading.Thread(target=self.update_progress)))
        self.progress_timer.start(1000)

        self.download_timer = QTimer()
        self.download_timer.timeout.connect(lambda: run_thread(threading.Thread(target=self.download_list_update)))
        self.download_timer.start(500)

        self.active_timer = QTimer()
        self.active_timer.timeout.connect(self.show_empty_downloads)
        self.active_timer.start(500)

    @staticmethod
    def add_log(text):
        if MainWindow._instance:
            MainWindow._instance.log_signal.emit(text)
    
    def _on_log_signal(self, text):
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
        

    def closeEvent(self, event: QCloseEvent):
        closehelper()
        event.accept()

    def set_tracker(self, _):
        state.tracker = self.tracker_list.currentText()

    def update_progress(self):
        progress = dlprogress()
        self.progressbar.setValue(progress)

    def show_empty_results(self, show: bool):
        if show:
            self.qtablewidget.hide()
            self.emptyResults.show()
        else:
            self.qtablewidget.show()
            self.emptyResults.hide()

    def show_empty_downloads(self):
        if len(state.downloads) > 0:
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



    
