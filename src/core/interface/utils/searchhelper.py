from PySide6.QtWidgets import QTableWidgetItem, QHeaderView
from core.utils.logging.logs import consoleLog
from core.data.scrapers.uztracker import scrape_uztracker
from core.data.scrapers.rutracker import scrape_rutracker
from core.data.scrapers.monkrus import scrape_m0nkrus
from core.data.scrapers.steamrip import filter_steamrip
from core.utils.data.state import state

def return_pressed(self):
    search_text = self.searchbar.text()
    if search_text == "":
        consoleLog("Error: Can't search for nothing")
        return
    consoleLog(f"User searched for: {search_text}")
    
    tracker = state.trackers[state.currenttracker]

    scrapefunc: function = tracker["scrapeFunc"]

    state.posts = scrapefunc(search_text)
    
    state.trackertable.clearContents()

    if state.posts == []:
        self.show_empty_results(True)
    
    state.trackertable.setColumnCount(len(tracker["headers"]))
    state.trackertable.setHorizontalHeaderLabels(tracker["headers"])
    state.trackertable.setRowCount(len(state.posts))
        
    for x, rowdata in enumerate(state.posts):
        for y, data in enumerate(rowdata.values()):
            state.trackertable.setItem(x, y, QTableWidgetItem(data))

    consoleLog("[searchhelper] updated table")
