import os
import requests

NEWS_API_KEY = os.getenv("NEWS_API_KEY")

def get_news(topic):
    """
    Fetch latest news articles from NewsAPI.
    Returns a list of dicts with 'title' and 'url'.
    """
    try:
        if not NEWS_API_KEY:
            print("❌ NEWS_API_KEY not set in environment")
            return []

        url = (
            f"https://newsapi.org/v2/everything?"
            f"q={topic}&"
            f"language=en&"
            f"sortBy=publishedAt&"
            f"pageSize=3&"
            f"apiKey={NEWS_API_KEY}"
        )

        resp = requests.get(url, timeout=10)
        data = resp.json()

        if resp.status_code != 200:
            print("❌ News API HTTP error:", resp.status_code, data)
            return []

        if data.get("status") != "ok":
            print("❌ News API error:", data)
            return []

        articles = []
        for art in data.get("articles", []):
            title = art.get("title", "No title")
            url = art.get("url", "")
            articles.append({"title": title, "url": url})

        return articles

    except Exception as e:
        print("❌ get_news error:", e)
        return []
