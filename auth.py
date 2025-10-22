import json
import os
import bcrypt
from google.oauth2 import id_token
from google.auth.transport import requests

# === File paths ===
BANNED_FILE = "banned.json"
USERS_FILE = "users.json"

# === Mod accounts ===
MOD_EMAILS = {"340234@apps.wilsonareasd.org"}

# === Ban logic ===
def load_banned():
    if not os.path.exists(BANNED_FILE):
        return set()
    with open(BANNED_FILE, "r") as f:
        return set(json.load(f))

def save_banned(banned_set):
    with open(BANNED_FILE, "w") as f:
        json.dump(list(banned_set), f)

def is_banned(email):
    return email in load_banned()

def ban_user(email):
    banned = load_banned()
    banned.add(email)
    save_banned(banned)

def unban_user(email):
    banned = load_banned()
    banned.discard(email)
    save_banned(banned)

# === Mod check ===
def is_mod(email):
    return email in MOD_EMAILS

# === Token verification ===
def verify_token(token):
    # Dev-mode override
    if token == "dev":
        return {
            "email": "340234@apps.wilsonareasd.org",
            "name": "Renee"
        }
    try:
        info = id_token.verify_oauth2_token(token, requests.Request())
        return {
            "email": info.get("email"),
            "name": info.get("name")
        }
    except Exception as e:
        print("Token verification failed:", e)
        return None

# === Optional: email/password login ===
def load_users():
    if not os.path.exists(USERS_FILE):
        return []
    with open(USERS_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)

def register_user(email, name, password):
    users = load_users()
    if any(u["email"] == email for u in users):
        return False
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    users.append({"email": email, "name": name, "password_hash": hashed})
    save_users(users)
    return True

def authenticate_user(email, password):
    users = load_users()
    for user in users:
        if user["email"] == email and bcrypt.checkpw(password.encode(), user["password_hash"].encode()):
            return {"email": user["email"], "name": user["name"]}
    return None

# === Runner block for testing ===
if __name__ == "__main__":
    print("🔧 Dev Auth Test")
    user = verify_token("dev")
    print("User:", user)
    print("Is mod:", is_mod(user["email"]))
    print("Is banned:", is_banned(user["email"]))
