import requests
import asyncio
from bs4 import BeautifulSoup
from core.utils.data.state import state
from core.utils.general.logs import consoleLog


global url_uztracker
url_uztracker = "https://uztracker.net/tracker.php?nm="

async def init_uztracker():
    global up
    global soup
    try:
        response = requests.get(url_uztracker, timeout=10)
        if response.status_code == 200:
            up = True
        else:
            up = False
            consoleLog(f"Uztracker seems down, status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        consoleLog(f"\nRequest Exception on {url_uztracker}:")
        consoleLog(str(e))
        consoleLog("\nIs the Site down?")
        up = False

asyncio.run(init_uztracker())

def scrape_uztracker(search):
    if up:
        search_url = url_uztracker + search
        consoleLog(search_url)
        result = False
        global results
        global resulttitles
        results = []
        resulttitles = []

        try:
            resultCount = 0
            response = requests.get(search_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            links = soup.find_all('a', class_="genmed tLink", href=lambda x: x and x.startswith('./viewtopic'))
            for link in links:
                if link.b:
                    resultCount += 1
                    results.append(link['href'])
                    resulttitles.append(link.b.text)
                    result = True

            if result:
                return resulttitles, results

            if not result:
                # add popup in gui for no result
                return None

        except requests.RequestException as e:
            if result:
                consoleLog(f"Failed to fetch {search_url}: {e}")
            return None
    else:
        consoleLog("Error: Uztracker down")
        return None, None

def get_post_title(post_url):
    if up:
        response = requests.get(post_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        maintitle = soup.find(class_='tt-text')
        if maintitle:
            return maintitle.text
        else:
            consoleLog("Program not found")
    else:
        consoleLog("Error: Uztracker down")
        return None   

    


