
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

    download_links = ["b", "g", "v", "m"]

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



    return ret


if __name__ == "__main__":
    #print(offline_scrape_steamrip_links())
    print(scrape_steamrip_game_downloads("/r-e-p-o-free-download/"))
