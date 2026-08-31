from flask import (
    render_template,
    session,
    redirect,
    request,
)

from contract.models import (
    get_contract_plans,
    get_user_contracts,
    get_plan,
    create_contract,
)

from dailycheck.models import (
    get_balance,
    update_balance,
)


def contract_page():
    if "user" not in session:
        return redirect("/login")

    user_id = session["user"]["id"]
    plans = get_contract_plans()
    contracts = get_user_contracts(user_id)
    balance = get_balance(user_id)

    return render_template(
        "contract/index.html",
        plans=plans,
        contracts=contracts,
        balance=balance,
    )


def buy_page():
    if "user" not in session:
        return redirect("/login")

    plan_id = request.args.get("id")
    if not plan_id:
        return redirect("/upgrade")

    plan = get_plan(plan_id)
    if not plan:
        return redirect("/upgrade")

    user_id = session["user"]["id"]
    balance = get_balance(user_id)

    return render_template(
        "upgrade/buy.html",
        plan=plan,
        balance=balance,
    )


def buy_contract():
    if "user" not in session:
        return redirect("/login")

    plan_id = request.args.get("id")
    quantity = int(request.args.get("quantity", 1))

    if quantity < 1:
        quantity = 1
    if quantity > 10:
        quantity = 10

    if not plan_id:
        return redirect("/upgrade")

    plan = get_plan(plan_id)
    if not plan:
        return redirect("/upgrade")

    user_id = session["user"]["id"]
    balance = get_balance(user_id)
    total_price = plan["price"] * quantity

    if balance < total_price:
        return redirect("/upgrade/buy?id=" + str(plan_id))

    update_balance(user_id, balance - total_price)
    create_contract(user_id, plan, quantity)

    return redirect("/upgrade")
