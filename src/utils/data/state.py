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

        # Trackers / Scraping
        self.posts: list[Dict[str,str]] | None = None  # titles, urls, author, seeders, leechers
        self.currenttracker: str = "rutracker"
        self.api_url: str = "https://api.michijackson.xyz"
        self.trackers: Dict[str,Dict[str,Any]] = {}  # each tracker should add itself here
        # an example:
        # "rutracker" : {
        #     "name" : "rutracker",
        #     "headers" : ["author", "title"],
        #     "scrapeFunc" : function,
        # }

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

state = AppState()
