from flask import (
    Blueprint,
    render_template,
    request,
    session,
    redirect,
    url_for,
    jsonify,
)
import uuid

from withdraw.models import (
    create_withdrawal_tables,
    get_withdrawal_accounts,
    add_withdrawal_account,
    get_withdrawal_account,
    create_withdrawal,
    update_withdrawal_status,
)

from withdraw.service import (
    get_banks,
    verify_bank_account,
    create_transfer,
)

from models import get_user
from referral.models import (
    get_commission_balance,
    deduct_commission,
    add_commission,
)


withdraw_bp = Blueprint(
    "withdraw",
    __name__,
)


# ==========================================
# CREATE TABLES
# ==========================================

create_withdrawal_tables()


# ==========================================
# WITHDRAW PAGE
# ==========================================

@withdraw_bp.route("/withdraw")
def withdraw():

    if "user" not in session:
        return redirect(url_for("index"))

    user_id = session["user"]["id"]
    accounts = get_withdrawal_accounts(user_id)
    user = get_user(user_id)
    commission = get_commission_balance(user_id)

    from withdraw.models import get_user_withdrawals
    history = get_user_withdrawals(user_id)

    return render_template(
        "withdraw/index.html",
        accounts=accounts,
        user=user,
        commission_balance=commission,
        history=history,
    )


# ==========================================
# ADD ACCOUNT PAGE
# ==========================================

@withdraw_bp.route("/withdraw/add-account")
def add_account():

    if "user" not in session:
        return redirect(url_for("index"))

    return render_template("withdraw/add_account.html")


# ==========================================
# GET BANKS
# ==========================================

@withdraw_bp.route("/withdraw/banks", methods=["GET"])
def banks():

    if "user" not in session:
        return jsonify({
            "status": "error",
            "message": "Not logged in.",
        }), 401

    result = get_banks()

    if not isinstance(result, dict):
        return jsonify({
            "status": "error",
            "message": "Invalid response.",
        }), 500

    return jsonify(result)


# ==========================================
# VERIFY BANK ACCOUNT
# ==========================================

@withdraw_bp.route("/withdraw/verify-account", methods=["POST"])
def verify_account():

    if "user" not in session:
        return jsonify({
            "status": "error",
            "message": "Not logged in.",
        }), 401

    data = request.get_json(silent=True) or {}

    bank_code = str(data.get("bank_code", "")).strip()
    account_number = str(data.get("account_number", "")).strip()

    if not bank_code:
        return jsonify({
            "status": "error",
            "message": "Please select your bank.",
        }), 400

    if not account_number.isdigit():
        return jsonify({
            "status": "error",
            "message": "Invalid account number.",
        }), 400

    if len(account_number) != 10:
        return jsonify({
            "status": "error",
            "message": "Account number must contain 10 digits.",
        }), 400

    result = verify_bank_account(
        account_number=account_number,
        account_bank=bank_code,
    )

    if not isinstance(result, dict):
        return jsonify({
            "status": "error",
            "message": "Invalid Flutterwave response.",
        }), 500

    if result.get("status") != "success":
        return jsonify({
            "status": "error",
            "message": result.get("message") or "Unable to verify bank account.",
        }), 400

    data_res = result.get("data", {})
    if not isinstance(data_res, dict):
        return jsonify({
            "status": "error",
            "message": "Invalid account information.",
        }), 400

    account_name = (data_res.get("account_name") or "").strip()
    if not account_name:
        return jsonify({
            "status": "error",
            "message": "Account name could not be verified.",
        }), 400

    bank_name = data_res.get("bank_name") or "Bank"

    return jsonify({
        "status": "success",
        "account_name": account_name,
        "account_number": account_number,
        "bank_code": bank_code,
        "bank_name": bank_name,
    })


# ==========================================
# SAVE ACCOUNT
# ==========================================

@withdraw_bp.route("/withdraw/save-account", methods=["POST"])
def save_account():

    if "user" not in session:
        return jsonify({
            "status": "error",
            "message": "Not logged in.",
        }), 401

    data = request.get_json(silent=True) or {}
    user_id = session["user"]["id"]

    bank_code = str(data.get("bank_code", "")).strip()
    bank_name = str(data.get("bank_name", "")).strip()
    account_number = str(data.get("account_number", "")).strip()
    account_name = str(data.get("account_name", "")).strip()

    if not bank_code:
        return jsonify({
            "status": "error",
            "message": "Bank is required.",
        }), 400

    if not account_number.isdigit():
        return jsonify({
            "status": "error",
            "message": "Invalid account number.",
        }), 400

    if len(account_number) != 10:
        return jsonify({
            "status": "error",
            "message": "Account number must contain 10 digits.",
        }), 400

    if not account_name:
        return jsonify({
            "status": "error",
            "message": "Account must be verified first.",
        }), 400

    account_id = add_withdrawal_account(
        user_id=user_id,
        bank_code=bank_code,
        bank_name=bank_name,
        account_number=account_number,
        account_name=account_name,
    )

    if not account_id:
        return jsonify({
            "status": "error",
            "message": "This bank account is already saved.",
        }), 409

    return jsonify({
        "status": "success",
        "message": "Bank account added successfully.",
        "account_id": account_id,
    })


# ==========================================
# PROCESS WITHDRAWAL
# ==========================================

@withdraw_bp.route("/withdraw/process", methods=["POST"])
def process_withdrawal():

    if "user" not in session:
        return jsonify({
            "status": "error",
            "message": "Not logged in.",
        }), 401

    data = request.get_json(silent=True) or {}
    user_id = session["user"]["id"]
    account_id = data.get("account_id")
    amount = data.get("amount")

    try:
        amount = float(amount)
    except (TypeError, ValueError):
        return jsonify({
            "status": "error",
            "message": "Invalid amount.",
        }), 400

    if amount < 100:
        return jsonify({
            "status": "error",
            "message": "Minimum withdrawal is ₦100.",
        }), 400

    user = get_user(user_id)
    if not user:
        return jsonify({
            "status": "error",
            "message": "User not found.",
        }), 404

    # Kawai referral commission za a iya cire
    commission = get_commission_balance(user_id)

    if commission < 100:
        return jsonify({
            "status": "error",
            "message": "You can only withdraw referral deposit commission. Refer someone who deposits to earn withdrawable balance.",
        }), 400

    if amount > commission:
        return jsonify({
            "status": "error",
            "message": f"You can only withdraw ₦{commission:.2f} (your referral commission).",
        }), 400

    account = get_withdrawal_account(account_id, user_id)
    if not account:
        return jsonify({
            "status": "error",
            "message": "Invalid bank account.",
        }), 400

    reference = f"ZEB-WTH-{uuid.uuid4().hex[:12].upper()}"
    fee = 0
    total = amount + fee

    if not deduct_commission(user_id, amount):
        return jsonify({
            "status": "error",
            "message": "Insufficient commission balance.",
        }), 400

    withdrawal_id = create_withdrawal(
        user_id=user_id,
        account_id=account_id,
        amount=amount,
        fee=fee,
        total=total,
        reference=reference,
    )

    result = create_transfer(
        account_number=account["account_number"],
        bank_code=account["bank_code"],
        amount=amount,
        account_name=account["account_name"],
        reference=reference,
    )

    if not isinstance(result, dict) or result.get("status") != "success":
        # Refund if transfer failed
        add_commission(user_id, amount)
        update_withdrawal_status(
            withdrawal_id,
            status="failed",
            failure_reason=(
                result.get("message", "Transfer failed")
                if isinstance(result, dict)
                else "Transfer failed"
            ),
        )
        return jsonify({
            "status": "error",
            "message": (
                result.get("message")
                if isinstance(result, dict)
                else None
            ) or "Withdrawal failed. Please try again.",
        }), 400

    update_withdrawal_status(
        withdrawal_id,
        status="successful",
        flutterwave_ref=str(result.get("data", {}).get("id", "")),
    )

    new_commission = get_commission_balance(user_id)
    user = get_user(user_id)
    new_balance = float(user["balance"] or 0) if user else 0

    if "user" in session:
        session["user"]["balance"] = new_balance

    return jsonify({
        "status": "success",
        "message": "Withdrawal successful!",
        "reference": reference,
        "new_balance": new_balance,
        "commission_balance": new_commission,
    })
