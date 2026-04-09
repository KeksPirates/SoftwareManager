from data.hosts.buzzheavier import scrape_buzzheavier
from data.hosts.gofile import scrape_gofile
from utils.logging.logs import consoleLog
from bs4 import BeautifulSoup
from typing import Dict
import webbrowser
import requests
import time
import re

class SteamripScraper:
    name = "steamrip"
    headers = ["Game"]
    is_magnet = False


    def __init__(self):
        self.cache = { "data": [], "last_fetched": 0 }
        self.cache_expiry = 300

    def scrape_steamrip_links(self):
        
        current_time = time.time()

        if self.cache["data"] != [] and (current_time - self.cache["last_fetched"] < self.cache_expiry):
            return self.cache["data"]

        url = f"https://steamrip.com/games-list-page/"
        response = requests.get(url)
        text = response.text

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
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        download_link_elements = soup.find_all("a",class_="shortc-button")
        download_links = ["buzzheavier", "gofile"]

        for download_link in download_link_elements:
            pure = download_link.attrs.get("href")
            if pure[2] == "b":
                download_links[0] = "https:" + pure
            if pure[2] == "g":
                download_links[1] = "https:" + pure

        ret = []

        for link in download_links:
            if len(link) != 1:
                ret.append(link)

        return ret

    def get_download_link(self, post: Dict):
        url = post["url"]
        links = self.scrape_steamrip_game_downloads(url)
        best = ""
        for link in links:
            if link[0] == "h":
                best = link
                break

        if links.index(best) == 0:
            link = scrape_buzzheavier(best)
            return link
        elif links.index(best) == 1:
            link, headers = scrape_gofile(best)
            return link, headers
        else:
            consoleLog("Unable to retrieve download link due to captcha, launching browser...")
            webbrowser.open(best)
            return None, None

    def search(self, query: str):
        games = self.scrape_steamrip_links()
        
        filtered_games = [
            game for game in games 
            if query.lower() in game["title"].lower()
        ]
        
        return filtered_games