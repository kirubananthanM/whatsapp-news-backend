from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
import os

FROM_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_FROM")
client = Client(os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN"))

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
        raise  # re-raise so /register can handle it
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise
