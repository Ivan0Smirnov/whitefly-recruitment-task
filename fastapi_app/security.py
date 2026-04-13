import os

import requests

from db import run_query


def verify_recaptcha(token: str) -> bool:
    secret_key = os.getenv("RECAPTCHA_SECRET")
    response = requests.post(
        "https://www.google.com/recaptcha/api/siteverify",
        data={
            "secret": secret_key,
            "response": token
        }
    )
    result = response.json()
    print("reCAPTCHA result:", result)
    return result.get('success', False)


def check_fingerprint(fingerprint: str) -> bool:
    """Returns True if fingerprint is allowed, False if blocked."""
    count = run_query(
        "SELECT COUNT(*) FROM fingerprint_attempts WHERE fingerprint=%s",
        (fingerprint,),
        fetch=True
    )
    if count and count[0][0] >= 5:
        return False
    run_query(
        "INSERT INTO fingerprint_attempts (fingerprint) VALUES (%s)",
        (fingerprint,)
    )
    return True
