from utils.logging.logs import update_download_completed_by_hash
from utils.logging.logs import consoleLog
from PySide6.QtCore import QObject, QTimer
from utils.data.state import state
from plyer import notification
import libtorrent as lt
import time
import os


def cleanup_session():
    if state.dl_session is not None:
        with state.downloads_lock:
            for magnetdl in state.active_downloads.values():
                if hasattr(magnetdl, 'pause'):  # check it's a handle
                    magnetdl.pause()
        
        del state.dl_session
        state.dl_session = None
        with state.downloads_lock:
            state.active_downloads.clear()

class AppDaemons(QObject):
    def __init__(self):
        super().__init__()

        self.notified_magnets = set()
        self.updated_magnets = set()

        # Create Timers
        self.deleted_files_timer = QTimer(self)
        self.completed_downloads_timer = QTimer(self)

        # Connect Timer Signals
        self.deleted_files_timer.timeout.connect(self.check_deleted_files)
        self.completed_downloads_timer.timeout.connect(self.check_completed_downloads)

    def start_all(self):
        consoleLog("Starting Timer: deleted_files")
        self.deleted_files_timer.start(2000)
        consoleLog("Starting Timer: completed_downloads")
        self.completed_downloads_timer.start(5000)

    def check_deleted_files(self):
        try:
            with state.downloads_lock:
                items = list(state.active_downloads.items())
            for magnet_uri, magnetdl in items:
                if isinstance(magnetdl, dict):
                    continue
                
                status = magnetdl.status()
                
                if status.state == lt.torrent_status.seeding and status.has_metadata:
                    file_path = os.path.join(status.save_path, status.name)

                    if not os.path.exists(file_path):
                        consoleLog(f"Registered File Deletion: {status.name}")
                        state.dl_session.remove_torrent(magnetdl)
                        with state.downloads_lock:
                            del state.active_downloads[magnet_uri]
        except Exception as e:
            consoleLog(f"Exception while checking for file deletions: {e}")

    def check_completed_downloads(self):
        try:
            with state.downloads_lock:
                items = list(state.active_downloads.items())
                seeded = set(state.seeded_magnets)
            for magnet_uri, magnetdl in items:
                if isinstance(magnetdl, dict):
                    continue
                
                status = magnetdl.status()
                
                if status.state == lt.torrent_status.seeding:
                
                    if magnet_uri not in self.updated_magnets and magnet_uri not in seeded:
                        consoleLog(f"Marking {status.name} as completed")
                        if hasattr(status, 'info_hashes'):
                            info_hash = str(status.info_hashes.v1)
                        else:
                            info_hash = str(status.info_hash)
                        update_download_completed_by_hash(info_hash, True)
                        self.updated_magnets.add(magnet_uri)

                    if magnet_uri not in self.notified_magnets:
                        notification.notify(
                            title="Download finished",
                            message=f"{status.name} has finished downloading.",
                            timeout=4
                        )
                        self.notified_magnets.add(magnet_uri)

        except Exception as e:
            consoleLog(f"Exception while checking downloads: {e}")