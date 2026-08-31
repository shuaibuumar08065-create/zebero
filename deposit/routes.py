from flask import (
    Blueprint,
    render_template,
    request,
    session,
    redirect,
    url_for,
    jsonify,
)

from deposit.models import (
    create_deposit,
    save_virtual_account,
    get_deposit,
    expire_deposit_if_needed,
    complete_deposit,
)

from deposit.flutterwave import (
    create_bank_transfer,
    verify_by_reference,
)


deposit_bp = Blueprint(
    "deposit",
    __name__,
)


# =========================================================
# DEPOSIT PAGE
# =========================================================

@deposit_bp.route("/deposit")
def deposit():

    if "user" not in session:
        return redirect(
            url_for("index")
        )

    return render_template(
        "deposit/index.html"
    )


# =========================================================
# CREATE BANK TRANSFER
# =========================================================

@deposit_bp.route(
    "/deposit/create",
    methods=["POST"],
)
def deposit_create():

    if "user" not in session:
        return redirect(
            url_for("index")
        )

    # -----------------------------------------------------
    # GET AMOUNT
    # -----------------------------------------------------

    try:

        amount = float(
            request.form.get(
                "amount",
                0,
            )
        )

    except (
        TypeError,
        ValueError,
    ):

        return (
            "Invalid deposit amount.",
            400,
        )

    # -----------------------------------------------------
    # MINIMUM DEPOSIT
    # -----------------------------------------------------

    if amount < 1000:

        return (
            "Minimum deposit is ₦1000.",
            400,
        )

    # -----------------------------------------------------
    # USER
    # -----------------------------------------------------

    user = session["user"]

    user_id = user["id"]

    email = user["email"]

    # -----------------------------------------------------
    # ACCOUNT NAME
    # -----------------------------------------------------

    username = "ZEBERO"

    # -----------------------------------------------------
    # CREATE LOCAL DEPOSIT
    # -----------------------------------------------------

    payment = create_deposit(
        user_id,
        amount,
    )

    tx_ref = payment["tx_ref"]

    print("\n==============================================")
    print("LOCAL DEPOSIT CREATED")
    print("==============================================")
    print("USER ID:", user_id)
    print("AMOUNT:", amount)
    print("TX_REF:", tx_ref)
    print("EMAIL:", email)
    print("==============================================")

    # -----------------------------------------------------
    # CREATE FLUTTERWAVE BANK TRANSFER
    # -----------------------------------------------------

    result = create_bank_transfer(
        tx_ref=tx_ref,
        amount=amount,
        email=email,
        name=username,
    )

    # -----------------------------------------------------
    # DEBUG FLUTTERWAVE RESPONSE
    # -----------------------------------------------------

    print("\n========== FLUTTERWAVE CREATE RESPONSE ==========")
    print(result)
    print("==================================================")

    # -----------------------------------------------------
    # CHECK FLUTTERWAVE RESPONSE
    # -----------------------------------------------------

    if not isinstance(result, dict):

        return (
            "<h3>Flutterwave Error</h3>"
            "<pre>"
            f"{result}"
            "</pre>",
            400,
        )

    if result.get("status") != "success":

        return (
            "<h3>Flutterwave Error</h3>"
            "<pre>"
            f"{result}"
            "</pre>",
            400,
        )

    # -----------------------------------------------------
    # GET AUTHORIZATION
    # -----------------------------------------------------

    authorization = (
        result
        .get("meta", {})
        .get("authorization", {})
    )

    if not isinstance(
        authorization,
        dict,
    ):

        authorization = {}

    # -----------------------------------------------------
    # BANK ACCOUNT
    # -----------------------------------------------------

    account_number = authorization.get(
        "transfer_account"
    )

    bank_name = authorization.get(
        "transfer_bank"
    )

    transfer_amount = authorization.get(
        "transfer_amount"
    )

    transfer_note = authorization.get(
        "transfer_note",
        "Please make a bank transfer to ZEBERO",
    )

    expiration = authorization.get(
        "account_expiration",
        "",
    )

    # -----------------------------------------------------
    # DEBUG AUTHORIZATION
    # -----------------------------------------------------

    print("\n========== FLUTTERWAVE AUTHORIZATION ==========")
    print("ACCOUNT NUMBER:", account_number)
    print("BANK:", bank_name)
    print("TRANSFER AMOUNT:", transfer_amount)
    print("TRANSFER NOTE:", transfer_note)
    print("EXPIRATION:", expiration)
    print("================================================")

    # -----------------------------------------------------
    # ACCOUNT WAS NOT GENERATED
    # -----------------------------------------------------

    if not account_number:

        return (
            "<h3>Bank account was not generated.</h3>"
            "<pre>"
            f"{result}"
            "</pre>",
            400,
        )

    # -----------------------------------------------------
    # FALLBACK AMOUNT
    # -----------------------------------------------------

    if not transfer_amount:

        transfer_amount = amount

    # -----------------------------------------------------
    # SAVE VIRTUAL ACCOUNT
    # -----------------------------------------------------

    save_virtual_account(
        tx_ref,
        account_number,
        bank_name or "Flutterwave MFB",
        "ZEBERO",
    )

    # -----------------------------------------------------
    # TRANSFER PAGE
    # -----------------------------------------------------

    return render_template(
        "deposit/transfer.html",

        amount=float(
            transfer_amount
        ),

        account_number=account_number,

        bank_name=(
            bank_name
            or "Flutterwave MFB"
        ),

        tx_ref=tx_ref,

        transfer_note=transfer_note,

        expiration=expiration,

        expires_at=payment[
            "expires_at"
        ].isoformat(),
    )


# =========================================================
# CHECK DEPOSIT STATUS
#
# This endpoint is called by transfer.html every 5 seconds.
# =========================================================

@deposit_bp.route(
    "/deposit/status/<tx_ref>",
    methods=["GET"],
)
def deposit_status(tx_ref):

    # -----------------------------------------------------
    # LOGIN CHECK
    # -----------------------------------------------------

    if "user" not in session:

        return jsonify({
            "success": False,
            "message": "Not logged in.",
        }), 401

    # -----------------------------------------------------
    # GET LOCAL DEPOSIT
    # -----------------------------------------------------

    deposit = get_deposit(
        tx_ref
    )

    if not deposit:

        return jsonify({
            "success": False,
            "message": "Deposit not found.",
        }), 404

    # -----------------------------------------------------
    # SECURITY CHECK
    # -----------------------------------------------------

    if int(
        deposit["user_id"]
    ) != int(
        session["user"]["id"]
    ):

        return jsonify({
            "success": False,
            "message": "Unauthorized.",
        }), 403

    # -----------------------------------------------------
    # EXPIRE LOCALLY
    # -----------------------------------------------------

    expire_deposit_if_needed(
        tx_ref
    )

    deposit = get_deposit(
        tx_ref
    )

    # -----------------------------------------------------
    # ALREADY SUCCESSFUL
    # -----------------------------------------------------

    if deposit["status"] == "successful":

        return jsonify({

            "success": True,

            "status": "successful",

            "amount": float(
                deposit["amount"]
            ),

            "tx_ref": tx_ref,

            "new_balance": None,

        })

    # -----------------------------------------------------
    # EXPIRED
    # -----------------------------------------------------

    if deposit["status"] == "expired":

        return jsonify({

            "success": True,

            "status": "expired",

            "amount": float(
                deposit["amount"]
            ),

            "tx_ref": tx_ref,

        })

    # -----------------------------------------------------
    # ONLY VERIFY PENDING
    # -----------------------------------------------------

    if deposit["status"] == "pending":

        print(
            "\n=============================================="
        )

        print(
            "CHECKING FLUTTERWAVE PAYMENT"
        )

        print(
            "TX_REF:",
            tx_ref,
        )

        print(
            "LOCAL AMOUNT:",
            deposit["amount"],
        )

        # -------------------------------------------------
        # ASK FLUTTERWAVE
        # -------------------------------------------------

        verification = verify_by_reference(
            tx_ref
        )

        print(
            "FLUTTERWAVE VERIFICATION:"
        )

        print(
            verification
        )

        print(
            "=============================================="
        )

        # -------------------------------------------------
        # CHECK RESPONSE
        # -------------------------------------------------

        if isinstance(
            verification,
            dict,
        ):

            if verification.get(
                "status"
            ) == "success":

                data = verification.get(
                    "data",
                    {},
                )

                if isinstance(
                    data,
                    dict,
                ):

                    # -------------------------------------
                    # FLUTTERWAVE STATUS
                    # -------------------------------------

                    flw_status = str(
                        data.get(
                            "status",
                            "",
                        )
                    ).lower()

                    # -------------------------------------
                    # TX REF
                    # -------------------------------------

                    flw_tx_ref = (
                        data.get(
                            "tx_ref"
                        )
                        or data.get(
                            "reference"
                        )
                    )

                    # -------------------------------------
                    # CURRENCY
                    # -------------------------------------

                    flw_currency = str(
                        data.get(
                            "currency",
                            "",
                        )
                    ).upper()

                    # -------------------------------------
                    # AMOUNT
                    # -------------------------------------

                    try:

                        flw_amount = float(
                            data.get(
                                "amount",
                                0,
                            )
                        )

                    except (
                        TypeError,
                        ValueError,
                    ):

                        flw_amount = 0

                    # -------------------------------------
                    # LOCAL AMOUNT
                    # -------------------------------------

                    local_amount = float(
                        deposit["amount"]
                    )

                    print(
                        "STATUS:",
                        flw_status,
                    )

                    print(
                        "TX_REF:",
                        flw_tx_ref,
                    )

                    print(
                        "AMOUNT:",
                        flw_amount,
                    )

                    print(
                        "CURRENCY:",
                        flw_currency,
                    )

                    # -------------------------------------
                    # STRICT VERIFICATION
                    # -------------------------------------

                    if (
                        flw_status
                        in (
                            "successful",
                            "succeeded",
                        )

                        and flw_tx_ref
                        == tx_ref

                        and flw_currency
                        == "NGN"

                        and flw_amount
                        >= local_amount
                    ):

                        # ---------------------------------
                        # FLUTTERWAVE REFERENCE
                        # ---------------------------------

                        flw_ref = (
                            data.get(
                                "flw_ref"
                            )

                            or str(
                                data.get(
                                    "id",
                                    ""
                                )
                            )
                        )

                        # ---------------------------------
                        # COMPLETE DEPOSIT
                        # ---------------------------------

                        print(
                            "\nPAYMENT VERIFIED!"
                        )

                        print(
                            "CREDITING USER BALANCE..."
                        )

                        result = complete_deposit(
                            tx_ref=tx_ref,
                            flw_ref=flw_ref,
                        )

                        print(
                            "AUTO DEPOSIT RESULT:"
                        )

                        print(
                            result
                        )

                        # ---------------------------------
                        # SUCCESS
                        # ---------------------------------

                        if result.get(
                            "success"
                        ):

                            return jsonify({

                                "success": True,

                                "status": "successful",

                                "amount": local_amount,

                                "tx_ref": tx_ref,

                                "new_balance":
                                    result.get(
                                        "new_balance"
                                    ),

                            })

    # -----------------------------------------------------
    # REFRESH LOCAL DEPOSIT
    # -----------------------------------------------------

    deposit = get_deposit(
        tx_ref
    )

    # -----------------------------------------------------
    # FINAL RESPONSE
    # -----------------------------------------------------

    return jsonify({

        "success": True,

        "status": deposit["status"],

        "amount": float(
            deposit["amount"]
        ),

        "tx_ref": deposit["tx_ref"],

        "expires_at": str(
            deposit["expires_at"]
        ),

    })
