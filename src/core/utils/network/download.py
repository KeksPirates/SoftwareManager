from PySide6.QtWidgets import QTableWidgetItem
from core.utils.logging.logs import consoleLog
from core.network.libtorrent_wrapper import add_magnet
from core.utils.general.wrappers import run_thread
from core.utils.logging.logs import add_download_log
from core.network.libtorrent_int import add_seed
from core.utils.data.state import state
from urllib.parse import urlparse, unquote
import threading
import re
import requests
import random


def download_selected(items: list[QTableWidgetItem]):
    if not items:
        consoleLog("No item selected for download.")
        return
    seen = set()
    for item in items:
        if item.column() != 0:
            continue
        text = item.text()
        if text != "" and text not in seen:
            seen.add(text)
            consoleLog(f"Downloading {text}")
            run_thread(threading.Thread(target=run_download, args=(state.posts[item.row()],)))

def get_direct_filename(url: str, headers) -> str:
    cd = headers.get('content-disposition', '')
    if cd:
        match = re.search(r'filename\*=UTF-8\'\'(.+)', cd)  # RFC 5987 encoded
        if match:
            return unquote(match.group(1))
        match = re.search(r'filename="?([^";\n]+)"?', cd)
        if match:
                return match.group(1).strip()

    path = urlparse(url).path
    name = path.split('/')[-1]
    if name:
        return unquote(name)

    return f"download{random.randint(1,9999)}" #avoid collision

def filedownload(url):
    try:
        with requests.get(url, stream=True, timeout=30) as r:
            r.raise_for_status()
            name = get_direct_filename(url, r.headers)

            with open(state.download_path + f"/{name}", 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)

        consoleLog(f"Finished downloading {name}")
    except Exception as e:
        consoleLog(f"Error downloading: {e}")

def run_download(post):
    linkfunc = state.trackers[state.currenttracker]["linkFunc"]
    ismagnet = state.trackers[state.currenttracker]["isMagnet"]
    link = linkfunc(post)

    if ismagnet:
        add_magnet(link)
    else:
        filedownload(link)

def run_download_direct(magnet_uri):
    consoleLog(f"Direct download: {magnet_uri[:60]}")
    add_magnet(magnet_uri)
    add_download_log("Direct Download", "", magnet_uri, False)

def seed_magnet(magnet_uri, file_path): 
    consoleLog(f"Seeding: {magnet_uri[:60]}")
    add_seed(magnet_uri, file_path)
