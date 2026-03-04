from PySide6.QtWidgets import QTableWidgetItem
from core.utils.logging.logs import consoleLog
from core.data.scrapers.uztracker import scrape_uztracker
from core.data.scrapers.rutracker import scrape_rutracker
from core.data.scrapers.monkrus import scrape_m0nkrus
from core.utils.network.jsonhandler import split_data, format_data, format_data_minimal
from core.utils.data.state import state

scrapers = {
    "uztracker": scrape_uztracker,
    "rutracker": scrape_rutracker,
    "m0nkrus": scrape_m0nkrus
}

def return_pressed(self):
    search_text = self.searchbar.text()
    if search_text == "":
        consoleLog("Error: Can't search for nothing")
        return
    consoleLog(f"User searched for: {search_text}")
    
    if state.tracker == "rutracker":
        response = scrape_rutracker(search_text)
        if response:
            _, state.posts, _, _, cached = split_data(response)
            if state.posts == []:
                consoleLog(f"No Results for {search_text}")
                state.tracker_list[state.tracker].clear()
                self.show_empty_results(True)
            else:
                state.post_titles, _, state.post_author, state.post_seeders, state.post_leechers = format_data(state.posts)
                self.show_empty_results(False)
                state.tracker_list[state.tracker].clear()
                state.tracker_list[state.tracker].setHorizontalHeaderLabels(["Post Title", "Author", "Seeders", "Leechers"])
                state.tracker_list[state.tracker].setRowCount(len(state.post_titles))
                for i, author in enumerate(state.post_author):
                    state.tracker_list[state.tracker].setItem(i, 1, QTableWidgetItem(author))
                for i, title in enumerate(state.post_titles):
                    state.tracker_list[state.tracker].setItem(i, 0, QTableWidgetItem(title))
                for i, seeders in enumerate(state.post_seeders):
                    state.tracker_list[state.tracker].setItem(i, 2, QTableWidgetItem(seeders))
                for i, leechers in enumerate(state.post_leechers):
                    state.tracker_list[state.tracker].setItem(i, 3, QTableWidgetItem(leechers))
                if state.debug == True:
                    consoleLog(f"Response Cached: {cached}")
        else:
            consoleLog(f"No response from rutracker")
            state.tracker_list[state.tracker].clear()
            self.show_empty_results(True)

    elif state.tracker is not None:
        state.posts = scrapers[state.tracker](search_text)
        if state.posts == []:
            consoleLog(f"No Results for {search_text}")
            state.tracker_list[state.tracker].clear()
            self.show_empty_results(True)
        else:
            state.post_author, state.post_titles, state.post_urls  = format_data_minimal(state.posts)
            self.show_empty_results(False)
            state.tracker_list[state.tracker].clear()
            state.tracker_list[state.tracker].setHorizontalHeaderLabels(["Post Title", "Author"])
            state.tracker_list[state.tracker].setRowCount(len(state.post_titles))
            for i, author in enumerate(state.post_author):
                state.tracker_list[state.tracker].setItem(i, 1, QTableWidgetItem(author))
            for i, title in enumerate(state.post_titles):
                state.tracker_list[state.tracker].setItem(i, 0, QTableWidgetItem(title))