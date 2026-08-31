import sqlite3

conn = sqlite3.connect("users.db")
cursor = conn.cursor()

try:

    cursor.execute("""
    ALTER TABLE tasks
    ADD COLUMN upgrade_level TEXT
    """)

    print("upgrade_level column added.")

except Exception:

    print("upgrade_level already exists.")

conn.commit()
conn.close()
