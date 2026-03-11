from core.utils.logging.loghandler import consoleLog
import requests
import re


def scrape_gofile(url):

    filetoken = re.findall(r"(?<=https...gofile.io\/d\/).*", url)[0]
    session = requests.Session()

    acc = session.post("https://api.gofile.io/accounts")
    token = acc.json()["data"]["token"]

    headers = {
        "Authorization": f"Bearer {token}",
        "X-Website-Token": "4fd6sg89d7s6", # Maybe make this dynamic in the future
    }

    r = session.get(
        f"https://api.gofile.io/contents/{filetoken}",
        headers=headers,
    )
    try:

        temp: dict = r.json()["data"]["children"]
        child = [key for key in temp.keys()]

        return temp[child[0]]["link"]
    except:
        consoleLog("GoFile Authorisation failed, if the Issue persists, please open an Issue on GitHub")

