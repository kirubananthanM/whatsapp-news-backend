from flask import Flask, request, jsonify
from apscheduler.schedulers.background import BackgroundScheduler
from backend.backend_utils import get_latest_news, send_whatsapp_message
from backend.db import get_all_users, init_db, save_user, get_user_topic
import os

# Init database
init_db()

app = Flask(__name__)
scheduler = BackgroundScheduler()
scheduler.start()

# Variables you can change anytime
TEST_WHATSAPP_NUMBER = os.getenv("FROM_WHATSAPP_NUMBER")  # Your test number
TEST_MESSAGE = "join material-claws"  # The single message content

@app.route('/')
def home():
    return "WhatsApp News Backend is running"

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    save_user(data['name'], data['number'], data['topic'], int(data['frequency']), data['email'])
    return jsonify({"status": "saved", "message": "User data saved successfully"})

@app.route('/start', methods=['POST'])
def start_service():
    # 1️⃣ Send single WhatsApp message
    send_whatsapp_message(TEST_WHATSAPP_NUMBER, TEST_MESSAGE)

    # 2️⃣ Start periodic jobs for all users
    schedule_existing_users()

    return jsonify({"status": "started", "message": "Service started and test message sent"})

@app.route('/stop', methods=['POST'])
def stop_service():
    scheduler.remove_all_jobs()
    return jsonify({"status": "stopped", "message": "All scheduled jobs stopped"})

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

if __name__ == '__main__':
    app.run()
