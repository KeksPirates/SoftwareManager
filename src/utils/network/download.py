from network.direct_download import add_direct_download
from network.libtorrent_wrapper import add_magnet
from PySide6.QtWidgets import QTableWidgetItem
from utils.logging.logs import add_download_log
from utils.general.wrappers import run_thread
from network.libtorrent_int import add_seed
from utils.logging.logs import consoleLog
from utils.data.state import state
from PySide6.QtCore import Qt
from typing import Optional
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

def run_download(post, headers: Optional[dict] = None):
    link_method = state.trackers[state.currenttracker].get_download_link
    ismagnet = state.trackers[state.currenttracker].is_magnet
    result = link_method(post)

    if ismagnet:
        link = result
        if not link:
            consoleLog("Failed to retrieve magnet link")
            return
        add_magnet(link)
        add_download_log(post.get("title", "Unknown"), "", link, False)
    else:
        link, link_headers = result if isinstance(result, tuple) else (result, None)
        if not link:
            consoleLog("Failed to retrieve download link")
            return
        final_headers = headers or link_headers
        add_direct_download(link, post.get("title", "Unknown"), headers=final_headers, single_threaded=final_headers is not None)

def run_download_direct(magnet_uri, title="Direct Download"):
    consoleLog(f"Magnet: {title}")
    add_magnet(magnet_uri)
    add_download_log(title, "", magnet_uri, False)

def seed_magnet(magnet_uri, file_path): 
    consoleLog(f"Seeding: {magnet_uri[:60]}")
    add_seed(magnet_uri, file_path)
