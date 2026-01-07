from core.utils.data.state import state
from core.utils.data.tracker import get_item_url
from core.utils.data.tracker import get_magnet_link
from core.network.aria2_wrapper import start_client
from core.network.aria2_wrapper import add_magnet
from core.utils.general.wrappers import run_thread
import threading


def download_selected(item, posts, post_titles):
    if item is not None:
        if state.debug:
            print(f"Downloading {item.text()}")
        run_thread(threading.Thread(target=run_download, args=(item.text(), posts, post_titles)))
    else:
        if state.debug:
            print("No item selected for download.")

def run_download(item, posts, post_titles):
    post_url = get_item_url(item, posts, post_titles)
    if state.debug:
        print("Selected URL: ", post_url)
    magnet_uri = get_magnet_link(post_url)
    start_client()
    add_magnet(magnet_uri)



