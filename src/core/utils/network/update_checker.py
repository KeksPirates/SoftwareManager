import requests
from core.utils.data.state import state
from core.utils.logging.logs import consoleLog

def get_updates():
    url = f"https://api.github.com/repos/KeksPirates/SoftwareManager/releases/latest"
    response = requests.get(url, timeout=15)

    if response.status_code != 200:
        consoleLog(f"Failed to fetch releases: {response.status_code}")
        return None

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
            return release_assets
        else: 
            return None
    else:
        consoleLog("Already up-to-date.")
        return None
