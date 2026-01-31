from core.utils.data.state import state
from .config import create_config


def save_settings(thread_count=None, close=lambda: None, apiurl=None, download_path=None, down_speed_limit=None, up_speed_limit=None, image_path=None, autoresume=None):
    if thread_count is not None:
        state.aria2_threads = thread_count
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
    
    
    create_config()
    close()
