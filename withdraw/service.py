import os
import requests


FLW_SECRET_KEY = os.getenv("FLW_SECRET_KEY")

FLW_BASE_URL = "https://api.flutterwave.com/v3"


def flutterwave_headers():
    return {
        "Authorization": f"Bearer {FLW_SECRET_KEY}",
        "Content-Type": "application/json",
    }


# ==========================================
# GET BANK LIST
# ==========================================

def get_banks():
    response = requests.get(
        f"{FLW_BASE_URL}/banks/NG",
        headers=flutterwave_headers(),
        timeout=30,
    )

    try:
        return response.json()
    except Exception:
        return {
            "status": "error",
            "message": "Invalid Flutterwave response.",
        }


# ==========================================
# VERIFY BANK ACCOUNT
# ==========================================

def verify_bank_account(
    account_number,
    account_bank,
):
    response = requests.post(
        f"{FLW_BASE_URL}/accounts/resolve",
        headers=flutterwave_headers(),
        json={
            "account_number": str(account_number),
            "account_bank": str(account_bank),
        },
        timeout=30,
    )

    try:
        return response.json()
    except Exception:
        return {
            "status": "error",
            "message": "Invalid Flutterwave response.",
        }


# ==========================================
# CREATE TRANSFER
# ==========================================

def create_transfer(
    account_number,
    bank_code,
    amount,
    account_name,
    reference,
    narration="ZEBERO Withdrawal",
):
    payload = {
        "account_bank": str(bank_code),
        "account_number": str(account_number),
        "amount": float(amount),
        "currency": "NGN",
        "beneficiary_name": account_name,
        "reference": reference,
        "narration": narration,
    }

    response = requests.post(
        f"{FLW_BASE_URL}/transfers",
        headers=flutterwave_headers(),
        json=payload,
        timeout=30,
    )

    try:
        return response.json()
    except Exception:
        return {
            "status": "error",
            "message": "Invalid Flutterwave response.",
        }


# ==========================================
# VERIFY TRANSFER
# ==========================================

def verify_transfer(reference):
    response = requests.get(
        f"{FLW_BASE_URL}/transfers/{reference}",
        headers=flutterwave_headers(),
        timeout=30,
    )

    try:
        return response.json()
    except Exception:
        return {
            "status": "error",
            "message": "Invalid Flutterwave response.",
        }
