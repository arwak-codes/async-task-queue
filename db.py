import sqlite3
from config import DATABASE_PATH

def get_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    return conn

def create_table():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS items(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item VARCHAR(20) NOT NULL,
            status VARCHAR(20) NOT NULL DEFAULT 'pending'
            )
        ''')
    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_table()
    print("Database and Table created succesfully!")
