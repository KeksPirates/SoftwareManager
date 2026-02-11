import json

def split_data(data):
    p_json = json.loads(data)

    count = p_json["count"]
    posts = p_json["data"]
    query = p_json["query"]
    success = p_json["success"]
    cached = p_json["cached"]

    return count, posts, query, success, cached

def format_data(data): 
    post_author = [post["author"] for post in data]
    post_titles = [post["title"] for post in data]
    post_links = [post["url"] for post in data]
    post_seeders = [post["seeders"] for post in data]
    post_leechers = [post["leechers"] for post in data]

    return post_titles, post_links, post_author, post_seeders, post_leechers

def format_data_m0nkrus(data): 
    post_author = [post["author"] for post in data]
    post_titles = [post["title"] for post in data]
    post_links = [post["url"] for post in data]

    return post_titles, post_links, post_author






# https://open.spotify.com/track/70vjXI7oBou5buTtgiJeRW?si=25640cc4243c4bf3
