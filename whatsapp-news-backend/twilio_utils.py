from twilio.rest import Client

TWILIO_SID = "ACbae10f24e7efe3ce8e176be07bb3d450"
AUTH_TOKEN = "61557ff372d44dd738799828392866eb"
FROM_NUMBER = "whatsapp:+14155238886"

client = Client(TWILIO_SID, AUTH_TOKEN)

def send_whatsapp(to_number, message):
    client.messages.create(
        from_=FROM_NUMBER,
        to=f"whatsapp:{to_number}",
        body=message
    )
