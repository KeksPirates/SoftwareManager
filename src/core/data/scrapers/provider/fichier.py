import requests
from bs4 import BeautifulSoup

def scrape_fichier(url: str):
    response = requests.get(url)

    soup = BeautifulSoup(response.text, "html.parser")

    btn = soup.find_all("a", class_="ok")

    print(response.text)

    link = btn[0].get("href")

    return link


if __name__ == "__main__":
    print(scrape_fichier("https://1fichier.com/?ai6vzcfi1r79q9rebc3a"))


