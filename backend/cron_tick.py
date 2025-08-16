import time
from backend.db import all_users, update_last_sent
from backend.backend_utils import get_latest_news, send_whatsapp_message

def process_due():
    now = int(time.time())
    users = all_users()
    print(f"⏰ cron_tick: checking {len(users)} user(s) at {now}")

    sent_count = 0
    for u in users:
        name = u["name"]
        number = u["number"]
        topic = u["topic"]
        freq = int(u["frequency_minutes"])
        last = u["last_sent_at"] or 0

        due = (now - last) >= (freq * 60)
        if not due:
            continue

        news = get_latest_news(topic, count=3)
        msg = f"Hi {name}! ⏱️ Your '{topic}' updates:\n\n{news}"
        try:
            send_whatsapp_message(number, msg)
            update_last_sent(number, now)
            sent_count += 1
        except Exception as e:
            print(f"❌ Couldn’t send to {number}: {e}")

    print(f"✅ cron_tick done. Messages sent: {sent_count}")

if __name__ == "__main__":
    process_due()
