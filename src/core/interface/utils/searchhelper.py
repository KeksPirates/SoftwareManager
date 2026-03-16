from core.data.scrapers.rutracker import init_rutracker
from core.data.scrapers.uztracker import init_uztracker
from core.data.scrapers.steamrip import init_steamrip
from core.data.scrapers.monkrus import init_m0nkrus
from core.utils.logging.logs import consoleLog
from core.utils.data.state import state

# Call initialization function for each tracker / site
init_rutracker()
init_uztracker()
init_m0nkrus()
init_steamrip()


def run_search(self) -> None:
    self.show_empty_results(False)

    search_text = self.searchbar.text()
    # Check for empty search
    if search_text == "":
        consoleLog("Error: Can't search for nothing")
        return
    consoleLog(f"User searched for: {search_text}")
    
    # Get current tracker and call its search function
    tracker = state.trackers[state.currenttracker]
    scrapefunc = tracker["scrapeFunc"]
    state.posts = scrapefunc(search_text)
    
    # Late to prevent circular import
    from core.interface.gui import MainWindow

    # Update GUI Headers
    MainWindow._instance.search_results_signal.emit(tracker["headers"])
