from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode='threading')

message_history = []
banned_users = set()

@app.route('/')
def index():
    return render_template('chat.html')

@socketio.on('join')
def handle_join(data):
    email = data.get('email')
    if email in banned_users:
        return
    emit('history', message_history, to=request.sid)

@socketio.on('message')
def handle_message(data):
    username = data.get('username', 'Anonymous')
    text = data.get('text', '')
    full_msg = f"{username}: {text}"
    message_history.append(full_msg)
    emit('message', full_msg, broadcast=True)

@socketio.on('ban')
def handle_ban(data):
    email = data.get('email')
    banned_users.add(email)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=8080, allow_unsafe_werkzeug=True)
