
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
    names = []
    for gamehtml in games:
        link = gamehtml.find("a", href=lambda x: x and x.startswith("/"))
        links += re.findall('(?<=href=")[^"]*', link.__str__())
        name = gamehtml.find("a", href=lambda x: x and x.startswith("/"))
        names += re.findall('(?<=\/">)[^<]*', name.__str__())



    # construct the list[dict[str,str]]

    ret = []

    for i in range(len(names)-1):
        ret.append({"name" : names[i], "link" : links[i]})

    return ret

def offline_scrape_steamrip_links():
    text = ""
    with open("example.html", encoding = "utf-8") as f:
        text=f.read()

    return scrape_steamrip_links(text)

if __name__ == "__main__":
    print(offline_scrape_steamrip_links())