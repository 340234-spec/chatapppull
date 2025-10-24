from flask import Flask, request, jsonify, render_template
from flask_socketio import SocketIO, emit, join_room
from auth import verify_token
import os

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

chat_history = []
user_sockets = {}  # Maps email or name to socket ID
banned_emails = set()
dev_users = set()
dev_mode_level = 0

# ✅ Multiple mod emails
MOD_EMAILS = {
    "340234@apps.wilsonareasd.org",
    "renee@example.com",
    "admin@school.edu"
}

# --- Routes ---
@app.route("/")
def index():
    return render_template("chat.html")

@app.route("/dm")
def dm_page():
    return render_template("dm.html")

@app.route("/dev-login")
def dev_login():
    return jsonify({
        "success": True,
        "token": "dev"
    })

@app.route("/verify", methods=["POST"])
def verify():
    data = request.get_json()
    token = data.get("token")
    user = verify_token(token)

    if not user:
        return jsonify({"success": False, "error": "Invalid token"}), 401

    if is_banned(user["email"]):
        return jsonify({"success": False, "error": "You are banned"}), 403

    return jsonify({
        "success": True,
        "email": user["email"],
        "name": user["name"],
        "is_mod": is_mod(user["email"]),
        "banned": is_banned(user["email"])
    })

# --- Socket.IO Events ---
@socketio.on("join")
def handle_join(data):
    token = data.get("token")
    user = verify_token(token)
    if not user:
        return

    email = user["email"]
    name = user["name"]
    sid = request.sid

    user_sockets[email] = sid
    user_sockets[name] = sid

    join_room("global")
    emit("history", chat_history, to=sid)

    if token == "dev":
        dev_users.add(sid)
        update_dev_mode_level()

@socketio.on("disconnect")
def handle_disconnect():
    sid = request.sid
    if sid in dev_users:
        dev_users.remove(sid)
        update_dev_mode_level()

def update_dev_mode_level():
    global dev_mode_level
    dev_mode_level = len(dev_users)
    socketio.emit("dev_level", {"level": dev_mode_level})
    print(f"Dev mode level updated: {dev_mode_level}")

@socketio.on("message")
def handle_message(data):
    token = data.get("token")
    text = data.get("text", "").strip()
    user = verify_token(token)

    if not user or is_banned(user["email"]) or not text:
        return

    msg = f"{user['name']}: {text}"
    chat_history.append(msg)
    emit("message", msg, to="global")

@socketio.on("private")
def handle_private(data):
    to = data.get("to")
    text = data.get("text")
    from_user = data.get("from")
    token = data.get("token")

    user = verify_token(token)
    if not user or is_banned(user["email"]) or not text:
        return

    target_sid = user_sockets.get(to)
    print(f"Private message from {from_user} to {to}: {text}")
    print(f"Target SID: {target_sid}")

    if target_sid:
        msg = f"[Private] {from_user}: {text}"
        emit("message", msg, to=target_sid)
        emit("message", f"[Private to {to}] {text}", to=request.sid)
    else:
        emit("message", f"User '{to}' not found", to=request.sid)

@socketio.on("ban")
def handle_ban(data):
    token = data.get("token")
    email = data.get("email")
    user = verify_token(token)

    if not user or not is_mod(user["email"]) or not email:
        return

    banned_emails.add(email)
    emit("message", f"{email} has been banned by {user['name']}", to="global")

@socketio.on("unban")
def handle_unban(data):
    token = data.get("token")
    email = data.get("email")
    user = verify_token(token)

    if not user or not is_mod(user["email"]) or not email:
        return

    if email in banned_emails:
        banned_emails.remove(email)
        emit("message", f"{email} has been unbanned by {user['name']}", to="global")

# --- Helpers ---
def is_banned(email):
    return email in banned_emails

def is_mod(email):
    return email in MOD_EMAILS

# --- Run Server ---
if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=8080, allow_unsafe_werkzeug=True)
