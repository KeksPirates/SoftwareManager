from core.network.libtorrent_int import update_settings
from core.utils.data.state import state
from core.utils.general.logs import consoleLog
from .config import create_config


def save_settings(close=lambda: None, apiurl=None, download_path=None, down_speed_limit=None, up_speed_limit=None, image_path=None, autoresume=None, max_connections=None, max_downloads=None, bound_interface=None):
    if apiurl is not None:
        state.api_url = apiurl
    if download_path is not None:
        state.download_path = download_path
    if down_speed_limit is not None:
        state.down_speed_limit = down_speed_limit
    if up_speed_limit is not None:
        state.up_speed_limit = up_speed_limit
    if image_path is not None:
        state.image_path = image_path
    if autoresume is not None:
        state.autoresume = autoresume
    if max_connections is not None:
        state.max_connections = max_connections
    if max_downloads is not None:
        state.max_downloads = max_downloads
    if bound_interface is not None:
        state.bound_interface = None if bound_interface == "None" else bound_interface
    

    update_settings()
    consoleLog("Saved Settings")
    create_config()
    close()
