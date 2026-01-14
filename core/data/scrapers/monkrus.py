from bs4 import BeautifulSoup
import requests
from core.utils.general.logs import consoleLog

def scrape_monkrus_telegram(query):
    post = 100
    max_posts = 250
    posts: list[dict] = []
    added = set()
    
    while post <= max_posts:
        url = f"https://t.me/s/real_monkrus/{post}"
        response = requests.get(url)
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
            
            if query.lower() in title.lower() and link:
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
    return(posts)
