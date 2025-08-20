from dotenv import load_dotenv
import requests
import os

load_dotenv()
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

# path: backend/news.py
import os
import requests

NEWS_API_KEY = os.getenv("NEWS_API_KEY")

def get_news(topic="technology"):
    """
    Fetch latest news articles from NewsAPI.
    Returns a list of dicts with 'title' and 'url'.
    """
    try:
        url = (
            f"https://newsapi.org/v2/everything?"
            f"q={topic}&"
            f"language=en&"
            f"sortBy=publishedAt&"
            f"pageSize=5&"
            f"apiKey={NEWS_API_KEY}"
        )

        resp = requests.get(url, timeout=10)
        data = resp.json()

        # If API error
        if resp.status_code != 200 or "articles" not in data:
            print("❌ News API error:", data)
            return []

        articles = []
        for art in data["articles"]:
            articles.append({
                "title": art.get("title", "No title"),
                "url": art.get("url", "")
            })

        return articles

    except Exception as e:
        print("❌ get_news error:", e)
        return []
