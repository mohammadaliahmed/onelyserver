from app.chat import bp
from app import moment, db
from flask import jsonify, g, request
from app.models import User, Message
from app.api.auth import token_auth
import datetime
from flask_login import current_user


@bp.before_request
def before_request():
    try:
        if "Authorization" in request.headers:
            token = request.headers.get("Authorization").split(" ")[1]
            u = User.check_token(token)
            if u is not None:
                u.last_seen = datetime.datetime.utcnow()
                db.session.commit()
    except:
        pass


@bp.route('/', methods=['GET'])
def index():
    return "ok"


@bp.route('/threads', methods=['GET'])
@token_auth.login_required
def get_threads():
    followed = g.current_user.followed
    followers = g.current_user.followers
    followed.union(followers)
    threads = []
    for user in followed.all():
        room = g.current_user.get_room(user.id)
        message = Message.query.filter_by(room=room).order_by(Message.sent_at.desc()).first()
        if message is not None:
            thread = {
                "user": user.to_dict(),
                "message": message.to_dict(),
                "count": Message.query.filter_by(room=room).count()
            }
            threads.append(thread)
        else:
            thread = {
                "user": user.to_dict(),
                "message": {
                    "id": 1,
                    "sender_id": 1,
                    "receiver_id": 2,
                    "data": "proba",
                    "sent_at": int(float(datetime.datetime(2020, 4, 18, 1, 45, 39).strftime('%s.%f'))*1000),
                    "read": True
                },
                "count": 1
            }
            threads.append(thread)
    threads.sort(key=thread_key, reverse=True)
    data = {
        "threads": threads
    }
    return jsonify(data)


def thread_key(t):
    return t["message"]["sent_at"]


@bp.route('/thread/<int:id>', methods=['GET'])
@token_auth.login_required
def get_thread(id):
    room = g.current_user.get_room(id)
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 100, type=int), 100)
    data = Message.to_collection_dict(Message.query.filter_by(room=room), page, per_page, 'chat.get_thread', id=id)
    return jsonify(data)


@bp.route('/thread/dummy', methods=['GET'])
@token_auth.login_required
def get_thread_dummy():
    items = []
    message1 = {
        "id": 1,
        "sender_id": 0,
        "receiver_id": 1,
        "data": "Odakle si Viktorija?",
        "sent_at": int(float(datetime.datetime(2020, 4, 18, 1, 45, 39).strftime('%s.%f'))*1000),
        "read": True
    }
    message2 = {
        "id": 1,
        "sender_id": 1,
        "receiver_id": 0,
        "data": "Dobro",
        "sent_at": int(float(datetime.datetime(2020, 4, 18, 1, 45, 39).strftime('%s.%f'))*1000),
        "read": True
    }
    message3 = {
        "id": 1,
        "sender_id": 0,
        "receiver_id": 1,
        "data": "Odakle si?",
        "sent_at": int(float(datetime.datetime(2020, 4, 18, 1, 45, 39).strftime('%s.%f'))*1000),
        "read": True
    }
    message4 = {
        "id": 1,
        "sender_id": 1,
        "receiver_id": 0,
        "data": "Iz Subotice",
        "sent_at": int(float(datetime.datetime(2020, 4, 18, 1, 45, 39).strftime('%s.%f'))*1000),
        "read": True
    }
    message5 = {
        "id": 1,
        "sender_id": 1,
        "receiver_id": 0,
        "data": "Ti?",
        "sent_at": int(float(datetime.datetime(2020, 4, 18, 1, 45, 39).strftime('%s.%f'))*1000),
        "read": True
    }
    message6 = {
        "id": 1,
        "sender_id": 0,
        "receiver_id": 1,
        "data": "Pancevo",
        "sent_at": int(float(datetime.datetime(2020, 4, 18, 1, 45, 39).strftime('%s.%f'))*1000),
        "read": True
    }
    message7 = {
        "id": 1,
        "sender_id": 1,
        "receiver_id": 0,
        "data": "Lepo",
        "sent_at": int(float(datetime.datetime(2020, 4, 18, 1, 45, 39).strftime('%s.%f'))*1000),
        "read": True
    }
    items.append(message1)
    items.append(message2)
    items.append(message3)
    items.append(message4)
    items.append(message5)
    items.append(message6)
    items.append(message7)
    return jsonify({"items": items})
