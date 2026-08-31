from flask import (
    session,
    redirect,
    request,
)

from models import get_task
from upgrade.models import get_upgrade_levels
from task.models import (
    already_claimed,
    save_claim,
    add_balance,
)


def claim_task():

    if "user" not in session:
        return redirect("/login")

    user_id = session["user"]["id"]

    task_id = request.args.get("id")

    if not task_id:
        return redirect("/earn")

    task = get_task(task_id)

    if not task:
        return redirect("/earn")

    if already_claimed(user_id, task["id"]):
        return redirect("/earn")

    reward = float(task["reward"])

    if task["task_type"] == "upgrade":

        levels = get_upgrade_levels(user_id)

        quantity = levels.get(
            task["upgrade_level"],
            0,
        )

        if quantity <= 0:
            return redirect("/upgrade")

        reward *= quantity

    add_balance(
        user_id,
        reward,
    )

    save_claim(
        user_id,
        task["id"],
        reward,
    )

    # Update session balance (idan kana amfani da session)
    if "balance" in session["user"]:
        session["user"]["balance"] = float(session["user"].get("balance", 0)) + reward

    return redirect("/earn")
