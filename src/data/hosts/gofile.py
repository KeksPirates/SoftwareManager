from utils.logging.logs import consoleLog
import requests
import hashlib
import time
import re

_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
_WT_SECRET = "5d4f7g8sd45fsd"
_API_BASE = "https://api.gofile.io"


def _generate_website_token(account_token):
    time_bucket = str(int(time.time() / 14400))
    raw = f"{_USER_AGENT}::en-US::{account_token}::{time_bucket}::{_WT_SECRET}"
    return hashlib.sha256(raw.encode()).hexdigest()


def scrape_gofile(url):
    match = re.search(r"gofile\.io/d/([a-zA-Z0-9]+)", url)
    if not match:
        consoleLog("GoFile: Invalid URL")
        return None

    content_id = match.group(1)
    session = requests.Session()
    try:
        # Create a guest account
        r = session.post(f"{_API_BASE}/accounts", headers={"User-Agent": _USER_AGENT}, timeout=15)
        data = r.json()
        if data.get("status") != "ok":
            consoleLog("GoFile: Failed to create guest account")
            return None

        account_token = data["data"]["token"]
        website_token = _generate_website_token(account_token)

        headers = {
            "User-Agent": _USER_AGENT,
            "Authorization": f"Bearer {account_token}",
            "X-Website-Token": website_token,
            "X-BL": "en-US",
            "Referer": "https://gofile.io/",
            "Origin": "https://gofile.io",
        }

        # Fetch folder contents
        r = session.get(f"{_API_BASE}/contents/{content_id}", headers=headers, timeout=15)
        data = r.json()
        if data.get("status") != "ok":
            consoleLog(f"GoFile: API error - {data.get('status')}")
            return None

        children = data["data"].get("children", {})
        if not children:
            consoleLog("GoFile: No files found")
            return None

        first_child = next(iter(children.values()))
        link = first_child.get("link")
        if not link:
            consoleLog("GoFile: No download link in response")
            return None

        return link, headers
    finally:
        session.close()