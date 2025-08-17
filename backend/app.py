import sqlite3
import time
from flask import Flask, request, jsonify
from flask_cors import CORS # type: ignore
from twilio.base.exceptions import TwilioRestException

from backend.db import DB_PATH, init_db, save_user, update_last_sent
from backend.backend_utils import get_latest_news, send_whatsapp_message
from backend.news import get_news

app = Flask(__name__)
CORS(app)

print("🚀 Flask app started, waiting for requests...")
init_db()

@app.route("/", methods=["GET"])
def root():
    return "OK", 200

@app.route("/twilio-check")
def twilio_check():
    try:
        client.api.accounts(TWILIO_ACCOUNT_SID).fetch()
        return {"status": "ok", "msg": "✅ Twilio credentials valid"}, 200
    except Exception as e:
        return {"status": "error", "msg": str(e)}, 500



@app.route("/register", methods=["POST"])
def register():
    try:
        data = request.get_json(force=True)
        print("📩 /register hit:", data)

        name = data.get("name")
        number = data.get("number")
        topic = data.get("topic")
        frequency = int(data.get("frequency", 1))

        # Save to DB
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute(
            "INSERT INTO users (name, number, topic, frequency, last_sent_at) VALUES (?, ?, ?, ?, ?)",
            (name, number, topic, frequency, int(time.time())),
        )
        conn.commit()
        conn.close()

        # Send first WhatsApp message (test)
        try:
            send_whatsapp_message(number, "✅ You are registered! First news will come soon.")
            print(f"✅ First message sent to {number}")
        except Exception as twilio_error:
            print("❌ Twilio send error:", str(twilio_error))
            return jsonify({"error": "Twilio send failed", "details": str(twilio_error)}), 500

        return jsonify({"status": "ok", "msg": f"User {name} registered"}), 200

    except Exception as e:
        print("❌ Error in /register:", str(e))
        return jsonify({"error": "Register failed", "details": str(e)}), 500



# (optional) simple healthcheck for Render
@app.route("/health", methods=["GET"])
def health():
    return jsonify({"ok": True}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

DB_PATH = "/opt/render/project/src/db.sqlite3"  # or your DB path

@app.route("/tick", methods=["GET"])
def tick():
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT id, name, number, topic, frequency, last_sent_at FROM users")
        users = c.fetchall()
        conn.close()

        now = int(time.time())

        for user in users:
            user_id, name, number, topic, frequency, last_sent_at = user

            if last_sent_at is None:
                last_sent_at = 0

            # frequency is in minutes, so convert to seconds
            if now - last_sent_at >= frequency * 60:
                try:
                    news = get_news(topic)
                    if news:
                        message = "📰 Here are your latest news:\n\n" + "\n".join(news[:3])
                        send_whatsapp_message(number, message)

                        # update last_sent_at
                        conn = sqlite3.connect(DB_PATH)
                        c = conn.cursor()
                        c.execute("UPDATE users SET last_sent_at=? WHERE id=?", (now, user_id))
                        conn.commit()
                        conn.close()

                        print(f"✅ Sent news to {number}")
                except Exception as e:
                    print(f"❌ Failed to send news to {number}: {e}")

        return jsonify({"status": "ok", "msg": "tick processed"}), 200

    except Exception as e:
        print("❌ Error in /tick:", e)
        return jsonify({"status": "error", "msg": str(e)}), 500

