import requests
from core.utils.data.state import state
from core.utils.general.logs import consoleLog

def check_for_updates():
    url = f"https://api.github.com/repos/KeksPirates/SoftwareManager/releases"
    response = requests.get(url)

    if response.status_code != 200:
        consoleLog(f"Failed to fetch releases: {response.status_code}")
        exit(1)

    releases = response.json()
    releases.sort(key=lambda r: r["published_at"], reverse=True)

    latest_release = releases[0]
    latest_version = latest_release["name"]
    assets = latest_release["assets"]


    if state.version == "dev":
        consoleLog("Dev release detected, skipping version check")
        return None, None
    elif latest_version != state.version:
        consoleLog(f"New release available: {latest_version}")
        if assets:
            consoleLog("Assets:")
            for asset in assets:
                consoleLog(f" - {asset['name']}: {asset['browser_download_url']}")
            return assets, latest_version
        else: 
            return None, None
    else:
        consoleLog("Already up-to-date.")
        return None, None
