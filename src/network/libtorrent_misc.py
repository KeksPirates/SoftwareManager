from utils.logging.logs import update_download_completed_by_hash
from utils.logging.logs import consoleLog
from utils.data.state import state
from plyer import notification
import libtorrent as lt
import time
import os


def cleanup_session():
    if state.dl_session is not None:
        for magnetdl in state.active_downloads.values():
            if hasattr(magnetdl, 'pause'):  # Check it's a handle
                magnetdl.pause()
        
        del state.dl_session
        state.dl_session = None
        state.active_downloads.clear()




def send_notification(shutdown_event):
    notified = set()
    while not shutdown_event.is_set():
        try:
            for magnet_uri, magnetdl in list(state.active_downloads.items()):
                if isinstance(magnetdl, dict):
                    continue
                
                status = magnetdl.status()
                
                if status.state == lt.torrent_status.seeding and magnet_uri not in notified:
                    notification.notify(
                        title="Download finished",
                        message=f"{status.name} has finished downloading.",
                        timeout=4
                    )
                    notified.add(magnet_uri)
        except Exception as e:
            consoleLog(f"Exception while sending notification: {e}")
        time.sleep(5)

def update_log(shutdown_event):
    updated = set()
    while not shutdown_event.is_set():
        try:
            for magnet_uri, magnetdl in list(state.active_downloads.items()):
                if isinstance(magnetdl, dict):
                    continue
                
                status = magnetdl.status()
                
                if status.state == lt.torrent_status.seeding and magnet_uri not in updated and magnet_uri not in state.seeded_magnets:
                    consoleLog(f"Marking {status.name} as completed")
                    if hasattr(status, 'info_hashes'):
                        info_hash = str(status.info_hashes.v1)
                    else:
                        info_hash = str(status.info_hash)
                    update_download_completed_by_hash(info_hash, True)
                    updated.add(magnet_uri)
        except Exception as e:
            consoleLog(f"Exception while updating log file: {e}")
        time.sleep(5)

def check_deleted_files(shutdown_event):
    while not shutdown_event.is_set():
        try:
            for magnet_uri, magnetdl in list(state.active_downloads.items()):
                if isinstance(magnetdl, dict):
                    continue
                
                status = magnetdl.status()
                
                if status.state == lt.torrent_status.seeding and status.has_metadata:
                    file_path = os.path.join(status.save_path, status.name)

                    if not os.path.exists(file_path):
                        consoleLog(f"Registered File Deletion: {status.name}")
                        state.dl_session.remove_torrent(magnetdl)
                        del state.active_downloads[magnet_uri]
        except Exception as e:
            consoleLog(f"Exception while checking for file deletions: {e}")
        time.sleep(5)