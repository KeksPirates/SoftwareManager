from utils.logging.logs import consoleLog
from utils.data.state import state
import requests


def get_updates():
    url = f"https://api.github.com/repos/KeksPirates/SoftwareManager/releases/latest"
    try:
        response = requests.get(url, timeout=15)
    except requests.RequestException as e:
        consoleLog(f"Failed to fetch releases: {e}")
        return None, None

    if response.status_code != 200:
        consoleLog(f"Failed to fetch releases: {response.status_code}")
        return None, None

    release = response.json()

    latest_version = release.get("name") or release.get("tag_name")
    assets = release.get("assets", [])

    release_assets = []

    if latest_version != state.version:
        consoleLog(f"New release available: {latest_version}")
        if assets:
            consoleLog("Assets:")
            for asset in assets:
                consoleLog(f"{asset['name']}")
                release_assets.append(dict(
                    name=asset['name'],
                    url=asset['browser_download_url'],
                    hash=asset.get('digest')
                ))
            return release_assets, latest_version
        else:
            return None, None
    else:
        consoleLog("Already up-to-date.")
        return None, None
