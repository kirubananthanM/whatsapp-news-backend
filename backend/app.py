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
    try:
        data = request.json or {}
        name = data.get('name')
        number = data.get('number')
        topic = data.get('topic')
        frequency = int(data.get('frequency', 2))  # default 2 minutes

        if not (name and number and topic):
            return jsonify({"status": "error", "message": "Missing name, number, or topic"}), 400

        save_user(name, number, topic, frequency)

        first_news = get_latest_news(topic, count=3)
        initial_message = f"Hi {name}! 👋\nHere’s your latest '{topic}' news:\n\n{first_news}"

        send_whatsapp_message(number, initial_message)

        job_id = f"user_{number}"
        scheduler.add_job(
            func=send_news_to_user,
            trigger='interval',
            minutes=frequency,  # CHANGED from hours to minutes
            id=job_id,
            replace_existing=True,
            args=[number]
        )

        return jsonify({
            "status": "registered",
            "message": f"{name} will now receive '{topic}' news every {frequency} minutes."
        })

    except TwilioRestException as e:
        return jsonify({"status": "error", "message": f"Twilio error: {e.msg}"}), 500
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    
    
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
