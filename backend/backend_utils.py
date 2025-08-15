from dotenv import load_dotenv
import requests
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
import os 

load_dotenv()

TWILIO_SID = os.getenv("TWILIO_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
FROM_WHATSAPP_NUMBER = os.getenv("FROM_WHATSAPP_NUMBER")
client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)

def get_latest_news(topic):
    NEWS_API_KEY = os.getenv("NEWS_API_KEY")
    url = f"https://newsdata.io/api/1/news?apikey={NEWS_API_KEY}&q={topic}&language=en"
    response = requests.get(url)
    data = response.json()
    if data.get("results"):
        article = data["results"][0]
        return f"📰 {article['title']}\n🔗 {article['link']}"
    return "No news found."

def format_number(number):
    """Ensure number is digits only for Twilio."""
    return ''.join(filter(str.isdigit, str(number)))

def send_whatsapp_message(to_number, message):
    try:
        formatted = format_number(to_number)
        client.messages.create(
            from_=FROM_WHATSAPP_NUMBER,
            to=f"whatsapp:{formatted}",
            body=message
        )
        print(f"✅ Message sent to {formatted}")
    except TwilioRestException as e:
        print(f"❌ Twilio error {e.status}: {e.msg} ({e.code})")
        raise
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        raise
