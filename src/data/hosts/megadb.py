from utils.logging.logs import consoleLog
import webbrowser
import re


def scrape_megadb(url):
    match = re.search(r"megadb\.net/([a-zA-Z0-9]+)", url)
    if not match:
        consoleLog("MegaDB: Invalid URL")
        return None

    consoleLog("MegaDB: Captcha required, launching browser...")
    webbrowser.open(url)
    return None
