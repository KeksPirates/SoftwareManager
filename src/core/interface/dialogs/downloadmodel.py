from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt
from core.utils.logging.logs import consoleLog
from core.utils.data.state import state
import libtorrent as lt
import subprocess
import platform
import os

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
