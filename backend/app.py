# app.py
import sqlite3
import os, time
from flask import Flask, request, jsonify
from flask_cors import CORS  # type: ignore
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from backend.news import get_news   # make sure you import at top

from backend.db import DB_PATH, init_db, save_user, update_last_sent, all_users
from backend.backend_utils import send_whatsapp_message

app = Flask(__name__)
CORS(app)

# Twilio client setup
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

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
        data = request.json
        print("📩 /register hit:", data)

        name = data.get("name")
        number = data.get("number")
        topic = data.get("topic")
        frequency = int(data.get("frequency"))

        # save user in DB
        save_user(name, number, topic, frequency)

        # send one welcome message
        send_whatsapp_message(number, "✅ You are registered! First news will come soon.")

        return jsonify({"status": "ok", "msg": "Registered"}), 200

    except Exception as e:
        print("❌ Error in /register:", e)
        return jsonify({"status": "error", "msg": str(e)}), 500


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"ok": True}), 200


@app.route("/tick", methods=["GET"])


@app.route("/tick", methods=["GET"])
def tick():
    try:
        now = int(time.time())
        users = all_users()
        print(f"⏰ Tick called at {now}, checking {len(users)} users")

        for user in users:
            last_sent = user.get("last_sent_at") or 0
            freq_minutes = int(user["frequency"])
            number = user["number"]
            topic = user["topic"]

            if (now - last_sent) >= freq_minutes * 60:
                try:
                    # ✅ fetch news
                    articles = get_news(topic)

                    if not articles:
                        send_whatsapp_message(number, f"⚠️ No news found for {topic} right now.")
                    else:
                        # send top 3 articles
                        news_msg = f"📰 Latest {topic} news:\n\n"
                        for i, a in enumerate(articles[:3], start=1):
                            news_msg += f"{i}. {a['title']}\n{a['url']}\n\n"

                        send_whatsapp_message(number, news_msg)

                    update_last_sent(number, now)
                    print(f"✅ Sent news to {number}")

                except Exception as twilio_err:
                    print(f"❌ Twilio send failed for {number}: {twilio_err}")

        return jsonify({"status": "ok", "msg": "Tick executed"}), 200

    except Exception as e:
        print("❌ Error in /tick:", e)
        return jsonify({"status": "error", "msg": str(e)}), 500


@app.route("/stop", methods=["POST"])
def stop():
    try:
        data = request.json
        number = data.get("number")
        print(f"🛑 Stop requested for {number}")

        # In simplest version → just remove the user from DB
        with sqlite3.connect(DB_PATH) as con:
            con.execute("DELETE FROM users WHERE number=?", (number,))
            con.commit()

        # Optional: send confirmation message
        send_whatsapp_message(number, "🛑 You have been unsubscribed from news updates.")

        return jsonify({"status": "ok", "msg": "Stopped"}), 200

    except Exception as e:
        print("❌ Error in /stop:", e)
        return jsonify({"status": "error", "msg": str(e)}), 500


if __name__ == "__main__":
    print("🚀 Flask app started, waiting for requests...")
    app.run(host="0.0.0.0", port=10000)
