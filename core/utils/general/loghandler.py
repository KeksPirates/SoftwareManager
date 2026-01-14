from core.utils.data.state import state
from core.utils.general.logs import consoleLog
from core.utils.network.download import run_download_direct

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

            


