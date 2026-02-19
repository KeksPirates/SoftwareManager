from core.utils.data.models import Download, DownloadList
from core.utils.data.state import state
from dataclasses import asdict
from datetime import datetime
import json
import os
import re

_log_buffer = []


def add_download_log(title, url, magnet_uri, completed) -> DownloadList:
    downloads_file = os.path.join(state.settings_path, "downloads.json")
    
    if os.path.exists(downloads_file) and os.path.getsize(downloads_file) > 0:
        try:
            with open(downloads_file, "r") as file:
                existing_data = json.load(file)
                downloads = [Download(**d) for d in existing_data.get("data", [])]
        except json.JSONDecodeError:
            downloads = []
    else:
        downloads = []
    

    if any(d.magnet_uri == magnet_uri or d.url == url for d in downloads):
        if magnet_uri in state.active_downloads:
            consoleLog("Skipping Logging, download already running...")
            return
        consoleLog("File already in Log, updating Download State...")
        hash = extract_hash_from_magnet(magnet_uri)
        update_download_completed_by_hash(hash, False)
        return DownloadList(data=downloads, count=len(downloads)) # thanks again claude (im stupid)
        
    
    downloads.append(Download(
        title=title,
        url=url,
        magnet_uri=magnet_uri,
        completed=completed,
    ))

    consoleLog(f"Added {title} to Log File")
    
    download_list = DownloadList(data=downloads, count=len(downloads))
    with open(downloads_file, "w") as file:
        json.dump(asdict(download_list), file, indent=4)
    
    return download_list

def remove_download_log(magnet_uri) -> DownloadList:
    downloads_file = os.path.join(state.settings_path, "downloads.json")
    
    if os.path.exists(downloads_file) and os.path.getsize(downloads_file) > 0:
        try:
            with open(downloads_file, "r") as file:
                existing_data = json.load(file)
                downloads = [Download(**d) for d in existing_data.get("data", [])]
        except json.JSONDecodeError:
            downloads = []
    else:
        downloads = []

    magnet_link = (magnet_uri or "").strip()
    downloads = [d for d in downloads if (getattr(d, 'magnet_uri', None) or "").strip() != magnet_link and (getattr(d, 'url', None) or "").strip() != magnet_link]

    consoleLog(f"Removed {magnet_link} from Log File")

    download_list = DownloadList(data=downloads, count=len(downloads))
    with open(downloads_file, "w") as file:
        json.dump(asdict(download_list), file, indent=4)
    
    return download_list

def update_download_completed(magnet_uri, completed) -> DownloadList:
    downloads_file = os.path.join(state.settings_path, "downloads.json")
    
    if os.path.exists(downloads_file) and os.path.getsize(downloads_file) > 0:
        try:
            with open(downloads_file, "r") as file:
                existing_data = json.load(file)
                downloads = [Download(**d) for d in existing_data.get("data", [])]
        except (json.JSONDecodeError, TypeError) as e:
            consoleLog(f"Error loading downloads.json: {e}")
            downloads = []
    else:
        downloads = []

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
            consoleLog(f"Comparing with magnet: {stored_magnet[:50] if stored_magnet else 'None'}...")
            if identifier and (stored_magnet == identifier or stored_url == identifier):
                consoleLog(f"Match found! Setting completed={completed}")
                download.completed = completed
                found = True
        except Exception as e:
            consoleLog(f"Error comparing download: {e}")

    if not found:
        consoleLog("No matching download found to update")
        return DownloadList(data=downloads, count=len(downloads))

    download_list = DownloadList(data=downloads, count=len(downloads))
    with open(downloads_file, "w") as file:
        json.dump(asdict(download_list), file, indent=4)
    
    consoleLog("Updated download log")
    
    return download_list
    

def get_download_logs() -> DownloadList:
    downloads_file = os.path.join(state.settings_path, "downloads.json")
    
    if os.path.exists(downloads_file) and os.path.getsize(downloads_file) > 0:
        try:
            with open(downloads_file, "r") as file:
                existing_data = json.load(file)
                downloads = [Download(**d) for d in existing_data.get("data", [])]
        except json.JSONDecodeError:
            downloads = []
    else:
        downloads = []
    
    return DownloadList(data=downloads, count=len(downloads))


def extract_hash_from_magnet(magnet_uri): # full credits to claude for this
    match = re.search(r'urn:btih:([A-F0-9]+)', magnet_uri, re.IGNORECASE)
    if match:
        return match.group(1).upper()
    return None


def update_download_completed_by_hash(info_hash, completed) -> DownloadList:
    downloads_file = os.path.join(state.settings_path, "downloads.json")
    
    if os.path.exists(downloads_file) and os.path.getsize(downloads_file) > 0:
        try:
            with open(downloads_file, "r") as file:
                existing_data = json.load(file)
                downloads = [Download(**d) for d in existing_data.get("data", [])]
        except (json.JSONDecodeError, TypeError) as e:
            consoleLog(f"Error loading downloads.json: {e}")
            downloads = []
    else:
        downloads = []

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

    download_list = DownloadList(data=downloads, count=len(downloads))
    with open(downloads_file, "w") as file:
        json.dump(asdict(download_list), file, indent=4)
    
    consoleLog("Updated download log")
    
    return download_list


_main_window = None

def set_main_window(window):
    global _main_window
    _main_window = window

def flush_log_buffer(): # credits to claude
    global _log_buffer
    if _log_buffer:
        try:
            from core.interface.gui import MainWindow
            for log_entry in _log_buffer:
                MainWindow.add_log(log_entry)
            _log_buffer = []
        except Exception:
            pass

def consoleLog(text, printAnyways = False):
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    formatted_text = f"[{current_time}] {text}"

    try:
        from core.interface.gui import MainWindow
        MainWindow.add_log(formatted_text)
    except Exception:
        global _log_buffer
        _log_buffer.append(formatted_text)
    
    if state.debug or printAnyways:
        print(formatted_text)
