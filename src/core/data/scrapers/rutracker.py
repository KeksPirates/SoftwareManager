import requests
from core.utils.data.state import state
from core.utils.logging.logs import consoleLog
from core.utils.network.jsonhandler import split_data


def scrape_rutracker(query):
    search = requests.get(f"{state.api_url}/search?q={query}")
    consoleLog("[core.data.scrapers.rutracker] Sent request to server")
    if search:
        _, data, _, _, _ = split_data(search.text)

        return data
    else:
        consoleLog("[core.data.scrapers.rutracker] No search Text, returning nothing")
        return []
        
Metadata = {
    "name" : "rutracker",
    "headers" : ["Post Title", "Author", "Seeders", "Leechers"],
    "searchkey" : None,
    "scrapeFunc" : scrape_rutracker,
    "scrapeSearches" : True,
}



if __name__ != "__main__":
    state.trackers.update({Metadata["name"] : Metadata})
