from app import socketio, db, fcm
from flask import g
from app.models import User, Message, FCMKey
from flask_socketio import emit, disconnect, join_room, leave_room


@socketio.on('join')
def connected(data):
    if not data.get("token"):
        return
    user = User.query.filter_by(token=data.get("token")).first()
    user_id = data.get("user_id")
    if User.query.get(user_id) is None:
        emit("error", "User with id %r does not exist." % user_id)
        disconnect()
    room = user.get_room(user_id)
    join_room(room)


@socketio.on('leave')
def disconnected(data):
    if not data.get("token"):
        return
    user = User.query.filter_by(token=data.get("token")).first()
    room = user.get_room(data.get('user_id'))

    stopped_typing_handler(user.username, room)
    leave_room(room)


@socketio.on('typing')
def started_typing(data):
    if not data.get("token"):
        return
    user = User.query.filter_by(token=data.get("token")).first()
    room = user.get_room(data.get('user_id'))

    emit("typing", user.username, room=room, include_self=False)


@socketio.on('stop typing')
def stopped_typing(data):
    if not data.get("token"):
        return
    user = User.query.filter_by(token=data.get("token")).first()
    room = user.get_room(data.get('user_id'))
    stopped_typing_handler(data.get("username"), room)


def stopped_typing_handler(username, room_name):
    emit("stop typing", username, room=room_name, include_self=False)


@socketio.on('send message')
def handle_sent_message(data):
    if not data.get("token"):
        return
    user = User.query.filter_by(token=data.get("token")).first()
    if not data.get('message'):
        return

    room = user.get_room(data.get('user_id'))

    message = Message(room=room, sender_id=user.id, receiver_id=data.get('user_id'), data=data.get('message'))
    db.session.add(message)
    db.session.commit()
    notify(data.get("user_id"), user.username + " sent you a message", data.get('message'))
    emit("received message", message.to_dict(), room=room)


def notify(u, title, message):
    keys = []
    fs = FCMKey.query.filter_by(user_id=int(u))
    for f in fs:
        keys.append(f.key)
    if keys is not []:
        try:
            result = fcm.service.notify_multiple_devices(registration_ids=keys, message_title=title,
                                                         message_body=message)
        except:
            pass
