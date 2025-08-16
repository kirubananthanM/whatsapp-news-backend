import os, sqlite3, time
from pathlib import Path

DB_PATH = os.getenv("DB_PATH", "db.sqlite3")
Path(os.path.dirname(DB_PATH) or ".").mkdir(parents=True, exist_ok=True)

def _conn():
    # check_same_thread=False lets Flask and cron both use sqlite
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def init_db():
    with _conn() as con:
        con.execute("""
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            number TEXT NOT NULL UNIQUE,
            topic TEXT NOT NULL,
            frequency_minutes INTEGER NOT NULL,
            last_sent_at INTEGER
        )
        """)
        con.commit()

def save_user(name, number, topic, frequency_minutes):
    with _conn() as con:
        con.execute("""
            INSERT INTO users(name, number, topic, frequency_minutes, last_sent_at)
            VALUES (?, ?, ?, ?, NULL)
            ON CONFLICT(number) DO UPDATE SET
                name=excluded.name,
                topic=excluded.topic,
                frequency_minutes=excluded.frequency_minutes
        """, (name, number, topic, frequency_minutes))
        con.commit()

def update_last_sent(number, when_ts=None):
    when_ts = when_ts or int(time.time())
    with _conn() as con:
        con.execute("UPDATE users SET last_sent_at=? WHERE number=?", (when_ts, number))
        con.commit()

def all_users():
    with _conn() as con:
        cur = con.execute("SELECT name, number, topic, frequency_minutes, last_sent_at FROM users")
        rows = cur.fetchall()
    # return list of dicts
    return [
        dict(name=r[0], number=r[1], topic=r[2],
             frequency_minutes=r[3], last_sent_at=r[4])
        for r in rows
    ]
