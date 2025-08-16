import time
from flask import Flask, request, jsonify
from flask_cors import CORS
from twilio.base.exceptions import TwilioRestException

from backend.db import init_db, save_user, update_last_sent
from backend.backend_utils import get_latest_news, send_whatsapp_message

app = Flask(__name__)
CORS(app)

print("🚀 Flask app started, waiting for requests...")
init_db()

@app.route("/", methods=["GET"])
def root():
    return "OK", 200

@app.route("/register", methods=["POST"])
def register():
    try:
        data = request.json or {}
        print("📩 /register hit:", data)

        name = (data.get("name") or "").strip()
        number = (data.get("number") or "").strip()      # e.g. 919xxxxxxx
        topic = (data.get("topic") or "").strip()
        # treat frequency as MINUTES from the app
        frequency_minutes = int(data.get("frequency", 2))

        if not (name and number and topic and frequency_minutes > 0):
            return jsonify({"status": "error",
                            "message": "Missing name/number/topic or invalid frequency"}), 400

        # Save or update user
        save_user(name, number, topic, frequency_minutes)

        # Compose first (3 links) message & send immediately
        news = get_latest_news(topic, count=3)
        msg = f"Hi {name}! 👋\nHere are the latest '{topic}' updates:\n\n{news}"
        try:
            send_whatsapp_message(number, msg)
            update_last_sent(number, int(time.time()))  # so cron won’t send again immediately
        except TwilioRestException as e:
            return jsonify({"status": "error", "message": f"Twilio error: {e.msg}"}), 500
        except Exception as e:
            return jsonify({"status": "error", "message": f"Send error: {e}"}), 500

        return jsonify({
            "status": "registered",
            "message": f"You will receive '{topic}' news every {frequency_minutes} minute(s)."
        }), 200

    except Exception as e:
        print("❌ Error in /register:", e)
        return jsonify({"status": "error", "message": "Internal server error"}), 500

# (optional) simple healthcheck for Render
@app.route("/health", methods=["GET"])
def health():
    return jsonify({"ok": True}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
