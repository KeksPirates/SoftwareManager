
import os
from bs4 import BeautifulSoup
from fuzzyfinder.main import fuzzyfinder
import requests
import re
import time
import webbrowser
from typing import Generator
from core.utils.data.state import state
from core.utils.logging.logs import consoleLog


cache = {
    "data": [],
    "last_fetched": 0
}

cache_expiry = 300

def get_Metadata():
    return Metadata

def scrape_steamrip_links():
    
    current_time = time.time()

    if cache["data"] != [] and (current_time - cache["last_fetched"] < cache_expiry):
        return cache["data"]

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
        links += re.findall(r'(?<=href=")[^"]*', link.__str__())
        name = gamehtml.find("a", href=lambda x: x and x.startswith("/"))
        names += re.findall(r'(?<=\/">)[^<]*', name.__str__())



    # construct the list[dict[str,str]]

    ret = []

    for i in range(len(names)-1):
        ret.append({"name" : names[i], "link" : links[i]})

    return ret

def scrape_steamrip_game_downloads(gamelink):
    url = "https://steamrip.com" + gamelink
    response = requests.get(url)

    soup = BeautifulSoup(response.text, "html.parser")

    download_link_elements = soup.find_all("a",class_="shortc-button")


    download_links = ["buzzheavier", "gofile", "vikingfile", "megadb"]

    for download_link in download_link_elements:
        pure = download_link.attrs.get("href")
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
        if len(link) != 1:
            ret.append(link)

    cache["data"] = ret

    return ret

def get_download_link(post: Dict):
    url = post["link"]
    links = scrape_steamrip_game_downloads(url)
    best = ""
    for link in links:
        if link[0] != "h":
            best = link
            break

    if links.index(best) < 2:
        return best
    else:
        consoleLog("cant scrape this cuz of captcha... opening in the browser")
        webbrowser.open(best)
        return None

def filter_steamrip(query: str):
    
    options: Generator = fuzzyfinder(query, scrape_steamrip_links(), accessor=lambda x: x["name"])

    return list(options)




Metadata = {
    "name" : "steamrip",
    "headers" : ["Game"],
    "scrapeFunc" : filter_steamrip,
}

def init_steamrip():
    state.trackers.update({Metadata["name"] : Metadata})

if __name__ == "__main__":
    print(scrape_steamrip_game_downloads("/r-e-p-o-free-download/"))
