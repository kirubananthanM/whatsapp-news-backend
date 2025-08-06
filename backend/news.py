from dotenv import load_dotenv
import requests
import os

load_dotenv()
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

def get_news(topic):
    url = f"https://newsdata.io/api/1/news?apikey={NEWS_API_KEY}&q={topic}&language=en"
    res = requests.get(url).json()
    if res.get("status") == "success" and res.get("results"):
        news = []
        for article in res["results"][:3]:
            title = article.get("title")
            link = article.get("link")
            news.append(f"{title}\n🔗 {link}")
        return "\n\n".join(news)
    return "No news available for now."
