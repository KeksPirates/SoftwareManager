from dataclasses import dataclass
from typing import Optional
import libtorrent as lt
import threading
import time


@dataclass
class ChunkSpec:
    chunk_id: int
    start: int
    end: int  # inclusive


class DirectDownloadStatus:

    def __init__(self, name: str, save_path: str, total_size: int = 0):
        self.name = name
        self.save_path = save_path
        self.total_wanted = total_size
        self.paused = False
        self.auto_managed = True
        self.has_metadata = True
        self.state = lt.torrent_status.downloading
        self.error: Optional[str] = None

        self._lock = threading.Lock()
        self._total_wanted_done = 0
        self._progress = 0.0
        self._download_rate = 0
        self._upload_rate = 0

        self._chunk_bytes: dict[int, int] = {}  
        self._speed_window: list[tuple[float, int]] = [] 
        self._speed_window_size = 3.0

    @property
    def total_wanted_done(self) -> int:
        with self._lock:
            return self._total_wanted_done

    @property
    def progress(self) -> float:
        with self._lock:
            return self._progress

    @property
    def download_rate(self) -> int:
        with self._lock:
            return self._download_rate

    @property
    def upload_rate(self) -> int:
        return 0

    def update_chunk_progress(self, chunk_id: int, bytes_downloaded: int):
        with self._lock:
            self._chunk_bytes[chunk_id] = bytes_downloaded
            self._total_wanted_done = sum(self._chunk_bytes.values())
            if self.total_wanted > 0:
                self._progress = min(self._total_wanted_done / self.total_wanted, 1.0)


            now = time.monotonic()
            self._speed_window.append((now, self._total_wanted_done))

            cutoff = now - self._speed_window_size
            self._speed_window = [
                (t, b) for t, b in self._speed_window if t >= cutoff
            ]
            if len(self._speed_window) >= 2:
                oldest_time, oldest_bytes = self._speed_window[0]
                dt = now - oldest_time
                if dt > 0:
                    self._download_rate = int(
                        (self._total_wanted_done - oldest_bytes) / dt
                    )

    def initialize_progress(self, total_wanted: int, chunk_bytes: dict[int, int]):
        with self._lock:
            self.total_wanted = total_wanted
            self._chunk_bytes = chunk_bytes.copy()
            self._total_wanted_done = sum(self._chunk_bytes.values())
            if self.total_wanted > 0:
                self._progress = min(self._total_wanted_done / self.total_wanted, 1.0)

    def mark_completed(self):
        with self._lock:
            self.state = lt.torrent_status.seeding
            self._progress = 1.0
            self._download_rate = 0

    def mark_error(self, error: str):
        with self._lock:
            self.error = error
            self._download_rate = 0
