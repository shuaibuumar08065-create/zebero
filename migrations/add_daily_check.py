import sqlite3

DATABASE = "users.db"

conn = sqlite3.connect(DATABASE)
cursor = conn.cursor()

try:
    cursor.execute("""
        ALTER TABLE users
        ADD COLUMN daily_day INTEGER DEFAULT 0
    """)
    print("daily_day column added.")
except:
    print("daily_day already exists.")

try:
    cursor.execute("""
        ALTER TABLE users
        ADD COLUMN last_daily_claim TEXT
    """)
    print("last_daily_claim column added.")
except:
    print("last_daily_claim already exists.")

conn.commit()
conn.close()

print("Done.")
