import aria2p
import subprocess
from core.utils.data.state import state
from core.utils.general.logs import update_download_completed_by_hash
from core.utils.general.logs import consoleLog
from plyer import notification
import socket
import time
import sys


def send_notification(shutdown_event):
    notified = set()
    while not shutdown_event.is_set():
        try:
            for d in state.aria2.get_downloads():
                if d.is_metadata:
                    continue
                if d.progress == 100 and d.gid not in notified:
                    notification.notify(
                        title="Download finished",
                        message=f"{d.name} has finished downloading.",
                        timeout=4
                    )
                    notified.add(d.gid)
            state.downloads = [d for d in state.aria2.get_downloads() if d.is_active and not d.is_metadata]
        except Exception:
            pass
        time.sleep(5)

def update_log(shutdown_event):
    updated = set()
    while not shutdown_event.is_set():
        try:
            for d in state.aria2.get_downloads():
                if d.is_metadata:
                    continue
                if d.progress == 100 and d.gid not in updated:
                    consoleLog(f"Marking {d.name} as completed")
                    update_download_completed_by_hash(d.info_hash, True)
                    updated.add(d.gid)
            state.downloads = [d for d in state.aria2.get_downloads() if d.is_active and not d.is_metadata]
        except Exception:
            pass
        time.sleep(5)