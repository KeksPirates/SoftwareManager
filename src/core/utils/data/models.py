from dataclasses import dataclass
from typing import List


@dataclass
class Download:
    title: str
    url: str
    magnet_uri: str
    path: str
    completed: bool

@dataclass
class DownloadList:
    count: int
    data: List[Download]