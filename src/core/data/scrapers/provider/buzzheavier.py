import requests

def scrape_buzzheavier(url):

    response = requests.get(url)
    response.raise_for_status()

    download_url = url + '/download'

    headers = {
        'hx-current-url': url,
        'hx-request': 'true',
        'referer': url
    }
    
    head_response = requests.head(download_url, headers=headers, allow_redirects=False)
    hx_redirect = head_response.headers.get('hx-redirect')
    return hx_redirect