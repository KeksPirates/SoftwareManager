from core.utils.data.models import Download, DownloadList
from core.utils.data.state import state
from dataclasses import asdict
import json
import os


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
    
    downloads.append(Download(
        title=title,
        url=url,
        magnet_uri=magnet_uri,
        completed=completed
    ))
    
    download_list = DownloadList(data=downloads, count=len(downloads))
    with open(downloads_file, "w") as file:
        json.dump(asdict(download_list), file, indent=4)
    
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