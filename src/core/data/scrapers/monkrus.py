from bs4 import BeautifulSoup
import requests
import time
from core.utils.general.logs import consoleLog

cache = {
    "data": [],
    "last_fetched": 0
}

cache_expiry = 300

def _get_telegram_posts():
    post = 100
    max_posts = 250
    posts = []
    added = set()

    current_time = time.time()

    if cache["data"] and (current_time - cache["last_fetched"] < cache_expiry):
        return cache["data"]

    while post <= max_posts:
        url = f"https://t.me/s/real_monkrus/{post}"
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        bubbles = soup.find_all("div", class_="tgme_widget_message_bubble")
        
        if not bubbles:
            break
        
        for bubble in bubbles:
            post_txt = bubble.find("div", class_="tgme_widget_message_text js-message_text")
            if not post_txt or not post_txt.b:
                continue
            
            title = post_txt.b.text
            link = bubble.find("a", href=lambda x: x and x.startswith("https://uztracker.net"))
            
            if link:
                post_url = link["href"]
                if post_url not in added:
                    added.add(post_url)
                    posts.append(dict(
                        author="m0nkrus",
                        id=len(posts) + 1,
                        title=title,
                        url=post_url
                    ))
        
        post += 22

    posts.reverse()

    cache["data"] = posts
    cache["last_fetched"] = current_time

    return(posts)

def scrape_monkrus_telegram(query):
    posts = _get_telegram_posts()
    filtered_posts = []

    for post in posts:
        if query.lower() in post["title"].lower():
            filtered_post = post.copy()
            filtered_post["id"] = len(filtered_posts) + 1
            filtered_posts.append(filtered_post)

    return filtered_posts