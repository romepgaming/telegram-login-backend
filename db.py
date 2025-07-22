import sqlite3

DB_NAME = "telegram_sessions.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            phone TEXT PRIMARY KEY,
            session TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_session(phone, session_str):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("REPLACE INTO sessions (phone, session) VALUES (?, ?)", (phone, session_str))
    conn.commit()
    conn.close()

def load_session(phone):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT session FROM sessions WHERE phone = ?", (phone,))
    row = c.fetchone()
    conn.close()
    if row:
        return row[0]
    return None

def delete_session(phone):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM sessions WHERE phone = ?", (phone,))
    conn.commit()
    conn.close()
