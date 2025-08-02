from flask_socketio import SocketIO, emit, join_room, leave_room
from flask import request
from flask_login import current_user
from app import socketio, db
from app.models import Message
from datetime import datetime

# Track online users per room and user-socket mapping
online_users_per_room = {}
user_sid_map = {}

@socketio.on('connect')
def handle_connect():
    print("[SocketIO] A user connected.")

@socketio.on('disconnect')
def handle_disconnect():
    username = request.args.get('username')
    print(f"[SocketIO] {username} disconnected.")

    for room, users in online_users_per_room.items():
        if username in users:
            users.remove(username)
            emit('user_list', list(users), room=room)
            emit('user_typing', {'username': username, 'typing': False}, room=room)

    user_sid_map.pop(username, None)

@socketio.on('join_room')
def handle_join(data):
    username = data.get('username')
    room = data.get('room')

    join_room(room)
    user_sid_map[username] = request.sid

    if room not in online_users_per_room:
        online_users_per_room[room] = set()

    online_users_per_room[room].add(username)
    print(f"[SocketIO] {username} joined room: {room}")

    emit('user_list', list(online_users_per_room[room]), room=room)

@socketio.on('send_message')
def handle_send_message(data):
    username = data.get('username')
    message_text = data.get('message')
    room = data.get('room')
    timestamp = datetime.utcnow()

    new_msg = Message(username=username, content=message_text, room=room, timestamp=timestamp)
    db.session.add(new_msg)
    db.session.commit()

    emit('receive_message', {
        'username': username,
        'message': message_text,
        'timestamp': timestamp.strftime('%H:%M:%S')  # includes seconds
    }, room=room)

@socketio.on('send_file')
def handle_send_file(data):
    username = data.get('username')
    room = data.get('room')
    file_data = data.get('file')
    filename = data.get('filename')
    timestamp = datetime.utcnow()

    file_link = f"<a href='{file_data}' download='{filename}' target='_blank'>📎 {filename}</a>"
    new_msg = Message(username=username, content=file_link, room=room, timestamp=timestamp)
    db.session.add(new_msg)
    db.session.commit()

    emit('receive_message', {
        'username': username,
        'message': file_link,
        'timestamp': timestamp.strftime('%H:%M:%S')  # includes seconds
    }, room=room)

@socketio.on('typing')
def handle_typing(data):
    username = data.get('username')
    room = data.get('room')
    typing = data.get('typing', False)

    emit('user_typing', {
        'username': username,
        'typing': typing
    }, room=room, include_self=False)

@socketio.on('private_message')
def handle_private_message(data):
    sender = data.get('sender')
    recipient = data.get('recipient')
    message_text = data.get('message')
    timestamp = datetime.utcnow()

    recipient_sid = user_sid_map.get(recipient)

    new_msg = Message(
        username=sender,
        content=message_text,
        recipient=recipient,
        is_private=True,
        timestamp=timestamp
    )
    db.session.add(new_msg)
    db.session.commit()

    message_payload = {
        'sender': sender,
        'message': message_text,
        'timestamp': timestamp.strftime('%H:%M:%S')  # include seconds
    }

    if recipient_sid:
        emit('receive_private_message', message_payload, room=recipient_sid)

    emit('receive_private_message', message_payload, room=request.sid)

    if not recipient_sid:
        print(f"[SocketIO] User '{recipient}' is offline. Could not send private message.")

# ✅ Handle Seen Message Acknowledgement
@socketio.on('message_seen')
def handle_message_seen(data):
    sender = data.get('sender')
    timestamp = data.get('timestamp')
    room = data.get('room')

    emit('message_seen_ack', {
        'sender': sender,
        'timestamp': timestamp
    }, room=room)
    print(f"[SocketIO] Message from {sender} seen at {timestamp} in room {room}.") 
    