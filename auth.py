import requests

MOD_EMAIL = "340234@apps.wilsonareasd.org"
BANNED_USERS = set()

def verify_token(token):
    """
    Verify Google ID token server-side using Google's tokeninfo endpoint.
    Returns user dict: {"email": ..., "name": ...} or None if invalid.
    """
    url = f"https://oauth2.googleapis.com/tokeninfo?id_token={token}"
    resp = requests.get(url)
    if resp.status_code != 200:
        return None
    data = resp.json()
    return {"email": data.get("email"), "name": data.get("name")}

def is_mod(email):
    return email == MOD_EMAIL

def is_banned(email):
    return email in BANNED_USERS
