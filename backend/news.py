from dotenv import load_dotenv
import requests
import os

load_dotenv()
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

# path: backend/news.py


def get_news(topic):
    """
    Fetch latest news articles from NewsAPI.org.
    Returns a single formatted string with up to 3 articles.
    """
    try:
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

        # If API error
        if resp.status_code != 200 or "articles" not in data:
            print("❌ News API error:", data)
            return f"⚠️ No news found. Error: {data.get('message', 'Unknown error')}"

        messages = []
        for art in data["articles"]:
            title = art.get("title", "No Title")
            source = art.get("source", {}).get("name", "Unknown")
            pub_date = art.get("publishedAt", "Unknown Date")
            link = art.get("url", "#")

            messages.append(f"🗞️ *{title}*\n📍{source} | 🕒 {pub_date}\n🔗 {link}")

        return "\n\n".join(messages)

    except Exception as e:
        print("❌ get_news error:", e)
        return "⚠️ Error fetching news"