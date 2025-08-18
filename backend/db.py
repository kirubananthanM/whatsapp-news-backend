# db.py
import os, sqlite3, time
from pathlib import Path

DB_PATH = os.getenv("DB_PATH", "db.sqlite3")
Path(os.path.dirname(DB_PATH) or ".").mkdir(parents=True, exist_ok=True)

def _conn():
    # check_same_thread=False lets Flask and cron both use sqlite
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # Ensure table exists with correct schema
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            number TEXT UNIQUE,
            topic TEXT,
            frequency INTEGER,
            last_sent_at INTEGER
        )
    """)
    # Ensure frequency column exists (for old DBs)
    c.execute("PRAGMA table_info(users)")
    columns = [col[1] for col in c.fetchall()]
    if "frequency" not in columns:
        c.execute("ALTER TABLE users ADD COLUMN frequency INTEGER DEFAULT 1")
        print("🔄 Added missing 'frequency' column")
    conn.commit()
    conn.close()
    print("✅ Database initialized with correct schema")

def save_user(name, number, topic, frequency):
    """Insert or update a user (number is UNIQUE key)."""
    with _conn() as con:
        con.execute("""
            INSERT INTO users(name, number, topic, frequency, last_sent_at)
            VALUES (?, ?, ?, ?, NULL)
            ON CONFLICT(number) DO UPDATE SET
                name=excluded.name,
                topic=excluded.topic,
                frequency=excluded.frequency
        """, (name, number, topic, frequency))
        con.commit()

def update_last_sent(number, when_ts=None):
    """Update last_sent_at for a user."""
    when_ts = when_ts or int(time.time())
    with _conn() as con:
        con.execute("UPDATE users SET last_sent_at=? WHERE number=?", (when_ts, number))
        con.commit()

def all_users():
    """Return all users as a list of dicts."""
    with _conn() as con:
        cur = con.execute("SELECT name, number, topic, frequency, last_sent_at FROM users")
        rows = cur.fetchall()
    return [
        dict(name=r[0], number=r[1], topic=r[2],
             frequency=r[3], last_sent_at=r[4])
        for r in rows
    ]
