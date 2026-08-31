import sqlite3

from flask import render_template

from config import DATABASE

from auth.admin_required import admin_required


@admin_required
def admin_users():

    conn = sqlite3.connect(DATABASE)

    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM users
        ORDER BY id DESC
    """)

    users = cursor.fetchall()

    conn.close()

    return render_template(
        "admin/users.html",
        users=users,
    )
