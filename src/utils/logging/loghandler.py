from utils.network.download import run_download_direct, seed_magnet
from utils.logging.logs import consoleLog, remove_download_log
import os

def split_data(data):

    count = data.count
    downloads = data.data

    return count, downloads

def check_completed(downloads, resume):
    for download in downloads:
        if download.completed == False:
            consoleLog(f"Found unfinished download: {download.title}")
            if resume == True:
                if download.magnet_uri:
                    run_download_direct(download.magnet_uri, download.title)
                    consoleLog(f"Resuming Magnet: {download.title}")
                elif download.url:
                    from network.direct_download import add_direct_download
                    add_direct_download(download.url, download.title)
                    consoleLog(f"Resuming Direct Download: {download.title}")

def check_downloads(downloads):
    for download in downloads:
        if download.completed == True and os.path.exists(download.path):
            consoleLog(f"Existing Download: {download.title}")
            try:
                seed_magnet(download.magnet_uri, download.path)
            except Exception as e:
                consoleLog(f"Failed to seed {download.title}: {e}")
        elif download.completed == True and not os.path.exists(download.path):
            consoleLog(f"Inexistent Download: {download.title}")
            remove_download_log(download.magnet_uri)
            