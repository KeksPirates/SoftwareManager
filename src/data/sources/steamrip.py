from data.hosts.buzzheavier import scrape_buzzheavier
from data.hosts.vikingfile import scrape_vikingfile
from data.hosts.gofile import scrape_gofile
from data.hosts.megadb import scrape_megadb
from utils.logging.logs import consoleLog
from bs4 import BeautifulSoup
from typing import Dict
import webbrowser
import requests
import time
import copy

class SteamripScraper:
    name = "steamrip"
    headers = ["Game"]
    is_magnet = False

    def __init__(self):
        self.cache = { "data": [], "last_fetched": 0 }
        self.cache_expiry = 300

    def scrape_steamrip_links(self):
        current_time = time.time()

        if self.cache["data"] and (current_time - self.cache["last_fetched"] < self.cache_expiry):
            return copy.deepcopy(self.cache["data"])

        try:
            url = f"https://steamrip.com/games-list-page/"
            response = requests.get(url)
            response.raise_for_status()
            text = response.text
        except requests.RequestException as e:
            consoleLog(f"SteamRip: Failed to fetch games list - {e}")
            return []

        soup = BeautifulSoup(text, "html.parser")
        games = soup.find_all("li", class_="az-list-item")
        
        if len(games) == 0:
            return []

        links = []
        names = []

        for gamehtml in games:
            link = gamehtml.find("a", href=lambda x: x and x.startswith("/"))
            if link:
                links.append("https://steamrip.com" + link["href"])
                names.append(link.get_text())

        ret = []

        for i in range(len(names)):
            ret.append({"title" : names[i], "url" : links[i]})

        self.cache["data"] = ret
        self.cache["last_fetched"] = current_time

        return ret

    def scrape_steamrip_game_downloads(self, url):
        try:
            response = requests.get(url)
            response.raise_for_status()
        except requests.RequestException as e:
            consoleLog(f"SteamRip: Failed to fetch game page - {e}")
            return []

        soup = BeautifulSoup(response.text, "html.parser")
        download_link_elements = soup.find_all("a",class_="shortc-button")
        download_links = ["", "", "", ""]

        for download_link in download_link_elements:
            pure = download_link.attrs.get("href")
            if not pure or len(pure) < 3:
                continue
            if pure[2] == "b":
                download_links[0] = "https:" + pure
            if pure[2] == "g":
                download_links[1] = "https:" + pure
            if pure[2] == "v":
                download_links[2] = "https:" + pure
            if pure[2] == "m":
                download_links[3] = "https:" + pure

        ret = []

        for link in download_links:
            if link != "":
                ret.append(link)

        return ret

    def get_download_link(self, post: Dict):
        url = post["url"]
        links = self.scrape_steamrip_game_downloads(url)

        if not links:
            consoleLog("SteamRip: No download links found")
            return None, None

        best = ""
        for link in links:
            if link[0] == "h":
                best = link
                break

        if not best:
            consoleLog("SteamRip: No valid download links found")
            return None, None


        try:
            consoleLog(f"Found download link: {best}")
            if "buzzheavier" in best:
                link = scrape_buzzheavier(best)
                return link
            elif "gofile" in best:
                link, headers = scrape_gofile(best)
                return link, headers
            elif "vikingfile" in best:
                scrape_vikingfile(best)
                return None, None
            elif "megadb" in best:
                scrape_megadb(best)
                return None, None
            else:
                consoleLog("SteamRip: Unknown host, launching browser...")
                webbrowser.open(best)
                return None, None
        except Exception as e:
            consoleLog(f"SteamRip: Scraper failed - {e}")
            return None, None

    def search(self, query: str):
        games = self.scrape_steamrip_links()
        
        filtered_games = [
            game for game in games 
            if query.lower() in game["title"].lower()
        ]
        
        return filtered_games