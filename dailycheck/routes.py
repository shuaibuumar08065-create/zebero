from datetime import date

from flask import (
    render_template,
    session,
    redirect,
)

from dailycheck.models import (
    get_daily_data,
    claim_daily,
)


def daily_check():

    if "user" not in session:
        return redirect("/login")

    user = get_daily_data(
        session["user"]["id"]
    )

    claimed_today = (
        user["last_daily_claim"] == str(date.today())
    )

    day = user["daily_day"]

    return render_template(
        "dailycheck/index.html",
        day=day,
        claimed_today=claimed_today,
    )


def claim():

    if "user" not in session:
        return redirect("/login")

    claim_daily(
        session["user"]["id"]
    )

    return redirect("/daily-check")
