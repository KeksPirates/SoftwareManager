from utils.data.models import Download, DownloadList
from utils.data.state import state
from dataclasses import asdict
from datetime import datetime
import json
import time
import os
import re


def _downloads_file_path() -> str:
    return os.path.join(state.settings_path, "downloads.json")

def _load_downloads() -> list[Download]:
    downloads_file = _downloads_file_path()
    if os.path.exists(downloads_file) and os.path.getsize(downloads_file) > 0:
        try:
            with open(downloads_file, "r") as file:
                existing_data = json.load(file)
                return [Download(**d) for d in existing_data.get("data", [])]
        except (json.JSONDecodeError, TypeError) as e:
            consoleLog(f"Error loading downloads.json: {e}")
    return []

def _save_downloads(downloads: list[Download]) -> DownloadList:
    download_list = DownloadList(data=downloads, count=len(downloads))
    with open(_downloads_file_path(), "w") as file:
        json.dump(asdict(download_list), file, indent=4)
    return download_list


def add_download_log(title, url, magnet_uri, completed) -> DownloadList:
    # wait for metadata outside the lock to avoid blocking other threads
    magnetdl = state.active_downloads.get(magnet_uri)
    if magnetdl:
        status = magnetdl.status()
        timeout = 60
        start = time.time()
        while not status.has_metadata and (time.time() - start) < timeout:
            time.sleep(0.5)
            status = magnetdl.status()
        torrent_name = status.name
        save_path = status.save_path
        consoleLog(f"Torrent name (has_metadata={status.has_metadata}): {torrent_name}")
        path = os.path.join(save_path, torrent_name)
    else:
        path = os.path.join(state.download_path, title)
    with state.downloads_lock:
        return _add_download_log_inner(title, url, magnet_uri, completed, path)

def _add_download_log_inner(title, url, magnet_uri, completed, path) -> DownloadList:
    downloads = _load_downloads()

    if any((magnet_uri and d.magnet_uri == magnet_uri) or (url and d.url == url) for d in downloads):
        if magnet_uri and magnet_uri in state.active_downloads:
            consoleLog("Skipping Logging, download already running...")
            return DownloadList(data=downloads, count=len(downloads))
        consoleLog("File already in Log, updating Download State...")
        hash = extract_hash_from_magnet(magnet_uri)
        if hash:
            update_download_completed_by_hash(hash, False)
        return DownloadList(data=downloads, count=len(downloads))
        
    
    downloads.append(Download(
        title=title,
        url=url,
        magnet_uri=magnet_uri,
        path=path,
        completed=completed
    ))

    consoleLog(f"Added {title} to Log File")
    return _save_downloads(downloads)

def remove_download_log(magnet_uri) -> DownloadList:
    with state.downloads_lock:
        return _remove_download_log_inner(magnet_uri)

def _remove_download_log_inner(magnet_uri) -> DownloadList:
    downloads = _load_downloads()

    magnet_link = (magnet_uri or "").strip()
    if not magnet_link:
        return DownloadList(data=downloads, count=len(downloads))

    title = next((getattr(d, 'title', 'Unknown') for d in downloads if (getattr(d, 'magnet_uri', None) or '').strip() == magnet_link or (getattr(d, 'url', None) or '').strip() == magnet_link), 'Unknown')
    downloads = [d for d in downloads if (getattr(d, 'magnet_uri', None) or "").strip() != magnet_link and (getattr(d, 'url', None) or "").strip() != magnet_link]

    consoleLog(f"Removed {title} from Log File")
    return _save_downloads(downloads)

def update_download_completed(magnet_uri, completed) -> DownloadList:
    with state.downloads_lock:
        return _update_download_completed_inner(magnet_uri, completed)

def _update_download_completed_inner(magnet_uri, completed) -> DownloadList:
    downloads = _load_downloads()

    identifier = (magnet_uri or "").strip()
    if state.debug:
        consoleLog(f"Updating download completed for identifier: {identifier!r}")
        consoleLog(f"Total downloads in file: {len(downloads)}")
        for i, d in enumerate(downloads):
            try:
                mag = (getattr(d, 'magnet_uri', None) or '')[:50]
                url = (getattr(d, 'url', None) or '')[:50]
                consoleLog(f"  [{i}] magnet: {mag}... url: {url}...")
            except Exception as e:
                consoleLog(f"  [{i}] Error reading download: {e}")

    found = False
    for download in downloads:
        try:
            stored_magnet = (getattr(download, 'magnet_uri', None) or "").strip()
            stored_url = (getattr(download, 'url', None) or "").strip()
            if identifier and (stored_magnet == identifier or stored_url == identifier):
                download.completed = completed
                found = True
        except Exception as e:
            consoleLog(f"Error comparing download: {e}")

    if not found:
        consoleLog("No matching download found to update")
        return DownloadList(data=downloads, count=len(downloads))

    consoleLog("Updated download log")
    return _save_downloads(downloads)
    

def get_download_logs() -> DownloadList:
    with state.downloads_lock:
        return _get_download_logs_inner()

def _get_download_logs_inner() -> DownloadList:
    downloads = _load_downloads()
    return DownloadList(data=downloads, count=len(downloads))


def extract_hash_from_magnet(magnet_uri):
    if not magnet_uri:
        return None
    try:
        import libtorrent as lt
        params = lt.parse_magnet_uri(magnet_uri)
        if hasattr(params, 'info_hashes'): # lt 2.0+
            return str(params.info_hashes.v1).upper()
        return str(params.info_hash).upper()
    except Exception:
        match = re.search(r'urn:btih:([a-zA-Z0-9]+)', magnet_uri)
        if match:
            return match.group(1).upper()
        return None


def update_download_completed_by_hash(info_hash, completed) -> DownloadList:
    with state.downloads_lock:
        return _update_download_completed_by_hash_inner(info_hash, completed)

def _update_download_completed_by_hash_inner(info_hash, completed) -> DownloadList:
    downloads = _load_downloads()

    info_hash_upper = (info_hash or "").upper().strip()
    consoleLog(f"Updating download by hash: {info_hash_upper}")
    consoleLog(f"Total downloads in file: {len(downloads)}")

    found = False
    for download in downloads:
        try:
            magnet_uri = getattr(download, 'magnet_uri', None)
            if magnet_uri:
                stored_hash = extract_hash_from_magnet(magnet_uri)
                if stored_hash and stored_hash == info_hash_upper:
                    download.completed = completed
                    found = True
        except Exception as e:
            consoleLog(f"Error comparing download: {e}")

    if not found:
        consoleLog("No matching download found to update")
        return DownloadList(data=downloads, count=len(downloads))

    consoleLog("Updated download log")
    return _save_downloads(downloads)


def set_main_window(window):
    state.main_window = window

def flush_log_buffer(): # credits to claude
    if state.log_buffer:
        try:
            from interface.gui import MainWindow
            for log_entry in state.log_buffer:
                MainWindow.add_log(log_entry)
            state.log_buffer = []
        except Exception as e:
            consoleLog(f"Exception while flushing log buffer: {e}")

def consoleLog(text, printAnyways = False):
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    formatted_text = f"[{current_time}] {text}"

    try:
        from interface.gui import MainWindow
        if not MainWindow.add_log(formatted_text):
            state.log_buffer.append(formatted_text)
    except Exception:
        state.log_buffer.append(formatted_text)
    
    if state.debug or printAnyways:
        print(formatted_text)
