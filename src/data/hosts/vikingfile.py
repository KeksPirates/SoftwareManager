from utils.logging.logs import consoleLog
import webbrowser
import re


def scrape_vikingfile(url):
    match = re.search(r"vikingfile\.com/f/([a-zA-Z0-9]+)", url)
    if not match:
        consoleLog("VikingFile: Invalid URL")
        return None

    consoleLog("VikingFile: Captcha required, launching browser...")
    webbrowser.open(url)
    return None
