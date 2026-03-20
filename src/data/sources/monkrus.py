from utils.data.tracker import get_magnet_link
from bs4 import BeautifulSoup
from typing import Dict
import requests
import time


class MonkrusScraper:
    name = "m0nkrus"
    headers = ["Post Title", "Author"]
    is_magnet = True

    def __init__(self):
        self.cache = { "data": [], "last_fetched": 0 }
        self.cache_expiry = 300

    def _get_telegram_posts(self):
        post = 100
        max_posts = 250
        posts = []
        added = set()

        current_time = time.time()

        if self.cache["data"] and (current_time - self.cache["last_fetched"] < self.cache_expiry):
            return self.cache["data"]

        while post <= max_posts:
            url = f"https://t.me/s/real_monkrus/{post}"
            response = requests.get(url, timeout=10)
            soup = BeautifulSoup(response.text, "html.parser")
            bubbles = soup.find_all("div", class_="tgme_widget_message_bubble")
            
            if not bubbles:
                break
            
            for bubble in bubbles:
                post_txt = bubble.find("div", class_="tgme_widget_message_text js-message_text")
                if post_txt is None or post_txt.b is None:
                    continue
                
                title = post_txt.b.text
                link = bubble.find("a", href=lambda x: x and x.startswith("https://uztracker.net"))
                
                if link:
                    post_url = link["href"]
                    if post_url not in added:
                        added.add(post_url)
                        posts.append(dict(
                            title=title,
                            author="m0nkrus",
                            id=len(posts) + 1,
                            url=post_url
                        ))
            
            post += 22

        posts.reverse()

        self.cache["data"] = posts
        self.cache["last_fetched"] = current_time

        return(posts)

    def search(self, query):
        posts = self._get_telegram_posts()
        filtered_posts = []

        for post in posts:
            if query.lower() in post["title"].lower():
                filtered_post = post.copy()
                filtered_post["id"] = len(filtered_posts) + 1
                filtered_posts.append(filtered_post)

        return filtered_posts

    def get_magnet(self, post: Dict):
        return get_magnet_link(post["url"])
