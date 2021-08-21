from app.api import bp
from app import db, fcm
from flask import jsonify, request
from app.models import Song, User, Message, FCMKey
from flask import g
from app.api.auth import token_auth
from sqlalchemy import and_
import datetime
import math


@bp.route('/history', methods=['POST'])
@token_auth.login_required
def add_to_history():
    data = request.get_json() or {}
    song = Song(listened_by_user=g.current_user)
    song.from_dict(data)
    db.session.add(song)
    db.session.commit()
    return jsonify(song.to_dict())


@bp.route('/match', methods=['POST'])
@token_auth.login_required
def match():
    data = request.get_json() or {}
    user = User.query.get_or_404(data['id'])
    if g.current_user.is_following(user):
        return jsonify({'following': True})
    g.current_user.follow(user)

    room = g.current_user.get_room(user.id)
    message = Message(room=room, sender_id=g.current_user.id, receiver_id=user.id, data=data['message'])
    db.session.add(message)
    db.session.commit()
    notify(data['id'], g.current_user.username + " wants to send you a message", data['message'])
    return jsonify(user.to_dict())


@bp.route('/discover', methods=['POST'])
@token_auth.login_required
def discover():
    data = request.get_json() or {}
    user_gender = g.current_user.gender[0].lower()
    user_looking_for = g.current_user.looking_for
    try:
        user_location = (float(data['listening_location'].split(',')[0]), float(data['listening_location'].split(',')[1]))
    except Exception as e:
        user_location = (0.0, 0.0)
    time = datetime.datetime.utcnow() - datetime.timedelta(minutes=5)
    q = Song.query.filter(Song.listening_time > time, Song.user_id != g.current_user.id)
    result = discover_hierarchy(q, data)
    if result is None:
        time = datetime.datetime.utcnow() - datetime.timedelta(minutes=15)
        q = Song.query.filter(Song.listening_time > time, Song.user_id != g.current_user.id)
        result = discover_hierarchy(q, data)
        if result is None:
            time = datetime.datetime.utcnow() - datetime.timedelta(hours=24)
            q = Song.query.filter(Song.listening_time > time, Song.user_id != g.current_user.id)
            result = discover_hierarchy(q, data)
            if result is None:
                return jsonify({"items": []})
    songs = result.all()
    users = []
    uids = []
    for s in songs:
        u = User.query.get(s.user_id).to_dict()
        if g.current_user.is_following(User.query.get(s.user_id)):
            continue
        if u['gender'] and u['looking_for']:
            u_gender = u['gender'][0].lower()
            if 'f' in user_looking_for:
                user_looking_for += 'w'
            if 'w' in user_looking_for:
                user_looking_for += 'f'
            target_looking_for = u['looking_for']
            if 'f' in target_looking_for:
                target_looking_for += 'w'
            if 'w' in target_looking_for:
                target_looking_for += 'f'
            if u_gender in user_looking_for and user_gender in target_looking_for:
                u['distance'] = None
                try:
                    song_location = (float(s.listening_location.split(',')[0]), float(s.listening_location.split(',')[1]))
                    u['distance'] = haversine(user_location, song_location)
                except Exception as e:
                    pass
                if u['id'] is not g.current_user.id:
                    if u['id'] not in uids:
                        users.append(u)
                        uids.append(u['id'])

    users.sort(key=user_distance_key)
    return jsonify({"items": users})


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


def discover_hierarchy(q, data):
    query = q.filter(Song.song_title == data['song_title'])
    if query.count() > 0:
        return query
    query = q.filter(Song.song_artist == data['song_artist'])
    if query.count() > 0:
        return query
    query = q.filter(Song.song_album_artist == data['song_album_artist'])
    if query.count() > 0:
        return query
    query = q.filter(Song.song_genre == data['song_genre'])
    if query.count() > 0:
        return query
    return None


def haversine(coord1, coord2):
    R = 6372800  # Earth radius in meters
    lat1, lon1 = coord1
    lat2, lon2 = coord2

    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = math.sin(dphi / 2) ** 2 + \
        math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2

    if coord1 == (0.0, 0.0) or coord2 == (0.0, 0.0):
        return 0.0

    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def user_distance_key(u):
    if u['distance'] is None:
        return float("inf")
    return u['distance']
