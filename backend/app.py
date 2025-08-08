from flask import Flask, request, jsonify
from apscheduler.schedulers.background import BackgroundScheduler
from backend.backend_utils import get_latest_news, send_whatsapp_message
from backend.db import save_user, get_user_topic, get_all_users, init_db

# Ensure DB exists
init_db()

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

    save_user(name, number, topic, frequency)

    scheduler.add_job(
        func=send_news_to_user,
        trigger='interval',
        hours=frequency,
        id=f"user_{number}",
        replace_existing=True,
        args=[number]
    )

    return jsonify({"status": "registered", "message": f"{name} will receive news every {frequency} hours."})

def send_news_to_user(number):
    topic = get_user_topic(number)
    message = get_latest_news(topic)
    send_whatsapp_message(number, message)

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
