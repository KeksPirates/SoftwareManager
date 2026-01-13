from core.utils.data.models import Download, DownloadList
from core.utils.data.state import state
from dataclasses import asdict
import json
import os
import re


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
        if state.debug:
            print("Skipped Logging, download already in file")
        return DownloadList(data=downloads, count=len(downloads)) # thanks again claude (im stupid)
        
    
    downloads.append(Download(
        title=title,
        url=url,
        magnet_uri=magnet_uri,
        completed=completed,
    ))

    if state.debug:
        print(f"Added {title} to Log File")
    
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
            if state.debug:
                print(f"Error loading downloads.json: {e}")
            downloads = []
    else:
        downloads = []

    identifier = (magnet_uri or "").strip()
    if state.debug:
        print(f"Updating download completed for identifier: {identifier!r}")
        print(f"Total downloads in file: {len(downloads)}")
        for i, d in enumerate(downloads):
            try:
                mag = (getattr(d, 'magnet_uri', None) or '')[:50]
                url = (getattr(d, 'url', None) or '')[:50]
                print(f"  [{i}] magnet: {mag}... url: {url}...")
            except Exception as e:
                print(f"  [{i}] Error reading download: {e}")

    found = False
    for download in downloads:
        try:
            stored_magnet = (getattr(download, 'magnet_uri', None) or "").strip()
            stored_url = (getattr(download, 'url', None) or "").strip()
            if state.debug:
                print(f"Comparing with magnet: {stored_magnet[:50] if stored_magnet else 'None'}...")
            if identifier and (stored_magnet == identifier or stored_url == identifier):
                if state.debug:
                    print(f"Match found! Setting completed={completed}")
                download.completed = completed
                found = True
        except Exception as e:
            if state.debug:
                print(f"Error comparing download: {e}")

    if not found:
        if state.debug:
            print("No matching download found to update")
        return DownloadList(data=downloads, count=len(downloads))

    download_list = DownloadList(data=downloads, count=len(downloads))
    with open(downloads_file, "w") as file:
        json.dump(asdict(download_list), file, indent=4)
    
    if state.debug:
        print("Updated download log")
    
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
            if state.debug:
                print(f"Error loading downloads.json: {e}")
            downloads = []
    else:
        downloads = []

    info_hash_upper = (info_hash or "").upper().strip()
    if state.debug:
        print(f"Updating download by hash: {info_hash_upper}")
        print(f"Total downloads in file: {len(downloads)}")

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
            if state.debug:
                print(f"Error comparing download: {e}")

    if not found:
        if state.debug:
            print("No matching download found to update")
        return DownloadList(data=downloads, count=len(downloads))

    download_list = DownloadList(data=downloads, count=len(downloads))
    with open(downloads_file, "w") as file:
        json.dump(asdict(download_list), file, indent=4)
    
    if state.debug:
        print("Updated download log")
    
    return download_list