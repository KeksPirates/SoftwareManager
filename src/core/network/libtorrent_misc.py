from core.utils.data.state import state
from core.utils.general.logs import update_download_completed_by_hash
from core.utils.general.logs import consoleLog
from plyer import notification
import libtorrent as lt
import time


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
        except Exception:
            pass
        time.sleep(5)

def update_log(shutdown_event):
    updated = set()
    while not shutdown_event.is_set():
        try:
            for magnet_uri, magnetdl in list(state.active_downloads.items()):
                if isinstance(magnetdl, dict):
                    continue
                
                status = magnetdl.status()
                
                if status.state == lt.torrent_status.seeding and magnet_uri not in updated:
                    consoleLog(f"Marking {status.name} as completed")
                    info_hash = str(status.info_hash)
                    update_download_completed_by_hash(info_hash, True)
                    updated.add(magnet_uri)
        except Exception:
            pass
        time.sleep(5)