from datetime import datetime
from flask import current_app, url_for
from app import db, login, moment
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from hashlib import md5
from time import time
import jwt
import os
from datetime import datetime, timedelta
import base64


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class PaginatedAPIMixin(object):
    @staticmethod
    def to_collection_dict(query, page, per_page, endpoint, **kwargs):
        resources = query.paginate(page, per_page, False)
        data = {
            'items': [item.to_dict() for item in resources.items],
            '_meta': {
                'page': page,
                'per_page': per_page,
                'total_pages': resources.pages,
                'total_items': resources.total
            },
            '_links': {
                'self': url_for(endpoint, page=page, per_page=per_page,
                                **kwargs),
                'next': url_for(endpoint, page=page + 1, per_page=per_page,
                                **kwargs) if resources.has_next else None,
                'prev': url_for(endpoint, page=page - 1, per_page=per_page,
                                **kwargs) if resources.has_prev else None
            }
        }
        return data


followers = db.Table('followers',
                     db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
                     db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
                     )


class User(PaginatedAPIMixin, UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    name = db.Column(db.String(128))
    login_type = db.Column(db.String(128))
    social_id = db.Column(db.String(200))
    email = db.Column(db.String(120), index=True, unique=True)
    country = db.Column(db.String(128))
    phone_number = db.Column(db.String(128))
    birthday = db.Column(db.String(128))
    gender = db.Column(db.String(128))
    looking_for = db.Column(db.String(16))
    genres = db.Column(db.Text)
    artists = db.Column(db.Text)
    questions = db.Column(db.Text)
    anthem = db.Column(db.String(128))
    bio = db.Column(db.Text)
    location = db.Column(db.Text)
    discover_location = db.Column(db.Text)
    height = db.Column(db.String(128))
    hometown = db.Column(db.String(256))
    ethnicity = db.Column(db.String(128))
    job = db.Column(db.String(128))
    education = db.Column(db.String(128))
    religion = db.Column(db.String(128))
    company = db.Column(db.String(128))
    instagram = db.Column(db.String(128))
    password_hash = db.Column(db.String(128))
    avatar = db.Column(db.String(128))
    photo1 = db.Column(db.String(128))
    photo2 = db.Column(db.String(128))
    photo3 = db.Column(db.String(128))
    photo4 = db.Column(db.String(128))
    photo5 = db.Column(db.String(128))
    photo6 = db.Column(db.String(128))
    favoriteSongs = db.Column(db.Text)
    favoriteAlbums = db.Column(db.Text)
    favoritePlaylists = db.Column(db.Text)
    favoriteArtists = db.Column(db.Text)
    favoriteGenres = db.Column(db.Text)
    verification_code = db.Column(db.Integer)
    verified = db.Column(db.Boolean, default=False)
    fcmkeys = db.relationship('FCMKey', backref='receiving_user', lazy='dynamic')
    songs = db.relationship('Song', backref='listened_by_user', lazy='dynamic')
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    creation_date = db.Column(db.DateTime, default=datetime.utcnow)
    token = db.Column(db.String(32), index=True, unique=True)
    token_expiration = db.Column(db.DateTime)
    tokens = db.Column(db.Integer())
    can_go_live = db.Column(db.Integer())
    followed = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        return self.followed.filter(
            followers.c.followed_id == user.id).count() > 0

    def following_users(self):
        return self.followed.all()

    def followers_users(self):
        return self.followers.all()

    def verify_account(self):
        self.verified = True

    def get_room(self, id):
        return str(min(self.id, id)) + "-" + str(max(self.id, id))

    def to_dict(self, include_email=False):
        data = {
            'id': self.id,
            'username': self.username,
            'name': self.name,
            'social_id': self.social_id,
            'login_type': self.login_type,
            'country': self.country,
            'phone_number': self.phone_number,
            'birthday': self.birthday,
            'gender': self.gender,
            'looking_for': self.looking_for,
            'genres': self.genres,
            'artists': self.artists,
            'questions': self.questions,
            'anthem': self.anthem,
            'bio': self.bio,
            'discover_location': self.discover_location,
            'location': self.location,
            'height': self.height,
            'hometown': self.hometown,
            'ethnicity': self.ethnicity,
            'job': self.job,
            'company': self.company,
            'education': self.education,
            'religion': self.religion,
            'instagram': self.instagram,
            'avatar': self.avatar,
            'photo1': self.photo1,
            'photo2': self.photo2,
            'photo3': self.photo3,
            'photo4': self.photo4,
            'photo5': self.photo5,
            'photo6': self.photo6,
            'favoriteSongs': self.favoriteSongs,
            'favoriteAlbums': self.favoriteAlbums,
            'favoritePlaylists': self.favoritePlaylists,
            'favoriteArtists': self.favoriteArtists,
            'favoriteGenres': self.favoriteGenres,
            'verified': self.verified,
            'following_count': self.followed.count(),
            'followers_count': self.followers.count(),
            '_links': {
                'self': url_for('api.get_user', id=self.id)
            },
            'can_go_live': self.can_go_live,
            'tokens': self.tokens,
        }
        if include_email:
            data['email'] = self.email
        return data

    def from_dict(self, data, new_user=False):
        for field in ['username', 'email', 'name', 'country', 'phone_number', 'birthday', 'genres', 'artists',
                      'questions', 'anthem', 'bio', 'discover_location', 'location', 'height', 'hometown', 'ethnicity',
                      'job', 'company', 'education', 'religion', 'instagram', 'gender', 'looking_for',
                      'photo1', 'photo2', 'photo3', 'photo4', 'photo5', 'photo6',
                      'favoriteSongs', 'favoriteAlbums', 'favoritePlaylists', 'favoriteArtists',
                      'favoriteGenres', 'social_id', 'login_type']:
            if field in data:
                setattr(self, field, data[field])
        if new_user and 'password' in data:
            self.set_password(data['password'])

    def get_token(self, expires_in=3600):
        now = datetime.utcnow()
        if self.token and self.token_expiration > now + timedelta(seconds=60):
            return self.token
        self.token = base64.b64encode(os.urandom(24)).decode('utf-8')
        self.token_expiration = now + timedelta(seconds=expires_in)
        db.session.add(self)
        return self.token

    def revoke_token(self):
        self.token_expiration = datetime.utcnow() - timedelta(seconds=1)

    @staticmethod
    def check_token(token):
        user = User.query.filter_by(token=token).first()
        if user is None or user.token_expiration < datetime.utcnow():
            return None
        return user


class Countries(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))

    def __repr__(self):
        return '<Countries {}>'.format(self.name)

    def to_dict(self):
        data = {
            'id': self.id,
            'name': self.name
        }
        return data


class Song(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    song_url = db.Column(db.String(1024))
    song_title = db.Column(db.String(1024))
    song_album_artist = db.Column(db.String(1024))
    song_artist = db.Column(db.String(1024))
    song_genre = db.Column(db.String(1024))
    song_album = db.Column(db.String(1024))
    listening_time = db.Column(db.DateTime, default=datetime.utcnow)
    listening_location = db.Column(db.String(1024))
    '''albumName = db.Column(db.String(256))
    artistName = db.Column(db.String(256))
    composerName = db.Column(db.String(256))
    contentRating = db.Column(db.String(256))
    discNumber = db.Column(db.Integer)
    durationInMillis = db.Column(db.Integer)
    genreNames = db.Column(db.String(512))
    isrc = db.Column(db.String(256))
    movementCount = db.Column(db.Integer)
    movementName = db.Column(db.String(256))
    movementNumber = db.Column(db.Integer)
    name = db.Column(db.String(256))
    releaseDate = db.Column(db.String(128))
    trackNumber = db.Column(db.Integer)
    url = db.Column(db.String(512))
    workName = db.Column(db.String(256))'''

    def __repr__(self):
        return '<Song {}>'.format(self.song_title)

    def to_dict(self):
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'song_url': self.song_url,
            'song_title': self.song_title,
            'song_album_artist': self.song_album_artist,
            'song_artist': self.song_artist,
            'song_genre': self.song_genre,
            'song_album': self.song_album,
            'listening_time': self.listening_time,
            'listening_location': self.listening_location
            # 'albumName': self.albumName,
            # 'artistName': self.artistName,
            # 'composerName': self.composerName,
            # 'contentRating': self.contentRating,
            # 'discNumber': self.discNumber,
            # 'durationInMillis': self.durationInMillis,
            # 'genreNames': self.genreNames,
            # 'isrc': self.isrc,
            # 'movementCount': self.movementCount,
            # 'movementName': self.movementName,
            # 'movementNumber': self.movementNumber,
            # 'name': self.name,
            # 'releaseDate': self.releaseDate,
            # 'trackNumber': self.trackNumber,
            # 'url': self.url,
            # 'workName': self.workName
        }
        return data

    def from_dict(self, data):
        for field in ['song_url', 'song_title', 'song_album_artist', 'song_artist', 'song_genre', 'song_album',
                      'listening_location',
                      'albumName', 'artistName', 'composerName', 'contentRating', 'discNumber', 'durationInMillis',
                      'genreNames', 'isrc', 'movementCount', 'movementName', 'movementNumber', 'name', 'releaseDate',
                      'trackNumber', 'url', 'workName']:
            if field in data:
                setattr(self, field, data[field])


class Message(PaginatedAPIMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    room = db.Column(db.String(128))
    sender_id = db.Column(db.Integer)
    receiver_id = db.Column(db.Integer)
    data = db.Column(db.String(1024))
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)
    read = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return '<Message {} - {}: {}>'.format(self.sender_id, self.receiver_id, self.data)

    def to_dict(self):
        data = {
            "id": self.id,
            "room": self.room,
            "sender_id": self.sender_id,
            "receiver_id": self.receiver_id,
            "data": self.data,
            "sent_at": 1631082607000,
            "read": self.read
        }
        return data


class FCMKey(db.Model):
    key = db.Column(db.String(256), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class LiveRequests(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id=db.Column(db.Integer)
    live_request=db.Column(db.Integer)
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)


