from core.utils.logging.logs import consoleLog
import requests
import re


def scrape_gofile(url):

    filetoken = re.findall(r"(?<=https...gofile.io\/d\/).*", url)[0]
    session = requests.Session()

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:148.0) Gecko/20100101 Firefox/148.0",
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Referer": "https://gofile.io/",
        "Authorization": f"Bearer lUUtRAccOuRUoZhelNSslDFSlpOgKLDj",
        "X-Website-Token": "ffd9ffa831c50b9e68ca5e65cbbbd1a50e9a32e63022e17c7c6748388a1ed73b",
        "X-BL": "en-US",
        "Origin": "https://gofile.io",
        "Sec-GPC": "1",
        "Connection": "keep-alive",
        "TE": "trailers"
    }

    r = session.get(
        f"https://api.gofile.io/contents/{filetoken}",
        headers=headers,
    )

    try:

        temp: dict = r.json()["data"]["children"]
        child = [key for key in temp.keys()]

        link = temp[child[0]]["link"]
        return link, headers
    except Exception:
        consoleLog("GoFile Authorization failed, if the Issue persists, please open an Issue on GitHub")
        return None

