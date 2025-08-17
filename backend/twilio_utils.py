from dotenv import load_dotenv
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
import os 

load_dotenv()

TWILIO_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
FROM_NUMBER = os.getenv("TWILIO_WHATSAPP_FROM")

client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)

def format_number(number):
    return ''.join(filter(str.isdigit, str(number)))

def send_whatsapp(to_number, message):
    try:
        formatted = format_number(to_number)
        client.messages.create(
            from_=FROM_NUMBER,
            to=f"whatsapp:{formatted}",
            body=message
        )
        print(f"✅ Scheduled message sent to {formatted}")
    except TwilioRestException as e:
        print(f"❌ Twilio error {e.status}: {e.msg} ({e.code})")
        raise
    except Exception as e:
        print(f"❌ Unexpected scheduler error: {e}")
        raise
