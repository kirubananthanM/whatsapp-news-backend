import sqlite3

DB_PATH = "whatsapp_news.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Create users table if it doesn't exist
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            whatsapp_number TEXT NOT NULL,
            topics TEXT,
            frequency INTEGER
        )
    """)

    conn.commit()
    conn.close()

def connect():
    return sqlite3.connect("users.db")

def save_user(name, number, topic, frequency):
    conn = connect()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            name TEXT, number TEXT PRIMARY KEY,
            topic TEXT, frequency INTEGER
        )
    ''')
    cur.execute('REPLACE INTO users VALUES (?, ?, ?, ?)', (name, number, topic, frequency))
    conn.commit()
    conn.close()

def get_user_topic(number):
    conn = connect()
    cur = conn.cursor()
    cur.execute("SELECT topic FROM users WHERE number = ?", (number,))
    result = cur.fetchone()
    conn.close()
    return result[0] if result else None

def get_all_users():
    conn = connect()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users")
    rows = cur.fetchall()
    conn.close()
    return [{"name": r[0], "number": r[1], "topic": r[2], "frequency": r[3]} for r in rows]
