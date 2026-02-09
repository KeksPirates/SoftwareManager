from PySide6.QtWidgets import QTableWidgetItem
from core.utils.general.logs import consoleLog
from core.data.scrapers.uztracker import scrape_uztracker
from core.data.scrapers.rutracker import scrape_rutracker
from core.data.scrapers.monkrus import scrape_monkrus_telegram
from core.utils.network.jsonhandler import split_data, format_data, format_data_m0nkrus
from core.utils.data.state import state

def return_pressed(self):
    search_text = self.searchbar.text()
    if search_text == "":
        consoleLog("Error: Can't search for nothing")
        return
    consoleLog(f"User searched for: {search_text}")
    
    if state.tracker == "uztracker":
        response = scrape_uztracker(search_text)
        if response:
            state.post_titles, state.post_urls = response
            self.qtablewidget.clear()
            if state.post_titles and len(state.post_titles) > 0:
                self.qtablewidget.setHorizontalHeaderLabels(["Post Title", "Author"])
                self.qtablewidget.setRowCount(len(state.post_titles))
                for i, author in enumerate(state.post_author):
                    self.qtablewidget.setItem(i, 1, QTableWidgetItem(author))
                for i, title in enumerate(state.post_titles):
                    self.qtablewidget.setItem(i, 0, QTableWidgetItem(title))
                self.show_empty_results(False)
            else:
                consoleLog(f"No Results for {search_text}")
                self.qtablewidget.clear()
                self.show_empty_results(True)
        else:
            consoleLog(f"No response from uztracker")
            self.qtablewidget.clear()
            self.show_empty_results(True)
    
    elif state.tracker == "rutracker":
        response = scrape_rutracker(search_text)
        if response:
            _, state.posts, _, _, cached = split_data(response)
            if state.posts == []:
                consoleLog(f"No Results for {search_text}")
                self.qtablewidget.clear()
                self.show_empty_results(True)
            else:
                state.post_titles, _, state.post_author, state.post_seeders, state.post_leechers = format_data(state.posts)
                self.show_empty_results(False)
                self.qtablewidget.clear()
                self.qtablewidget.setHorizontalHeaderLabels(["Post Title", "Author", "Seeders", "Leechers"])
                self.qtablewidget.setRowCount(len(state.post_titles))
                for i, author in enumerate(state.post_author):
                    self.qtablewidget.setItem(i, 1, QTableWidgetItem(author))
                for i, title in enumerate(state.post_titles):
                    self.qtablewidget.setItem(i, 0, QTableWidgetItem(title))
                for i, seeders in enumerate(state.post_seeders):
                    self.qtablewidget.setItem(i, 2, QTableWidgetItem(seeders))
                for i, leechers in enumerate(state.post_leechers):
                    self.qtablewidget.setItem(i, 3, QTableWidgetItem(leechers))
                if state.debug == True:
                    consoleLog(f"Response Cached: {cached}")
        else:
            consoleLog(f"No response from rutracker")
            self.qtablewidget.clear()
            self.show_empty_results(True)

    elif state.tracker == "m0nkrus":
        state.posts = scrape_monkrus_telegram(search_text)

        if state.posts == []:
            consoleLog(f"No Results for {search_text}")
            self.qtablewidget.clear()
            self.show_empty_results(True)
        else:
            state.post_titles, _, state.post_author = format_data_m0nkrus(state.posts)
            self.show_empty_results(False)
            self.qtablewidget.clear()
            self.qtablewidget.setHorizontalHeaderLabels(["Post Title", "Author"])
            self.qtablewidget.setRowCount(len(state.post_titles))
            for i, author in enumerate(state.post_author):
                self.qtablewidget.setItem(i, 1, QTableWidgetItem(author))
            for i, title in enumerate(state.post_titles):
                self.qtablewidget.setItem(i, 0, QTableWidgetItem(title))
