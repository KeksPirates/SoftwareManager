import requests
from core.utils.data.state import state
from core.utils.logging.logs import consoleLog
from core.utils.data.tracker import get_magnet_link
from core.utils.network.jsonhandler import split_data, format_data
from typing import Dict

def scrape_rutracker(query):
    search = requests.get(f"{state.api_url}/search?q={query}", timeout=15)
    consoleLog("Sent request to server")
    if search:
        _, data, _, success, cached = split_data(search.text)
        if cached:
            consoleLog("Server response cached")
        if success:
            sorted_data = []

            for entry in data:
                sorted_data.append(
                    {
                        "title" : entry["title"],
                        "author" : entry["author"],
                        "seeders" : entry["seeders"],
                        "leechers" : entry["leechers"],
                        "url" : entry["url"],
                        "id" : entry["id"],
                    }
                )

            return sorted_data
        else: 
            consoleLog("Scraping failed server-side, unable to fetch posts from rutracker")
            return []
    else:
        consoleLog("No response from server, returning nothing")
        return []


def get_magnet(post: Dict):
    _, post_links, _, _, _ = format_data([post])
    return get_magnet_link(post_links[0])

Metadata = {
    "name" : "rutracker",
    "headers" : ["Post Title", "Author", "Seeders", "Leechers"],
    "scrapeFunc" : scrape_rutracker,
    "linkFunc" : get_magnet,
    "isMagnet" : True,
}

def init_rutracker():
    state.trackers.update({Metadata["name"] : Metadata})
