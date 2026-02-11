import requests
from core.utils.data.state import state
from core.utils.general.logs import consoleLog


def scrape_rutracker(search_text):
    search = requests.get(f"{state.api_url}/search?q={search_text}")
    consoleLog("Sent request to server")
    if search:
        try:
            return search.text
        except Exception:
            consoleLog("No results found / No response from server")
            return None

    else:
        return None
        


# This function utilizes the SoftwareManager server - source code can be found under the "server" branch.
