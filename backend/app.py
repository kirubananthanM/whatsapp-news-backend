from flask import Flask, request, jsonify
from apscheduler.schedulers.background import BackgroundScheduler
from backend.backend_utils import get_latest_news, send_whatsapp_message
from backend.db import init_db, save_user, get_all_users, get_user_topic

init_db()

app = Flask(__name__)
scheduler = BackgroundScheduler()
scheduler.start()

@app.route('/')
def home():
    return "WhatsApp News Backend is running"


@app.route('/register', methods=['POST'])
def register():
    data = request.json or {}
    name = data.get('name')
    number = data.get('number')  # Raw digits (e.g., "919876543210")
    topic = data.get('topic')
    frequency = int(data.get('frequency', 12))
    send_whatsapp_message("919787589869", "Hello from Render test")

    if not (name and number and topic):
        return jsonify({"status": "error", "message": "Missing fields"}), 400

    # Save to DB
    save_user(name, number, topic, frequency)

    # Send first news immediately
    try:
        first_news = get_latest_news(topic)
        initial_message = f"Hi {name}! 👋\nHere’s your latest '{topic}' news:\n\n{first_news}"
        send_whatsapp_message(number, initial_message)
    except Exception as e:
        print(f"Error sending first news: {e}")

    # Schedule future jobs
    job_id = f"user_{number}"
    scheduler.add_job(
        func=send_news_to_user,
        trigger='interval',
        hours=frequency,
        id=job_id,
        replace_existing=True,
        args=[number]
    )

    return jsonify({
        "status": "registered",
        "message": f"{name} will now receive '{topic}' news every {frequency} hours, starting now."
    })


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
