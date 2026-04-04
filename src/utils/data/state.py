from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QTableWidget
from typing import Any, List, Dict
from pathlib import Path
import threading

class AppState(QObject):
    image_changed = Signal(str)

    def __init__(self):
        super().__init__()

        # General
        self.version: str = "Unknown"
        self.debug: bool = False
        self.main_window: Any = None
        self.loop_running: bool = False
        self.shutdown_event = threading.Event()
        self.log_buffer: List[str] = []

        # Paths
        self.settings_path: str = ""
        self._image_path: str = ""
        self.download_path: str = str(Path.home() / "Downloads")

        # GUI
        self.window_transparency: bool = False
        self.trackertable: QTableWidget
        self.interfaces: List = []
        self.active_interfaces: List = []
        self.bound_interface: Any = None

        # Image
        self._image_enabled: bool = False
        self._image_width: int = 300 # Default to 300px
        self._image_offset: int = 50
        self._image_opacity: int = 100

        # Trackers / Scraping
        self.posts: list[Dict[str,str]] | None = None  # titles, urls, author, seeders, leechers
        self.currenttracker: str = "rutracker"
        self.api_url: str = "https://api.michijackson.xyz"
        self.trackers: Dict[str,Dict[str,Any]] = {}

        # LibTorrent / Download related stuff
        self.dl_session: Any = None
        self.active_downloads: Dict = {}
        self.seeded_magnets: set = set()
        self.ignore_updates: bool = False
        self.autoresume: bool = True
        self.up_speed_limit: int = 0
        self.down_speed_limit: int = 0
        self.max_connections: int = 200
        self.max_downloads: int = 10
        self.downloads_lock = threading.RLock()

    @property
    def image_path(self) -> str:
        return self._image_path

    @image_path.setter
    def image_path(self, new_path: str):
        if new_path != self._image_path:
            self._image_path = new_path
            self.image_changed.emit(new_path)

    @property
    def image_offset(self) -> int:
        return self._image_offset

    @image_offset.setter
    def image_offset(self, new_offset: int):
        if new_offset != self._image_offset:
            self._image_offset = new_offset
            self.image_changed.emit(self._image_path)

    @property
    def image_width(self) -> int:
        return self._image_width

    @image_width.setter
    def image_width(self, new_width: int):
        if new_width != self._image_width:
            self._image_width = new_width
            self.image_changed.emit(self._image_path)

    @property
    def image_opacity(self) -> int:
        return self._image_opacity

    @image_opacity.setter
    def image_opacity(self, new_opacity: int):
        if new_opacity != self._image_opacity:
            self._image_opacity = new_opacity
            self.image_changed.emit(self._image_path)

    @property
    def image_enabled(self) -> bool:
        return self._image_enabled

    @image_enabled.setter
    def image_enabled(self, new_state: bool):
        if new_state != self._image_enabled:
            self._image_enabled = new_state
            self.image_changed.emit(self._image_path)

state = AppState()
