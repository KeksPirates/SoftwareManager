import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from core.utils.logging.logs import consoleLog
from core.utils.data.state import state
from typing import Dict


def scrape_uztracker(query):
    base_url="https://uztracker.net/"
    search_url = f"{base_url.rstrip('/')}/tracker.php?nm={query}"
    consoleLog(search_url)
    posts = []

    try:
        response = requests.get(search_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        links = soup.find_all('tr', class_="tCenter hl-tr", id=lambda x: x and x.startswith('tor_'))
        for link in links:

            theme_link = link.find('a', class_="genmed tLink", href=lambda x: x and x.startswith('./viewtopic'))
            if not theme_link or not theme_link.b:
                continue
            url = urljoin(base_url, theme_link['href'])
            title = theme_link.b.text
            author_link = link.find('a', class_="med")
            author = author_link.text.strip() if author_link else "Unknown"

            posts.append(dict(
                title=title,
                author=author,
                url=url,
            ))

        return posts

    except requests.RequestException as e:
        consoleLog(f"Failed to fetch {search_url}: {e}")
        return None

Metadata = {
    "name" : "uztracker",
    "headers" : ["Post Title", "Author"],
    "searchkey" : None,
    "scrapeFunc" : scrape_uztracker,
    "scrapeSearches" : True,
}
def get_magnet_link(post: Dict):
    item = "https://uztracker.net/" + post["url"].lstrip("./")
    return item

def init_uztracker():
    state.trackers.update({Metadata["name"] : Metadata})
