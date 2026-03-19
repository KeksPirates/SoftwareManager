from network.direct_download.status import DirectDownloadStatus, ChunkSpec
from utils.logging.logs import consoleLog, update_download_completed
from concurrent.futures import ThreadPoolExecutor, as_completed
from network.direct_download.utils import format_size
from utils.data.state import state
from typing import Optional
import libtorrent as lt
import threading
import requests
import hashlib
import json
import time
import os


class SimpleThrottler:
    def __init__(self):
        self._lock = threading.Lock()
        self._last_time = time.monotonic()
        self._allowance = 0.0

    def throttle(self, bytes_count: int, limit_kbps: int):
        if limit_kbps <= 0:
            return

        limit_bps = limit_kbps * 1024
        wait_time = 0
        with self._lock:
            now = time.monotonic()
            elapsed = now - self._last_time
            self._last_time = now
            
            self._allowance += elapsed * limit_bps
            if self._allowance > 2 * limit_bps:
                self._allowance = 2 * limit_bps
                
            self._allowance -= bytes_count
            
            if self._allowance < 0:
                wait_time = -self._allowance / limit_bps
                self._allowance = 0
        
        if wait_time > 0:
            time.sleep(min(wait_time, 1.0))

_throttler = SimpleThrottler()

class DirectDownloadHandle:
    STREAM_BLOCK_SIZE = 1 << 17  # 128 KiB per read
    MAX_RETRIES = 5
    RETRY_BACKOFF_BASE = 2.0
    NUM_THREADS = 16
    MIN_CHUNK_SIZE = 1 << 20  # 1 MiB minimum per chunk
    REQUEST_TIMEOUT = (15, 60)  # (connect, read) timeouts
    USER_AGENT = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    )

    def __init__(self, url: str, name: str, save_path: str, headers: Optional[dict] = None, single_threaded: bool = False):
        self.url = url
        self._name = name
        self._save_path = save_path
        self._file_path = os.path.join(save_path, name)
        self._status = DirectDownloadStatus(name, save_path, 0)
        self._stop_event = threading.Event()
        self._pause_event = threading.Event()  # SET = paused
        self._thread: Optional[threading.Thread] = None
        self._session: Optional[requests.Session] = None
        self._supports_range = False
        self._custom_headers = headers
        self._single_threaded = single_threaded
        
        state_dir = os.path.join(state.settings_path, "direct_downloads")
        os.makedirs(state_dir, exist_ok=True)
        url_hash = hashlib.sha256(url.encode()).hexdigest()
        self._state_file = os.path.join(state_dir, f"{url_hash}.json")
        
        # Load state to initialize progress
        state_data = self._load_state()
        if state_data:
            total_wanted = state_data.get("total_wanted", 0)
            chunks_progress = state_data.get("chunks", {})
            chunks_progress = {int(k): int(v) for k, v in chunks_progress.items()}
            self._status.initialize_progress(total_wanted, chunks_progress)


    def status(self) -> DirectDownloadStatus:
        return self._status

    def pause(self):
        self._status.paused = True
        self._pause_event.set()

    def resume(self):
        self._status.paused = False
        self._pause_event.clear()

    def set_flags(self, flags):
        if flags & lt.torrent_flags.auto_managed:
            self._status.auto_managed = True

    def unset_flags(self, flags):
        if flags & lt.torrent_flags.auto_managed:
            self._status.auto_managed = False

    def save_path(self) -> str:
        return self._save_path

    def stop(self):
        self._stop_event.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=10)


    def _load_state(self) -> dict:
        if os.path.exists(self._state_file):
            try:
                with open(self._state_file, "r") as f:
                    return json.load(f)
            except Exception as e:
                consoleLog(f"Failed to load state for {self._name}: {e}")
        return {}

    def _save_state(self, chunks_done: dict[int, int]):
        try:
            with open(self._state_file, "w") as f:
                json.dump({
                    "url": self.url,
                    "name": self._name,
                    "save_path": self._save_path,
                    "total_wanted": self._status.total_wanted,
                    "chunks": chunks_done
                }, f)
        except Exception as e:
            consoleLog(f"Exception while saving download state: {e}")

    def _clear_state(self):
        if os.path.exists(self._state_file):
            try:
                os.remove(self._state_file)
            except Exception as e:
                consoleLog(f"Exception while removing download state file: {e}")


    def start(self):
        self._thread = threading.Thread(
            target=self._download_orchestrator, name=f"dl-{self._name}", daemon=True
        )
        self._thread.start()

    def _build_session(self) -> requests.Session:
        session = requests.Session()
        session.headers.update({"User-Agent": self.USER_AGENT})
        if self._custom_headers is not None:
            session.headers.update(self._custom_headers)
        adapter = requests.adapters.HTTPAdapter(
            max_retries=0,
            pool_connections=self.NUM_THREADS,
            pool_maxsize=self.NUM_THREADS + 2,
        )
        session.mount("https://", adapter)
        session.mount("http://", adapter)
        return session

    def _probe_url(self, session: requests.Session) -> tuple[int, bool]:
        resp = session.head(self.url, allow_redirects=True, timeout=self.REQUEST_TIMEOUT)
        resp.raise_for_status()

        total_size = int(resp.headers.get("content-length", 0))
        supports_range = (total_size > 0)

        # Double-check range support with a small range request
        if supports_range:
            try:
                test = session.get(
                    self.url,
                    headers={"Range": "bytes=0-0"},
                    timeout=self.REQUEST_TIMEOUT,
                    stream=True,
                )
                supports_range = test.status_code == 206
                test.close()
            except Exception:
                supports_range = False

        return total_size, supports_range

    def _download_orchestrator(self):
        try:
            self._session = self._build_session()
            total_size, self._supports_range = self._probe_url(self._session)
            self._status.total_wanted = total_size

            os.makedirs(self._save_path, exist_ok=True)

            use_multithreaded = (
                self._supports_range
                and total_size > self.MIN_CHUNK_SIZE * 2
                and not self._single_threaded
            )

            if use_multithreaded:
                consoleLog(
                    f"Multi-threaded download ({self.NUM_THREADS} threads): {self._name} "
                    f"({format_size(total_size)})"
                )
                self._preallocate_file(total_size)
                self._multithreaded_download(total_size)
            else:
                reason = "no range support" if not self._supports_range else "file too small or single-threaded mode"
                consoleLog(f"Single-threaded download ({reason}): {self._name}")
                self._single_threaded_download()

            if not self._stop_event.is_set() and self._status.error is None:
                self._verify_download(total_size)
                self._status.mark_completed()
                update_download_completed(self.url, True)
                self._clear_state()
                consoleLog(f"Finished downloading {self._name}")

        except Exception as e:
            self._status.mark_error(str(e))
            consoleLog(f"Download failed for {self._name}: {e}")
        finally:
            if self._session:
                self._session.close()


    def _preallocate_file(self, total_size: int):
        if os.path.exists(self._file_path) and os.path.getsize(self._file_path) == total_size:
            return
        with open(self._file_path, "wb") as f:
            f.truncate(total_size)

    def _compute_chunks(self, total_size: int) -> list[ChunkSpec]:
        num_chunks = min(self.NUM_THREADS, max(1, total_size // self.MIN_CHUNK_SIZE))
        chunk_size = total_size // num_chunks
        chunks = []
        for i in range(num_chunks):
            start = i * chunk_size
            end = (i + 1) * chunk_size - 1 if i < num_chunks - 1 else total_size - 1
            chunks.append(ChunkSpec(chunk_id=i, start=start, end=end))
        return chunks

    def _multithreaded_download(self, total_size: int):
        chunks = self._compute_chunks(total_size)
        state_data = self._load_state()
        chunks_progress = state_data.get("chunks", {})
        
        chunks_progress = {int(k): int(v) for k, v in chunks_progress.items()}

        # Initialize progress in status
        for chunk_id, bytes_done in chunks_progress.items():
            self._status.update_chunk_progress(chunk_id, bytes_done)

        with ThreadPoolExecutor(
            max_workers=len(chunks), thread_name_prefix="dl-chunk"
        ) as executor:
            futures = {
                executor.submit(self._download_chunk_with_retry, chunk, chunks_progress.get(chunk.chunk_id, 0)): chunk
                for chunk in chunks
            }

            for future in as_completed(futures):
                chunk = futures[future]
                try:
                    future.result()
                except Exception as e:
                    consoleLog(
                        f"Chunk {chunk.chunk_id} ({chunk.start}-{chunk.end}) "
                        f"failed permanently: {e}"
                    )
                    self._status.mark_error(
                        f"Chunk {chunk.chunk_id} failed: {e}"
                    )
                    self._stop_event.set()

    def _download_chunk_with_retry(self, chunk: ChunkSpec, initial_bytes: int):
        bytes_written = initial_bytes

        for attempt in range(1, self.MAX_RETRIES + 1):
            if self._stop_event.is_set():
                return

            current_start = chunk.start + bytes_written
            if current_start > chunk.end:
                return

            try:
                # _download_range returns new bytes written
                bytes_written += self._download_range(
                    chunk.chunk_id, current_start, chunk.end, bytes_written
                )
                return
            except Exception as e:
                if self._stop_event.is_set():
                    return
                if attempt < self.MAX_RETRIES:
                    wait = self.RETRY_BACKOFF_BASE ** attempt
                    consoleLog(
                        f"Chunk {chunk.chunk_id} attempt {attempt} failed: {e}. "
                        f"Retrying in {wait:.0f}s (resuming from byte {current_start})..."
                    )
                    if self._stop_event.wait(timeout=wait):
                        return
                else:
                    raise RuntimeError(
                        f"Chunk {chunk.chunk_id} failed after {self.MAX_RETRIES} attempts: {e}"
                    ) from e

    def _download_range(
        self, chunk_id: int, start: int, end: int, prior_bytes: int
    ) -> int:

        headers = {"Range": f"bytes={start}-{end}"}
        new_bytes = 0

        with self._session.get(
            self.url, headers=headers, stream=True, timeout=self.REQUEST_TIMEOUT
        ) as resp:
            resp.raise_for_status()
            if resp.status_code not in (200, 206):
                raise RuntimeError(f"Unexpected status {resp.status_code}")

            with open(self._file_path, "r+b") as f:
                f.seek(start)
                for block in resp.iter_content(chunk_size=self.STREAM_BLOCK_SIZE):
                    if self._stop_event.is_set():
                        return new_bytes

                    self._wait_if_paused()
                    if self._stop_event.is_set():
                        return new_bytes

                    _throttler.throttle(len(block), state.down_speed_limit)

                    f.write(block)
                    new_bytes += len(block)
                    self._status.update_chunk_progress(
                        chunk_id, prior_bytes + new_bytes
                    )
                    

                    if new_bytes % (1024 * 1024) < len(block):

                        with self._status._lock:
                            self._save_state(self._status._chunk_bytes)

        with self._status._lock:
            self._save_state(self._status._chunk_bytes)
            
        return new_bytes


    def _single_threaded_download(self):
        chunk_id = 0
        bytes_written = 0
        
        if os.path.exists(self._file_path):
            bytes_written = os.path.getsize(self._file_path)
            if bytes_written > 0:
                self._status.update_chunk_progress(chunk_id, bytes_written)

        for attempt in range(1, self.MAX_RETRIES + 1):
            if self._stop_event.is_set():
                return

            try:
                headers = {}
                mode = "wb"

                if bytes_written > 0 and self._supports_range:
                    headers["Range"] = f"bytes={bytes_written}-"
                    mode = "r+b"
                elif bytes_written > 0:
                    bytes_written = 0
                    mode = "wb"

                with self._session.get(
                    self.url, headers=headers, stream=True, timeout=self.REQUEST_TIMEOUT
                ) as resp:
                    resp.raise_for_status()

                    if self._status.total_wanted == 0:
                        content_length = int(resp.headers.get("content-length", 0))
                        self._status.total_wanted = content_length + bytes_written

                    with open(self._file_path, mode) as f:
                        if mode == "r+b":
                            f.seek(bytes_written)

                        for block in resp.iter_content(
                            chunk_size=self.STREAM_BLOCK_SIZE
                        ):
                            if self._stop_event.is_set():
                                return

                            self._wait_if_paused()
                            if self._stop_event.is_set():
                                return

                            _throttler.throttle(len(block), state.down_speed_limit)

                            f.write(block)
                            bytes_written += len(block)
                            self._status.update_chunk_progress(chunk_id, bytes_written)
                            
                            # Periodic state save (single thread, chunk_id=0)
                            if bytes_written % (1024 * 1024) < len(block):
                                self._save_state({0: bytes_written})

                self._save_state({0: bytes_written})
                return

            except Exception as e:
                if self._stop_event.is_set():
                    return
                if attempt < self.MAX_RETRIES:
                    wait = self.RETRY_BACKOFF_BASE ** attempt
                    consoleLog(
                        f"Download attempt {attempt} failed: {e}. "
                        f"Retrying in {wait:.0f}s..."
                    )
                    if self._stop_event.wait(timeout=wait):
                        return
                else:
                    raise RuntimeError(
                        f"Download failed after {self.MAX_RETRIES} attempts: {e}"
                    ) from e


    def _wait_if_paused(self):
        while self._pause_event.is_set():
            if self._stop_event.wait(timeout=0.5):
                return

    def _verify_download(self, expected_size: int):
        if expected_size <= 0:
            return
        actual_size = os.path.getsize(self._file_path)
        if actual_size != expected_size:
            raise RuntimeError(
                f"Size mismatch: expected {format_size(expected_size)}, "
                f"got {format_size(actual_size)}"
            )