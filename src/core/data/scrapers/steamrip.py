
from bs4 import BeautifulSoup
import requests
import re
#from core.utils.general.logs import consoleLog

def scrape_steamrip_links():
    url = f"https://steamrip.com/games-list-page/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    games = soup.find_all("li", class_="az-list-item")
    
    if len(games) == 0:
        return []

    links = []
    for gamehtml in games:
        link = gamehtml.find("a", href=lambda x: x and x.startswith("/"))
        links += re.findall('(?<=href=")[^"]*', link.__str__())

    return links

if __name__ == "__main__":
    print(scrape_steamrip_links())
