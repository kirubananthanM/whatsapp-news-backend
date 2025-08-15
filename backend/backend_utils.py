from dotenv import load_dotenv
import requests
from twilio.rest import Client
import os 

load_dotenv()

TWILIO_SID = os.getenv("TWILIO_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
FROM_WHATSAPP_NUMBER = os.getenv("FROM_WHATSAPP_NUMBER")
client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)

def get_latest_news(topic):
    url = f"https://newsdata.io/api/1/news?apikey=your_api_key&q={topic}&language=en"
    response = requests.get(url)
    data = response.json()
    if data.get("results"):
        article = data["results"][0]
        return f"📰 {article['title']}\n🔗 {article['link']}"
    return "No news found."

from twilio.base.exceptions import TwilioRestException

def send_whatsapp_message(to_number, message):
    try:
        client.messages.create(
            from_=FROM_WHATSAPP_NUMBER,
            to=f"whatsapp:{to_number}",
            body=message
        )
        print(f"Message sent to {to_number}")
    except TwilioRestException as e:
        print(f"Twilio error {e.status}: {e.msg} ({e.code})")
        raise
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise

