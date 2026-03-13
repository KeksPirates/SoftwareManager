from core.utils.logging.logs import consoleLog, remove_download_log
from PySide6.QtWidgets import QMessageBox
from core.utils.data.state import state
from PySide6.QtCore import Qt, QPoint
from PySide6 import QtWidgets
import subprocess
import platform
import time
import os

class ContextMenu:
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
        if not hasattr(self, '_context_menu_row'):
            return
        row = self._context_menu_row
        with state.downloads_lock:
            if row < 0 or row >= len(state.active_downloads):
                return
            magnet_link = list(state.active_downloads.keys())[row]
            magnetdl = state.active_downloads[magnet_link]

        # Cache the name BEFORE removing from session
        try:
            torrent_name = magnetdl.status().name
        except RuntimeError:
            torrent_name = "Unknown"

        confirm = QMessageBox.question(
            self.main_window, "Cancel Download",
            f"Are you sure you want to cancel the download of '{torrent_name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if confirm == QMessageBox.StandardButton.Yes:
            with state.downloads_lock:
                state.active_downloads.pop(magnet_link, None)
            remove_download_log(magnet_link)

            if state.dl_session:
                try:
                    state.dl_session.remove_torrent(magnetdl)
                except Exception:
                    pass

            consoleLog(f"Cancelled download: {torrent_name}", True)


    def deleteFileAction(self):
        if not hasattr(self, '_context_menu_row'):
            return
        row = self._context_menu_row
        with state.downloads_lock:
            if row < 0 or row >= len(state.active_downloads):
                return
            magnet_link = list(state.active_downloads.keys())[row]
            magnetdl = state.active_downloads[magnet_link]
        try:
            status = magnetdl.status()
            save_path = status.save_path
            torrent_name = status.name
        except RuntimeError:
            consoleLog("Error: torrent handle already invalid", True)
            with state.downloads_lock:
                state.active_downloads.pop(magnet_link, None)
            remove_download_log(magnet_link)
            return
        download_path = os.path.join(save_path, torrent_name)
        confirm = QMessageBox.question(
            self.main_window, "Delete Files",
            f"Are you sure you want to delete the downloaded files of '{torrent_name}'? This action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if confirm == QMessageBox.StandardButton.Yes:
            with state.downloads_lock:
                state.active_downloads.pop(magnet_link, None)
            remove_download_log(magnet_link)
            if state.dl_session:
                try:
                    state.dl_session.remove_torrent(magnetdl)
                    time.sleep(0.5)
                except Exception:
                    pass
            if download_path and os.path.exists(download_path):
                import shutil
                last_error = None
                for attempt in range(3):
                    try:
                        if os.path.isfile(download_path):
                            os.remove(download_path)
                        else:
                            shutil.rmtree(download_path)
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
