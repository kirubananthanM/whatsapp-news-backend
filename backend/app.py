from flask import Flask, request, jsonify
from apscheduler.schedulers.background import BackgroundScheduler
from backend_utils import get_latest_news, send_whatsapp_message
from db import init_db, save_user, get_all_users, get_user_topic

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

    # Schedule periodic job
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

@app.route('/stop', methods=['POST'])
def stop():
    number = request.json.get('number')
    job_id = f"user_{number}"
    scheduler.remove_job(job_id)
    return jsonify({"status": "stopped", "message": f"News sending stopped for {number}."})

def send_news_to_user(number):
    topic = get_user_topic(number)
    if topic:
        message = get_latest_news(topic)
        send_whatsapp_message(number, message)

# On server restart, reschedule all users
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
