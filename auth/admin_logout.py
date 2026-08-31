from flask import Blueprint, redirect, url_for, session

admin_logout_bp = Blueprint("admin_logout", __name__)


@admin_logout_bp.route("/admin/logout")
def admin_logout():
    session.pop("admin_logged_in", None)
    session.pop("admin_id", None)
    session.pop("admin_username", None)
    return redirect(url_for("admin_login.admin_login"))
