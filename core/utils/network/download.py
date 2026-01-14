from core.utils.data.state import state
from core.utils.general.logs import consoleLog
from core.utils.data.tracker import get_item_url
from core.utils.data.tracker import get_magnet_link
from core.network.aria2_wrapper import start_client
from core.network.aria2_wrapper import add_magnet
from core.utils.general.wrappers import run_thread
from core.utils.general.logs import add_download_log

import threading


def download_selected(item, posts, post_titles):
    if item is not None:
        consoleLog(f"Downloading {item.text()}")
        run_thread(threading.Thread(target=run_download, args=(item.text(), posts, post_titles)))
    else:
        consoleLog("No item selected for download.")

def run_download(item, posts, post_titles):
    post_url = get_item_url(item, posts, post_titles)
    consoleLog(f"Selected URL: {post_url}")
    magnet_uri = get_magnet_link(post_url)
    start_client()
    add_download_log(item, post_url, magnet_uri, False)
    add_magnet(magnet_uri)

def run_download_direct(magnet_uri):
    start_client()
    add_magnet(magnet_uri)    



