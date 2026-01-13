from core.utils.data.state import state
from core.utils.network.download import run_download_direct

def split_data(data):

    count = data.count
    downloads = data.data

    return count, downloads

def check_completed(downloads, resume):
    for download in downloads:
        if download.completed == False:
            if state.debug:
                print(f"Found unfinished download: {download.title}")
            if resume == True:
                run_download_direct(download.magnet_uri)
                if state.debug:
                    print(f"Resuming {download.title}")

            


