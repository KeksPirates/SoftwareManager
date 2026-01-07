from core.utils.data.models import Download, DownloadList
import json




def add_download_log(title, url, magnet_uri, completed) -> DownloadList:
    downloads: list[Download] = []
    downloads.append(Download(
        title=title,
        url=url,
        magnet_uri=magnet_uri,
        completed=completed
    ))

    return DownloadList(data=downloads, count=len(downloads))