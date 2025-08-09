import sqlite3

DB_PATH = "whatsapp_news.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            whatsapp_number TEXT NOT NULL,
            topics TEXT,
            frequency INTEGER,
            email TEXT
        )
    """)
    conn.commit()
    conn.close()

def connect():
    return sqlite3.connect(DB_PATH)

def save_user(name, number, topic, frequency, email):
    conn = connect()
    cur = conn.cursor()
    cur.execute('''
        INSERT OR REPLACE INTO users (name, whatsapp_number, topics, frequency, email)
        VALUES (?, ?, ?, ?, ?)
    ''', (name, number, topic, frequency, email))
    conn.commit()
    conn.close()

def get_user_topic(number):
    conn = connect()
    cur = conn.cursor()
    cur.execute("SELECT topics FROM users WHERE whatsapp_number = ?", (number,))
    result = cur.fetchone()
    conn.close()
    return result[0] if result else None

def get_all_users():
    conn = connect()
    cur = conn.cursor()
    cur.execute("SELECT name, whatsapp_number, topics, frequency, email FROM users")
    rows = cur.fetchall()
    conn.close()
    return [
        {"name": r[0], "number": r[1], "topic": r[2], "frequency": r[3], "email": r[4]}
        for r in rows
    ]
