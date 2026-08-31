from functools import wraps

from flask import (
    session,
    redirect,
    url_for,
)


def admin_required(func):

    @wraps(func)
    def wrapper(*args, **kwargs):

        if not session.get("admin_logged_in"):
            return redirect(
                url_for("admin_login.admin_login")
            )

        return func(*args, **kwargs)

    return wrapper
