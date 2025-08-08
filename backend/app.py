from flask import Flask, request, jsonify
from apscheduler.schedulers.background import BackgroundScheduler
import datetime
from backend.backend_utils import get_latest_news, send_whatsapp_message
from db import get_all_users

app = Flask(__name__)
scheduler = BackgroundScheduler()
scheduler.start()

@app.route('/')
def home():
    return "WhatsApp News Backend is running"

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    name = data['name']
    number = data['number']
    topic = data['topic']
    frequency = int(data['frequency'])

    # Save to SQLite
    from db import save_user
    save_user(name, number, topic, frequency)

    # Schedule individual job
    job_id = f"user_{number}"
    scheduler.add_job(
        func=send_news_to_user,
        trigger='interval',
        hours=frequency,
        id=job_id,
        replace_existing=True,
        args=[number]
    )
    return jsonify({"status": "registered", "message": f"{name} will receive news every {frequency} hours."})

def send_news_to_user(number):
    from db import get_user_topic
    topic = get_user_topic(number)
    message = get_latest_news(topic)
    send_whatsapp_message(number, message)

# On server restart, reload all users from DB
def schedule_existing_users():
    users = get_all_users()
    for user in users:
        scheduler.add_job(
            func=send_news_to_user,
            trigger='interval',
            hours=user['frequency'],
            id=f"user_{user['number']}",
            replace_existing=True,
            args=[user['number']]
        )

schedule_existing_users()

if __name__ == '__main__':
    app.run()
