
from bs4 import BeautifulSoup
import requests
import re
#from core.utils.general.logs import consoleLog

def scrape_steamrip_links(text = None):
    if text is None:
        url = f"https://steamrip.com/games-list-page/"
        response = requests.get(url)
        text = response.text

    soup = BeautifulSoup(text, "html.parser")
    games = soup.find_all("li", class_="az-list-item")
    
    if len(games) == 0:
        return []

    links = []
    for i, gamehtml in enumerate(games):
        if i == 0: print(gamehtml)
        link = gamehtml.find("a", href=lambda x: x and x.startswith("/"))
        links += re.findall('(?<=href=")[^"]*', link.__str__())


    # construct the list[dict[str,str]]

    ret = []

    for link in links:
        ret.append({"name" : link})

    return ret

def offline_scrape_steamrip_links():
    text = ""
    with open("example.html", encoding = "utf-8") as f:
        text=f.read()

    return scrape_steamrip_links(text)

if __name__ == "__main__":
    print(offline_scrape_steamrip_links())