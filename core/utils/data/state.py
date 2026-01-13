from PySide6.QtCore import QObject, Signal
from typing import Optional, Any, List, Dict
from pathlib import Path

class AppState(QObject):
    image_changed = Signal(str)

    def __init__(self):
        super().__init__()
        self.posts: List[Dict[str, Any]] = []
        self.post_titles: List[str] = []
        self.post_urls: List[str] = []
        self.post_author: List[str] = []
        self.downloads: List[str] = []
        self.version: str = "dev"
        self._image_path: str = ""
        self.ignore_updates: bool = False
        self.debug: bool = False
        self.autoresume: bool = True
        self.tracker: str = "rutracker"
        self.api_url: str = "https://api.michijackson.xyz"
        self.download_path: str = str(Path.home() / "Downloads")
        self.speed_limit: int = 0
        self.aria2process: Optional[Any] = None
        self.aria2: Any = None
        self.aria2p: Any = None
        self.aria2_threads: int = 4
        self.settings_path: str = None

    @property
    def image_path(self) -> str:
        return self._image_path

    @image_path.setter
    def image_path(self, new_path: str):
        if new_path != self._image_path:
            self._image_path = new_path
            self.image_changed.emit(new_path)

state = AppState()
