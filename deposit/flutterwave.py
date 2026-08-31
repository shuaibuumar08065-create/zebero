import os
import requests

from dotenv import load_dotenv


load_dotenv()


FLW_SECRET_KEY = os.getenv(
    "FLW_SECRET_KEY",
    "",
).strip()

BASE_URL = os.getenv(
    "FLW_BASE_URL",
    "https://api.flutterwave.com/v3",
).rstrip("/")


# =========================================================
# HEADERS
# =========================================================

def headers():
    return {
        "Authorization": f"Bearer {FLW_SECRET_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }


# =========================================================
# ERROR
# =========================================================

def _error(message, response=None):

    result = {
        "status": "error",
        "message": message,
    }

    if response is not None:

        result["http_status"] = response.status_code

        try:
            result["response"] = response.json()
        except Exception:
            result["response"] = response.text

    return result


# =========================================================
# CREATE BANK TRANSFER
# =========================================================

def create_bank_transfer(
    tx_ref,
    amount,
    email,
    name,
    phone_number=None,
):

    if not FLW_SECRET_KEY:
        return _error(
            "FLW_SECRET_KEY is missing from .env"
        )

    payload = {
        "tx_ref": tx_ref,
        "amount": float(amount),
        "currency": "NGN",
        "email": email,
        "fullname": name,
        "narration": "ZEBERO Deposit",
    }

    if phone_number:
        payload["phone_number"] = phone_number

    try:

        response = requests.post(
            f"{BASE_URL}/charges?type=bank_transfer",
            headers=headers(),
            json=payload,
            timeout=30,
        )

        try:
            return response.json()

        except ValueError:
            return _error(
                "Flutterwave returned invalid JSON.",
                response,
            )

    except requests.RequestException as e:

        return _error(str(e))


# =========================================================
# VERIFY BY TRANSACTION ID
# =========================================================

def verify_payment(transaction_id):

    if not FLW_SECRET_KEY:
        return _error(
            "FLW_SECRET_KEY is missing from .env"
        )

    try:

        response = requests.get(
            f"{BASE_URL}/transactions/{transaction_id}/verify",
            headers=headers(),
            timeout=30,
        )

        try:
            return response.json()

        except ValueError:
            return _error(
                "Flutterwave returned invalid JSON.",
                response,
            )

    except requests.RequestException as e:

        return _error(str(e))


# =========================================================
# VERIFY BY TX_REF
# =========================================================

def verify_by_reference(tx_ref):

    if not FLW_SECRET_KEY:
        return _error(
            "FLW_SECRET_KEY is missing from .env"
        )

    try:

        response = requests.get(
            f"{BASE_URL}/transactions/verify_by_reference",
            headers=headers(),
            params={
                "tx_ref": tx_ref,
            },
            timeout=30,
        )

        try:
            result = response.json()

        except ValueError:
            return _error(
                "Flutterwave returned invalid JSON.",
                response,
            )

        return result

    except requests.RequestException as e:

        return _error(str(e))


# =========================================================
# VERIFY CHARGE
# =========================================================

def verify_charge(transaction_id):

    return verify_payment(
        transaction_id
    )


# =========================================================
# GET BANKS
# =========================================================

def get_banks():

    if not FLW_SECRET_KEY:
        return _error(
            "FLW_SECRET_KEY is missing from .env"
        )

    try:

        response = requests.get(
            f"{BASE_URL}/banks/NG",
            headers=headers(),
            timeout=30,
        )

        try:
            return response.json()

        except ValueError:
            return _error(
                "Flutterwave returned invalid JSON.",
                response,
            )

    except requests.RequestException as e:

        return _error(str(e))


# =========================================================
# TRANSFER FEE
# =========================================================

def transfer_fee(amount):

    if not FLW_SECRET_KEY:
        return _error(
            "FLW_SECRET_KEY is missing from .env"
        )

    try:

        response = requests.get(
            f"{BASE_URL}/transactions/fee",
            headers=headers(),
            params={
                "amount": float(amount),
                "currency": "NGN",
                "payment_type": "bank_transfer",
            },
            timeout=30,
        )

        try:
            return response.json()

        except ValueError:
            return _error(
                "Flutterwave returned invalid JSON.",
                response,
            )

    except requests.RequestException as e:

        return _error(str(e))


# =========================================================
# CREATE TRANSFER
# =========================================================

def create_transfer(
    account_bank,
    account_number,
    amount,
    narration,
    reference,
):

    if not FLW_SECRET_KEY:
        return _error(
            "FLW_SECRET_KEY is missing from .env"
        )

    payload = {
        "account_bank": account_bank,
        "account_number": account_number,
        "amount": float(amount),
        "currency": "NGN",
        "reference": reference,
        "narration": narration,
        "debit_currency": "NGN",
    }

    try:

        response = requests.post(
            f"{BASE_URL}/transfers",
            headers=headers(),
            json=payload,
            timeout=30,
        )

        try:
            return response.json()

        except ValueError:
            return _error(
                "Flutterwave returned invalid JSON.",
                response,
            )

    except requests.RequestException as e:

        return _error(str(e))
