from core.utils.logging.logs import consoleLog
from core.utils.data.tracker import get_item_url
from core.utils.data.tracker import get_magnet_link
from core.network.libtorrent_wrapper import add_download
from core.utils.general.wrappers import run_thread
from core.utils.logging.logs import add_download_log
from core.network.libtorrent_int import add_seed
import threading


def download_selected(items, posts, post_titles):
    if not items:
        consoleLog("No item selected for download.")
        return
    seen = set()
    for item in items:
        if item.column() != 0:
            continue
        text = item.text()
        if text and text not in seen:
            seen.add(text)
            consoleLog(f"Downloading {text}")
            run_thread(threading.Thread(target=run_download, args=(text, posts, post_titles)))

def run_download(item, posts, post_titles):
    post_url = get_item_url(item, posts, post_titles)
    consoleLog(f"Selected URL: {post_url}")
    magnet_uri = get_magnet_link(post_url)

    if add_download(magnet_uri):
        add_download_log(item, post_url, magnet_uri, False)

def run_download_direct(magnet_uri):
    consoleLog(f"Direct download: {magnet_uri[:60]}")
    add_download(magnet_uri)
    add_download_log("Direct Download", "", magnet_uri, False)

def seed_magnet(magnet_uri, file_path): 
    consoleLog(f"Seeding: {magnet_uri[:60]}")
    add_seed(magnet_uri, file_path)