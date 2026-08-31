import sqlite3

conn = sqlite3.connect("users.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS contract_plans(

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    name TEXT NOT NULL,

    price REAL NOT NULL,

    daily_profit REAL NOT NULL,

    duration INTEGER NOT NULL,

    status TEXT DEFAULT 'active'

)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS user_contracts(

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    user_id INTEGER NOT NULL,

    plan_id INTEGER NOT NULL,

    amount REAL NOT NULL,

    daily_profit REAL NOT NULL,

    duration INTEGER NOT NULL,

    days_completed INTEGER DEFAULT 0,

    status TEXT DEFAULT 'active',

    start_date TEXT,

    last_claim TEXT

)
""")

plans = cursor.execute(
    "SELECT COUNT(*) FROM contract_plans"
).fetchone()[0]

if plans == 0:

    cursor.executemany(
        """
        INSERT INTO contract_plans
        (
            name,
            price,
            daily_profit,
            duration
        )
        VALUES
        (?, ?, ?, ?)
        """,
        [

            (
                "Basic",
                1000,
                150,
                30,
            ),

            (
                "Silver",
                5000,
                800,
                30,
            ),

            (
                "Gold",
                10000,
                1700,
                30,
            ),

            (
                "Diamond",
                50000,
                9000,
                30,
            ),

        ],
    )

    print("Default plans added.")

conn.commit()
conn.close()

print("Contract migration completed.")
