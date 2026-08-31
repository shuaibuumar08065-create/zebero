import sqlite3

conn = sqlite3.connect("users.db")
cursor = conn.cursor()

try:
    cursor.execute("""
        ALTER TABLE users
        ADD COLUMN balance REAL DEFAULT 0
    """)
    print("Balance column added.")
except sqlite3.OperationalError:
    print("Balance column already exists.")

conn.commit()
conn.close()
