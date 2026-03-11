from typing import Optional
from core.utils.data.state import state
from core.utils.logging.logs import consoleLog, add_download_log

from .handle import DirectDownloadHandle
from .utils import (
    sanitize_filename,
    extract_filename_from_url,
    detect_filename_from_headers,
)

def add_direct_download(url: str, title: str, dl_path: Optional[str] = None, headers: Optional[dict] = None, single_threaded: bool = False):

    if dl_path is None:
        dl_path = state.download_path

    if url in state.active_downloads:
        consoleLog(f"Download already active: {title}")
        return

    filename = (
        detect_filename_from_headers(url, DirectDownloadHandle.USER_AGENT)
        or extract_filename_from_url(url)
        or sanitize_filename(title) + ".zip"
    )

    handle = DirectDownloadHandle(url, filename, dl_path, headers, single_threaded)
    state.active_downloads[url] = handle
    add_download_log(title, url, "", False)
    handle.start()
    consoleLog(f"Started direct download: {filename}")
