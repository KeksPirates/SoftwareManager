import requests
from core.utils.data.state import state
from core.utils.logging.logs import consoleLog

Metadata = {
    "headers" : ["Post Title", "Author", "Seeders", "Leechers"],
    "name" : "rutracker",
}

def get_Metadata():
    return Metadata

def scrape_rutracker(query):
    search = requests.get(f"{state.api_url}/search?q={query}")
    consoleLog("Sent request to server")
    if search:
        try:
            return search.text
        except Exception:
            consoleLog(f"No results found / No response from server, exception: {Exception}")
            return None
    else:
        return None
        


# This function utilizes the SoftwareManager server - source code can be found under the SoftwareManager-Server repository.
