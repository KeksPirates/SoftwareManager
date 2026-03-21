from utils.logging.logs import consoleLog
from utils.data.state import state
from data.sources import SCRAPERS

for scraper in SCRAPERS:
    state.trackers[scraper.name] = scraper

def run_search(self) -> None:
    state.trackertable.setRowCount(0)
    self.show_empty_results(False)

    search_text = self.searchbar.text()
    # Check for empty search
    if search_text == "":
        consoleLog("Error: Can't search for nothing")
        return

    state.posts = []
    self.searchbar.setEnabled(False)
    consoleLog(f"User searched for: {search_text}")
    
    # Get current tracker and call its search function
    scraper = state.trackers[state.currenttracker]
    state.posts = scraper.search(search_text)
    
    # Update GUI headers to match the current scraper
    self.search_results_signal.emit(scraper.headers)