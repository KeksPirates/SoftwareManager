from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QTableWidget
from typing import Any, List, Dict
from pathlib import Path

class AppState(QObject):
    image_changed = Signal(str)

    def __init__(self):
        super().__init__()
        self.posts: list[Dict[str,str]] | None = None # titles, urls, author, seederm leecher
        self.version: str = "dev"
        self._image_path: str = ""
        self.ignore_updates: bool = False
        self.debug: bool = False
        self.autoresume: bool = True

        self.currenttracker: str = "rutracker"
        self.trackertable: QTableWidget
        self.trackers: Dict[str,Dict[str,Any]] # each tracker should add itself here, will be listed in order of module initialisation
        '''
        an example:
        "rutracker" : {
            "name" : "rutracker", # name of the tracker
            "posts" : [post1, post2, ...], # all the posts, will be in self.posts,
            "headers" : ["author", "title"], # keys shown in the table
            "sortkey" : "name" # the key to sort posts by # currently only usefull to steamrip
        }
        '''
        self.api_url: str = "https://api.michijackson.xyz"
        self.seeded_magnets: set = set()
        self.download_path: str = str(Path.home() / "Downloads")
        self.up_speed_limit: int = 0
        self.down_speed_limit: int = 0
        self.max_connections: int = 200
        self.max_downloads: int = 10
        self.settings_path: str = "" 
        self.dl_session: Any = None
        self.active_downloads: Dict = {}
        self.window_transparency: bool = False
        self.interfaces: List = []
        self.active_interfaces: List = []
        self.bound_interface: Any = None

    def update_tracker_table(self, newtracker: str):

        if newtracker not in self.trackers.keys():
            raise ValueError("the selected tracker is not initialised.")

        self.trackertable.setColumnCount(self.trackers[self.currenttracker][])

        for row_index, row_data in enumerate(self.trackers[self.currenttracker].values()):
            for col_index, key in enumerate(row_data.keys()):
                if key in self.trackers[self.currenttracker]["ignorekeys"]:
                    continue
                value = row_data.get(key, "")
                self.trackertable.setItem(
                    row_index,
                    col_index,
                    QtWidgets.QTableWidgetItem(value)
                )


    @property
    def image_path(self) -> str:
        return self._image_path

    @image_path.setter
    def image_path(self, new_path: str):
        if new_path != self._image_path:
            self._image_path = new_path
            self.image_changed.emit(new_path)

state = AppState()
