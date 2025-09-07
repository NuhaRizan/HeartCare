import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '../users.db')

def column_exists(cursor, table, column):
    cursor.execute(f"PRAGMA table_info({table})")
    return any(col[1] == column for col in cursor.fetchall())

def add_is_admin_column():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    if not column_exists(c, 'users', 'is_admin'):
        c.execute('ALTER TABLE users ADD COLUMN is_admin INTEGER DEFAULT 0')
        print('Added is_admin column to users table.')
    else:
        print('is_admin column already exists.')
    conn.commit()
    conn.close()

if __name__ == '__main__':
    add_is_admin_column() 