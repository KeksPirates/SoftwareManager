from PySide6.QtWidgets import QTableWidgetItem, QHeaderView
from core.utils.logging.logs import consoleLog
from core.data.scrapers.rutracker import init_rutracker
from core.data.scrapers.uztracker import init_uztracker
from core.data.scrapers.monkrus import init_m0nkrus
from core.data.scrapers.steamrip import init_steamrip
from core.utils.data.state import state

init_rutracker()
init_uztracker()
init_m0nkrus()
init_steamrip()

def return_pressed(self):
    self.show_empty_results(False)
    search_text = self.searchbar.text()
    if search_text == "":
        consoleLog("Error: Can't search for nothing")
        return
    consoleLog(f"User searched for: {search_text}")
    
    tracker = state.trackers[state.currenttracker]
    scrapefunc = tracker["scrapeFunc"]
    state.posts = scrapefunc(search_text)

    from core.interface.gui import MainWindow
    MainWindow._instance.search_results_signal.emit(tracker["headers"])
