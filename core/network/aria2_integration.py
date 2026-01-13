import aria2p
import subprocess
from core.utils.data.state import state
from core.utils.general.logs import update_download_completed_by_hash
from plyer import notification
import time
import sys

def run_aria2p():

    state.aria2 = aria2p.API(
        aria2p.Client(
            host="http://localhost",
            port=6800,
            secret=""
        )
    )
    
    return state.aria2


def aria2server():
    download_path = state.download_path
    speed_limit = state.speed_limit

    cmd = [
        "aria2c",
        "--enable-rpc",
        "--disable-ipv6", # added this since it caused problems with vpns
        "--rpc-listen-all",
        "--rpc-listen-port=6800",
        f"--dir={download_path}",
        f"--max-download-limit={speed_limit * 1024}",
        "-x", str(state.aria2_threads),
        "-s", str(state.aria2_threads),
    ]
    
    aria2server = subprocess.Popen(
        cmd,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
    )
    return aria2server

def dlprogress():
    try:
        state.downloads = [download for download in state.aria2.get_downloads() if not download.is_metadata]
        downloads = state.downloads
        if downloads:
            for download in downloads:
                progress = download.progress_string(0)
                progress_int = int(progress.strip('%'))
                return progress_int
        return 0
    except:
        return 0

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
                    if state.debug:
                        print(f"Marking {d.name} as completed")
                    update_download_completed_by_hash(d.info_hash, True)
                    updated.add(d.gid)
            state.downloads = [d for d in state.aria2.get_downloads() if d.is_active and not d.is_metadata]
        except Exception:
            pass
        time.sleep(5)