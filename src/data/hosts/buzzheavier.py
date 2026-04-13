from utils.logging.logs import consoleLog
import requests

def scrape_buzzheavier(url):
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
    except requests.RequestException as e:
        consoleLog(f"Buzzheavier: Failed to fetch page - {e}")
        return None

    download_url = url + '/download'

    headers = {
        'hx-current-url': url,
        'hx-request': 'true',
        'referer': url
    }

    try:
        head_response = requests.head(download_url, headers=headers, allow_redirects=False, timeout=15)
        hx_redirect = head_response.headers.get('hx-redirect')
        return hx_redirect
    except requests.RequestException as e:
        consoleLog(f"Buzzheavier: Failed to fetch download URL - {e}")
        return None