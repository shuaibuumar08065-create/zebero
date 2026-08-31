import sqlite3

conn = sqlite3.connect("users.db")
cursor = conn.cursor()

columns = [
    row[1]
    for row in cursor.execute(
        "PRAGMA table_info(users)"
    ).fetchall()
]

if "referral_code" not in columns:
    cursor.execute(
        "ALTER TABLE users ADD COLUMN referral_code TEXT"
    )
    print("referral_code added")
else:
    print("referral_code already exists")

if "referred_by" not in columns:
    cursor.execute(
        "ALTER TABLE users ADD COLUMN referred_by TEXT"
    )
    print("referred_by added")
else:
    print("referred_by already exists")

conn.commit()
conn.close()
