import sqlite3

def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT,
            password TEXT,
            whatsapp_number TEXT,
            topic TEXT,
            frequency_hours INTEGER,
            last_sent TEXT
        )
    ''')
    conn.commit()
    conn.close()

def add_user(data):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO users (name, email, password, whatsapp_number, topic, frequency_hours, last_sent)
        VALUES (?, ?, ?, ?, ?, ?, datetime('now', '-1 hour'))
    ''', (
        data['name'], data['email'], data['password'],
        data['whatsapp_number'], data['topic'], data['frequency_hours']
    ))
    conn.commit()
    conn.close()

def get_users():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users")
    rows = c.fetchall()
    conn.close()
    return rows
