# backend/backend_utils.py
import os
import requests
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

# Twilio setup
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
FROM_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_FROM", "whatsapp:+14155238886")

# News API setup
NEWS_API_KEY = os.getenv("NEWS_API_KEY", "")
NEWS_API_URL = "https://newsapi.org/v2/top-headlines"

# Initialize Twilio client
client = None
if TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN:
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
else:
    print("⚠️ Warning: Twilio credentials not set. WhatsApp sending will fail.")


# --------------------------
# ✅ Twilio WhatsApp Sending
# --------------------------
def send_whatsapp_message(to_number, message):
    """Send a WhatsApp message using Twilio API."""
    if not client:
        print("❌ Twilio client not initialized (check env vars)")
        return False

    try:
        msg = client.messages.create(
            from_=FROM_WHATSAPP_NUMBER,
            to=f"whatsapp:{to_number}",
            body=message
        )
        print(f"✅ WhatsApp message sent to {to_number}: SID={msg.sid}")
        return True
    except TwilioRestException as e:
        print(f"❌ Twilio error {e.code}: {e.msg}")
        return False
    except Exception as e:
        print(f"❌ Unknown error sending WhatsApp to {to_number}: {e}")
        return False


# --------------------------
# ✅ News Fetching
# --------------------------
def get_latest_news(topic="general", count=3):
    """
    Fetch latest news headlines for a topic.
    Defaults to 3 headlines.
    """
    if not NEWS_API_KEY:
        print("⚠️ NEWS_API_KEY not set. Returning dummy headlines.")
        return [f"[Dummy] News about {topic}"]

    try:
        params = {
            "apiKey": NEWS_API_KEY,
            "q": topic,
            "language": "en",
            "pageSize": count,
        }
        response = requests.get(NEWS_API_URL, params=params, timeout=10)
        data = response.json()

        if response.status_code != 200 or "articles" not in data:
            print(f"❌ Error fetching news: {data}")
            return [f"No news available for {topic}"]

        headlines = []
        for art in data["articles"][:count]:
            title = art.get("title")
            url = art.get("url")
            if title and url:
                headlines.append(f"{title}\n{url}")
            elif title:
                headlines.append(title)

        print(f"✅ Fetched {len(headlines)} news for topic '{topic}'")
        return headlines if headlines else [f"No news available for {topic}"]

    except Exception as e:
        print(f"❌ News API error: {e}")
        return [f"Error fetching news for {topic}"]
