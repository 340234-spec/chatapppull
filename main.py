from flask import Flask, render_template
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

message_history = []

@app.route('/')
def index():
    return render_template('chat.html')

@socketio.on('connect')
def handle_connect():
    for msg in message_history:
        emit('message', msg)

@socketio.on('message')
def handle_message(data):
    username = data.get('username', 'Anonymous')
    text = data.get('text', '')
    full_msg = f"{username}: {text}"
    message_history.append(full_msg)
    emit('message', full_msg, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=8080)
