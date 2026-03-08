import requests
from core.utils.data.state import state
from core.utils.logging.logs import consoleLog
from core.utils.network.jsonhandler import split_data


def scrape_rutracker(query):
    search = requests.get(f"{state.api_url}/search?q={query}")
    consoleLog("[core.data.scrapers.rutracker] Sent request to server")
    if search:
        _, data, _, _, _ = split_data(search.text)
        
        sorteddata = []

        for entry in data:
            sorteddata.append(
                {
                    "title" : entry["title"],
                    "author" : entry["author"],
                    "seeders" : entry["seeders"],
                    "leechers" : entry["leechers"],
                    "url" : entry["url"],
                    "id" : entry["id"],
                }
            )

        return sorteddata
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


def init_rutracker():
    state.trackers.update({Metadata["name"] : Metadata})
