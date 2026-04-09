from PySide6.QtCore import Qt, QPoint, Signal, QThreadPool, QThread
from utils.logging.logs import consoleLog, remove_download_log
from utils.network.download import download_selected
from utils.data.tracker import get_magnet_link
from utils.general.wrappers import run_thread
from PySide6.QtWidgets import QMessageBox
from utils.data.state import state
from send2trash import send2trash
from PySide6 import QtWidgets
import threading
import webbrowser
import subprocess
import platform
import time
import os


class MagnetWorker(QThread):
    finished = Signal(str)

    def __init__(self, url, parent=None):
        super().__init__(parent)
        self.url = url

    def run(self):
        magnet = get_magnet_link(self.url)
        if magnet:
            self.finished.emit(magnet)

class ContextMenu_Downloads:
    def __init__(self, main_window):
        self.main_window = main_window
        self.context_menu = QtWidgets.QMenu(main_window)
        self.context_menu.addAction("Open Containing Folder", self.openFolderAction)
        self.context_menu.addAction("Copy Magnet URI", self.copyMagnetURIAction)
        self.context_menu.addAction("Remove from list", self.cancelDownloadAction)
        self.context_menu.addAction("Delete File", self.deleteFileAction)

        main_window.downloadList.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        main_window.downloadList.customContextMenuRequested.connect(self._show_context_menu)

    @property
    def downloadList(self):
        return self.main_window.downloadList

    def _show_context_menu(self, pos: QPoint):
        index = self.downloadList.indexAt(pos)
        if index.isValid():
            self._context_menu_row = index.row()
            self.context_menu.exec(self.downloadList.viewport().mapToGlobal(pos))

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
        selected_rows = sorted(set(index.row() for index in self.downloadList.selectedIndexes()), reverse=True)

        if not selected_rows:
            return

        names = []
        items_to_remove = []

        with state.downloads_lock:
            keys = list(state.active_downloads.keys())

            for row in selected_rows:
                if 0 <= row < len(keys):
                    magnet_link = keys[row]
                    magnetdl = state.active_downloads[magnet_link]

                    try:
                        name = magnetdl.status().name
                    except RuntimeError:
                        name = "Unknown"

                    names.append(name)
                    items_to_remove.append((magnet_link, magnetdl, name))

        confirm = QMessageBox.question(
            self.main_window,
            "Cancel Downloads",
            f"Are you sure you want to cancel {len(names)} download(s)?\n\n" + "\n".join(names),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if confirm != QMessageBox.StandardButton.Yes:
            return

        for magnet_link, magnetdl, name in items_to_remove:
            with state.downloads_lock:
                state.active_downloads.pop(magnet_link, None)

            remove_download_log(magnet_link)

            if state.dl_session:
                try:
                    state.dl_session.remove_torrent(magnetdl)
                except Exception as e:
                    consoleLog(f"Exception while removing download from LibTorrent: {e}")

            consoleLog(f"Cancelled download: {name}", True)


    def deleteFileAction(self):
        selected_rows = sorted(set(index.row() for index in self.downloadList.selectedIndexes()), reverse=True)

        if not selected_rows:
            return

        items_to_remove = []

        with state.downloads_lock:
            keys = list(state.active_downloads.keys())

            for row in selected_rows:
                if 0 <= row < len(keys):
                    magnet_link = keys[row]
                    magnetdl = state.active_downloads[magnet_link]

                    try:
                        status = magnetdl.status()
                        save_path = status.save_path
                        torrent_name = status.name
                    except RuntimeError:
                        consoleLog("Error: torrent handle already invalid", True)
                        continue

                    download_path = os.path.join(save_path, torrent_name)

                    items_to_remove.append((magnet_link, magnetdl, torrent_name, download_path))

        if not items_to_remove:
            return

        names = [item[2] for item in items_to_remove]

        confirm = QMessageBox.question(
            self.main_window,
            "Delete Files",
            f"Are you sure you want to delete {len(names)} download(s)?\n\n" + "\n".join(names),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if confirm != QMessageBox.StandardButton.Yes:
            return

        for magnet_link, magnetdl, torrent_name, download_path in items_to_remove:
            with state.downloads_lock:
                state.active_downloads.pop(magnet_link, None)

            remove_download_log(magnet_link)

            if state.dl_session:
                try:
                    state.dl_session.remove_torrent(magnetdl)
                    time.sleep(0.5)
                except Exception as e:
                    consoleLog(f"Exception while removing download from LibTorrent: {e}")

            if download_path and os.path.exists(download_path):
                last_error = None
                for attempt in range(3):
                    try:
                        if os.path.isfile(download_path) or os.path.isdir(download_path):
                            send2trash(download_path)
                        consoleLog(f"Deleted files for: {torrent_name}", True)
                        last_error = None
                        break
                    except Exception as e:
                        last_error = e
                        if attempt < 2:
                            time.sleep(0.5)

                if last_error:
                    consoleLog(f"Error deleting files: {last_error}", True)
            else:
                consoleLog(f"Removed entry (files not found): {torrent_name}", True)

class ContextMenu_TrackerTable:
    def __init__(self, main_window):
        self.main_window = main_window
        self.context_menu = QtWidgets.QMenu(main_window)
        self.context_menu.addAction("Copy Magnet URI", self.copyMagnetURIAction)
        self.context_menu.addAction("Open in Browser", self.openInBrowserAction)
        self.context_menu.addAction("Download Item", self.downloadItemAction)

        state.trackertable.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        state.trackertable.customContextMenuRequested.connect(self._show_context_menu)

    @property
    def TrackerTable(self):
        return state.trackertable

    def _show_context_menu(self, pos: QPoint):
        index = self.TrackerTable.indexAt(pos)
        if index.isValid():
            self._context_menu_row = index.row()
            self.context_menu.exec(self.TrackerTable.viewport().mapToGlobal(pos))

    def copyMagnetURIAction(self):
        if not hasattr(self, '_context_menu_row'):
            return
        row = self._context_menu_row

        if not state.posts or row < 0 or row >= len(state.posts):
            return

        post = state.posts[row]
        url = post.get("url")
        if not url:
            return

        worker = MagnetWorker(url, parent=self.main_window)
        worker.finished.connect(self._on_magnet_fetched)
        worker.finished.connect(worker.deleteLater)
        worker.start()

    def _on_magnet_fetched(self, magnet):
        clipboard = QtWidgets.QApplication.clipboard()
        clipboard.setText(magnet)
        consoleLog("Magnet URI copied to clipboard!", True)

    def openInBrowserAction(self):
        if not hasattr(self, '_context_menu_row'):
            return
        row = self._context_menu_row

        if not state.posts or row < 0 or row >= len(state.posts):
            return

        post = state.posts[row]
        url = post.get("url")
        if url:
            try: webbrowser.open(url)
            except Exception as e: consoleLog(f"Failed to open URL: {e}", True)

    def downloadItemAction(self):
        if not hasattr(self, '_context_menu_row'):
            return
        row = self._context_menu_row
        if not state.posts or row < 0 or row >= len(state.posts):
            return

        run_thread(threading.Thread(target=download_selected, args=(state.trackertable.selectedItems(),)))
