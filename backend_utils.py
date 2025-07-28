import requests
from twilio.rest import Client

TWILIO_SID = "ACbae10f24e7efe3ce8e176be07bb3d450"
TWILIO_AUTH_TOKEN = "61557ff372d44dd738799828392866eb"
FROM_WHATSAPP_NUMBER = "whatsapp:+14155238886"
client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)

def get_latest_news(topic):
    url = f"https://newsdata.io/api/1/news?apikey=your_api_key&q={topic}&language=en"
    response = requests.get(url)
    data = response.json()
    if data.get("results"):
        article = data["results"][0]
        return f"📰 {article['title']}\n🔗 {article['link']}"
    return "No news found."

def send_whatsapp_message(to_number, message):
    client.messages.create(
        from_=FROM_WHATSAPP_NUMBER,
        to=f"whatsapp:{to_number}",
        body=message
    )
