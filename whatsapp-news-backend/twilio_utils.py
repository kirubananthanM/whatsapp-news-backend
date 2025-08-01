from twilio.rest import Client
from dotenv import load_dotenv
import os

load_dotenv()

TWILIO_SID = os.getenv("TWILIO_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
FROM_WHATSAPP_NUMBER = os.getenv("FROM_WHATSAPP_NUMBER")
client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)

def send_whatsapp(to_number, message):
    client.messages.create(
        from_=FROM_WHATSAPP_NUMBER,
        to=f"whatsapp:{to_number}",
        body=message
    )
