from utils.network.jsonhandler import split_data, format_data
from utils.data.tracker import get_magnet_link
from utils.logging.logs import consoleLog
from utils.data.state import state
from urllib.parse import quote
from typing import Dict
import requests

class RutrackerScraper:
    name = "rutracker"
    headers = ["Post Title", "Author", "Seeders", "Leechers"]
    is_magnet = True

    def search(self, query):
        try:
            search = requests.get(f"{state.api_url}/search?q={quote(query)}", timeout=15)
        except requests.RequestException as e:
            consoleLog(f"Failed to reach server: {e}")
            return []
        consoleLog("Sent request to server")
        if search:
            try:
                _, data, _, success, cached = split_data(search.text)
            except (KeyError, ValueError) as e:
                consoleLog(f"Failed to parse server response: {e}")
                return []
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

    def get_download_link(self, post: Dict):
        _, post_links, _, _, _ = format_data([post])
        return get_magnet_link(post_links[0])

