from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
from auth import (
    verify_token,
    is_mod,
    is_banned,
    ban_user,
    unban_user
)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode='threading')

message_history = []

# === Routes ===

@app.route('/')
def index():
    return render_template('chat.html')

@app.route('/verify', methods=['POST'])
def verify():
    data = request.get_json()
    if not data or "token" not in data:
        return jsonify({"success": False, "error": "No token provided"}), 400

    token = data["token"]
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

@app.route('/dev-login', methods=['GET', 'POST'])
def dev_login():
    # Dev login returns a usable token and user info
    return jsonify({
        "success": True,
        "token": "dev",
        "email": "im watching",
        "name": "DEV",
        "is_mod": True,
        "banned": True,
    })

@app.route('/crash')
def crash():
    raise Exception("Intentional crash for testing")

# === Socket.IO Events ===

@socketio.on('join')
def handle_join(data):
    token = data.get("token")
    user = verify_token(token)
    if not user or is_banned(user["email"]):
        return
    emit('history', message_history, to=request.sid)

@socketio.on('message')
def handle_message(data):
    token = data.get("token")
    user = verify_token(token)
    if not user or is_banned(user["email"]):
        return

    username = user["name"]
    text = data.get("text", "").strip()
    if not text:
        return

    full_msg = f"{username}: {text}"
    message_history.append(full_msg)

    print("Broadcasting message:", full_msg)
    emit('message', full_msg, broadcast=True)

@socketio.on('ban')
def handle_ban(data):
    token = data.get('token')
    user = verify_token(token)
    if not user or not is_mod(user["email"]):
        return
    email_to_ban = data.get('email')
    if email_to_ban:
        ban_user(email_to_ban)
        print(f"User banned: {email_to_ban}")

@socketio.on('unban')
def handle_unban(data):
    token = data.get('token')
    user = verify_token(token)
    if not user or not is_mod(user["email"]):
        return
    email_to_unban = data.get('email')
    if email_to_unban:
        unban_user(email_to_unban)
        print(f"User unbanned: {email_to_unban}")

# === Server Runner ===

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=8080, allow_unsafe_werkzeug=True)
