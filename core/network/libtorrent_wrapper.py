from core.utils.general.logs import consoleLog
from core.network.libtorrent_int import add_download, dl_status_loop

def add_magnet(uri):
    if uri is not None and uri.startswith("magnet:?"):  
        add_download(uri)
        consoleLog("Magnet URI added to LibTorrent")
    else:
        consoleLog(f"Invalid Magnet Link: {uri}")



