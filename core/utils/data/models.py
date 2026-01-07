from dataclasses import dataclass
from typing import List


@dataclass
class Download:
    title: str
    url: str
    torrent_uri: str
    completed: bool

@dataclass
class DownloadList:
    count: int
    data: List[Download]