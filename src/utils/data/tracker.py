from utils.logging.logs import consoleLog
from bs4 import BeautifulSoup
import requests


def get_magnet_link(post_url):
    try:
        response = requests.get(post_url, timeout=15) # eventually impl. cloudscraper
        consoleLog("Sent Request to retrieve Magnet Link...")
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        magnet_link = soup.find('a', href=lambda x: x and x.startswith('magnet:'))
        if magnet_link:
            consoleLog(f"Magnet Link Retrieved: {magnet_link['href']}")
            return magnet_link['href']
        else:
            consoleLog("Magnet Link not Found!")
            return None
    except requests.RequestException as e:
        consoleLog(f"Failed to fetch {post_url}: {e}")
        return None
    
