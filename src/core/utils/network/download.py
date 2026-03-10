from PySide6.QtWidgets import QTableWidgetItem
from PySide6.QtCore import Qt
from core.utils.logging.logs import consoleLog
from core.network.libtorrent_wrapper import add_magnet
from core.utils.general.wrappers import run_thread
from core.utils.logging.logs import add_download_log
from core.network.libtorrent_int import add_seed
from core.utils.data.state import state
from core.network.direct_download import add_direct_download
import threading




def download_selected(items: list[QTableWidgetItem]):
    if not items:
        consoleLog("No item selected for download.")
        return
    seen = set()
    for item in items:
        if item.column() != 0:
            continue
        post_idx = item.data(Qt.ItemDataRole.UserRole)
        if post_idx is None:
            post_idx = item.row()
        
        if post_idx not in seen:
            seen.add(post_idx)
            post = state.posts[post_idx]
            consoleLog(f"Downloading {post.get('title', 'Unknown')}")
            run_thread(threading.Thread(target=run_download, args=(post,)))

def run_download(post):
    linkfunc = state.trackers[state.currenttracker]["linkFunc"]
    ismagnet = state.trackers[state.currenttracker]["isMagnet"]
    link = linkfunc(post)

    if ismagnet:
        add_magnet(link)
        add_download_log(post.get("title", "Unknown"), "", link, False)
    else:
        add_direct_download(link, post.get("title", "Unknown"))

def run_download_direct(magnet_uri, dl_path=None, title="Direct Download"):
    consoleLog(f"Magnet: {title}")
    add_magnet(magnet_uri, dl_path)
    add_download_log(title, "", magnet_uri, False)

def seed_magnet(magnet_uri, file_path): 
    consoleLog(f"Seeding: {magnet_uri[:60]}")
    add_seed(magnet_uri, file_path)
