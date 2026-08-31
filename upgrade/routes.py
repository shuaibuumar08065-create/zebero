from flask import (
    session,
    redirect,
    render_template,
)

from upgrade.models import (
    has_active_contract,
)

from contract.models import (
    get_contract_plans,
)


def upgrade_page():

    if "user" not in session:
        return redirect("/login")

    plans = get_contract_plans()

    return render_template(
        "upgrade/index.html",
        plans=plans,
    )


def check_upgrade():

    if "user" not in session:
        return redirect("/login")

    user_id = session["user"]["id"]

    if has_active_contract(user_id):
        return True

    return False
