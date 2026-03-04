import requests
import threading
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from core.utils.data.state import state
from core.utils.logging.logs import consoleLog
from core.utils.general.wrappers import run_thread

def scrape_uztracker(query):
    base_url="https://uztracker.net/"
    search_url = f"{base_url.rstrip('/')}/tracker.php?nm={query}"
    consoleLog(search_url)
    posts = []

    try:
        response = requests.get(search_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        links = soup.find_all('a', class_="genmed tLink", href=lambda x: x and x.startswith('./viewtopic'))
        
        for link in links:
            if link.b:
                title = link.b.text
                url = urljoin(base_url, link['href'])

                author_link = link.find_parent('td').find('a', class_="med ts-text")
                author = author_link.text.strip() if author_link else "Unknown"

                posts.append(dict(
                    title=title,
                    url=url,
                    author=author
                ))

        return posts

    except requests.RequestException as e:
        if posts:
            consoleLog(f"Failed to fetch {search_url}: {e}")
        return None



