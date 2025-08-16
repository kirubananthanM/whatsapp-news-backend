import os, requests
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

# ---- Twilio client from env ----
ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
AUTH_TOKEN  = os.getenv("TWILIO_AUTH_TOKEN")
FROM_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_FROM")  # e.g. whatsapp:+14155238886
client = Client(ACCOUNT_SID, AUTH_TOKEN)

# ---- News fetcher: returns 3 items merged into one text ----
def get_latest_news(topic, count=3):
    api_key = os.getenv("NEWS_API_KEY")
    url = f"https://newsdata.io/api/1/news?apikey={api_key}&q={topic}&language=en"
    try:
        r = requests.get(url, timeout=12)
        r.raise_for_status()
        data = r.json()
    except Exception as e:
        return f"No news found (API error: {e})"

    results = (data or {}).get("results") or []
    if not results:
        return "No news found."

    items = []
    for art in results[:count]:
        title = art.get("title") or "Untitled"
        link = art.get("link") or ""
        items.append(f"📰 {title}\n🔗 {link}")

    return "\n\n".join(items)

# ---- Number utility ----
def digits_only(number):
    return "".join(ch for ch in str(number) if ch.isdigit())

# ---- WhatsApp sender with clear error logs ----
def send_whatsapp_message(to_number, message):
    to = f"whatsapp:{digits_only(to_number)}"
    try:
        client.messages.create(from_=FROM_WHATSAPP_NUMBER, to=to, body=message)
        print(f"✅ Message sent to {to}")
    except TwilioRestException as e:
        print(f"❌ Twilio error {e.status}: {e.msg} ({e.code})")
        raise
    except Exception as e:
        print(f"❌ Unexpected send error: {e}")
        raise
