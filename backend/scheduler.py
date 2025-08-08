import time
from datetime import datetime, timedelta
from backend.models import get_users
from news import get_news
from backend.twilio_utils import send_whatsapp_message
import sqlite3

def update_last_sent(user_id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("UPDATE users SET last_sent = datetime('now') WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()

def send_messages():
    users = get_users()
    for user in users:
        id, name, email, password, number, topic, freq, last_sent = user
        last_sent_time = datetime.strptime(last_sent, "%Y-%m-%d %H:%M:%S")
        if datetime.now() >= last_sent_time + timedelta(hours=freq):
            news = get_news(topic)
            send_whatsapp(number, f"Hello {name}, here's your news update:\n\n{news}")
            update_last_sent(id)

if __name__ == "__main__":
    while True:
        send_messages()
        time.sleep(300)  # Check every 5 mins
