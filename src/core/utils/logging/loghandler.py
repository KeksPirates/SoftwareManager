from core.utils.logging.logs import consoleLog, remove_download_log
from core.utils.network.download import run_download_direct

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
                run_download_direct(download.magnet_uri)
                consoleLog(f"Resuming {download.title}")

def check_downloads(downloads):
    for download in downloads:
        if os.path.exists(download.path):
            consoleLog(f"Existing Download: {download.title}")
        else:
            consoleLog(f"Inexistent Download: {download.title}")
            remove_download_log(download.magnet_uri)
            