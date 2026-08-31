import secrets
import requests

from flask import session

from config import (
    GOOGLE_CLIENT_ID,
    GOOGLE_CLIENT_SECRET,
    GOOGLE_REDIRECT_URI,
)


GOOGLE_AUTH_URL = (
    "https://accounts.google.com/o/oauth2/v2/auth"
)

GOOGLE_TOKEN_URL = (
    "https://oauth2.googleapis.com/token"
)

GOOGLE_USERINFO_URL = (
    "https://www.googleapis.com/oauth2/v3/userinfo"
)


def get_google_login_url():

    state = secrets.token_urlsafe(32)

    session["oauth_state"] = state

    params = {
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
        "state": state,
        "access_type": "offline",
        "prompt": "select_account",
    }

    query = "&".join(
        f"{k}={v}"
        for k, v in params.items()
    )

    return f"{GOOGLE_AUTH_URL}?{query}"


def exchange_code_for_token(code):

    response = requests.post(
        GOOGLE_TOKEN_URL,
        data={
            "code": code,
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "redirect_uri": GOOGLE_REDIRECT_URI,
            "grant_type": "authorization_code",
        },
    )

    print("GOOGLE TOKEN STATUS:", response.status_code)
    print("GOOGLE TOKEN BODY:", response.text)

    return response.json()


def get_google_user(access_token):

    response = requests.get(
        GOOGLE_USERINFO_URL,
        headers={
            "Authorization":
            f"Bearer {access_token}"
        },
    )

    return response.json()
