import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '../../web/users.db')

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        name TEXT,
        email TEXT,
        is_admin INTEGER DEFAULT 0
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        age INTEGER, sex INTEGER, cp INTEGER, trestbps INTEGER, chol INTEGER, fbs INTEGER, restecg INTEGER, thalach INTEGER, exang INTEGER, oldpeak REAL, slope INTEGER, ca INTEGER, thal INTEGER, risk INTEGER,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS report_links (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        report_id TEXT UNIQUE NOT NULL,
        prediction REAL,
        reasoning TEXT,
        recommendations TEXT,
        features TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        expires_at TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )''')
    conn.commit()
    conn.close()

def create_user(username, password, name, email):
    conn = get_db()
    c = conn.cursor()
    c.execute('INSERT INTO users (username, password, name, email) VALUES (?, ?, ?, ?)', (username, generate_password_hash(password), name, email))
    conn.commit()
    conn.close()

def check_user(username, password):
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = c.fetchone()
    conn.close()
    if user and check_password_hash(user['password'], password):
        return user['id']
    return None

def save_record(user_id, features, risk):
    conn = get_db()
    c = conn.cursor()
    c.execute('''INSERT INTO records (user_id, age, sex, cp, trestbps, chol, fbs, restecg, thalach, exang, oldpeak, slope, ca, thal, risk)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', (user_id, *features, risk))
    conn.commit()
    conn.close()

def get_records(user_id):
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM records WHERE user_id = ?', (user_id,))
    records = c.fetchall()
    conn.close()
    return records

def get_user_info(user_id):
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT id, username, name, email FROM users WHERE id = ?', (user_id,))
    user = c.fetchone()
    conn.close()
    return user

def create_admin(username, password, name, email):
    conn = get_db()
    c = conn.cursor()
    c.execute('INSERT INTO users (username, password, name, email, is_admin) VALUES (?, ?, ?, ?, 1)', (username, generate_password_hash(password), name, email))
    conn.commit()
    conn.close()

def check_admin(username, password):
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE username = ? AND is_admin = 1', (username,))
    user = c.fetchone()
    conn.close()
    if user and check_password_hash(user['password'], password):
        return user['id']
    return None

def get_all_users():
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT id, username, name, email, is_admin FROM users')
    users = c.fetchall()
    conn.close()
    return users

def delete_user(user_id):
    conn = get_db()
    c = conn.cursor()
    c.execute('DELETE FROM users WHERE id = ?', (user_id,))
    conn.commit()
    conn.close()

def save_report_link(user_id, report_id, prediction, reasoning, recommendations, features, expires_in_hours=24):
    conn = get_db()
    c = conn.cursor()
    import datetime
    expires_at = datetime.datetime.now() + datetime.timedelta(hours=expires_in_hours)
    c.execute('''INSERT INTO report_links (user_id, report_id, prediction, reasoning, recommendations, features, expires_at)
                 VALUES (?, ?, ?, ?, ?, ?, ?)''', (user_id, report_id, prediction, reasoning, recommendations, features, expires_at))
    conn.commit()
    conn.close()

def get_report_by_id(report_id):
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM report_links WHERE report_id = ? AND expires_at > datetime("now")', (report_id,))
    report = c.fetchone()
    conn.close()
    return report

def cleanup_expired_reports():
    conn = get_db()
    c = conn.cursor()
    c.execute('DELETE FROM report_links WHERE expires_at <= datetime("now")')
    conn.commit()
    conn.close() 