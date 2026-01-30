import subprocess
import libtorrent as lt
from core.utils.data.state import state
from core.utils.general.logs import consoleLog



def init_session():
    if state.dl_session is not None:
        return

    state.dl_session = lt.session()

    settings = {
        "upload_rate_limit": 0,
        "download_rate_limit": 0,
        "enable_dht": True,
        "enable_lsd": True,
        "enable_upnp": True,
        "enable_natpmp": True,
        "dht_bootstrap_nodes": "router.bittorrent.com:6881,dht.transmissionbt.com:6881",
        "connections_limit": 200,
        "active_downloads": 10
    }

    state.dl_session.apply_settings(settings)


def add_download(magnet_uri, dl_path=state.download_path):

    init_session()

    if magnet_uri in state.active_downloads:
        consoleLog("Skipping, download already running...")
        return

    consoleLog(f"Adding {magnet_uri} to downloads...")

    magnetdl = lt.parse_magnet_uri(magnet_uri)
    magnetdl.save_path = dl_path

    download = state.dl_session.add_torrent(magnetdl)
    state.active_downloads[magnet_uri] = magnetdl
