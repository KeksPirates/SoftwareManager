from core.utils.logging.logs import consoleLog
from core.network.libtorrent_int import add_download

def add_magnet(uri, dl_path=None):
    if uri is not None and uri.startswith("magnet:?"):  
        if dl_path:
            add_download(uri, dl_path)
        else:
            add_download(uri)
        consoleLog("Magnet URI added to LibTorrent")
    else:
        consoleLog(f"Invalid Magnet Link: {uri}")