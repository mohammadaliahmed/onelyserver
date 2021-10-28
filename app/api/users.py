from app.api import bp
from app import db, fcm, s3
from flask import jsonify, request, url_for
from app.models import User, FCMKey, LiveRequests
from app.api.errors import bad_request
from flask import g, abort, current_app
from app.api.auth import token_auth
from app.email import send_verification_email, send_password_reset_email
import random
import string
import os
import datetime
from flask_login import current_user

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])


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


@bp.route('/users/<int:id>', methods=['GET'])
@token_auth.login_required
def get_user(id):
    return jsonify(User.query.get_or_404(id).to_dict())


@bp.route('/users/verify', methods=['POST'])
def code_verification():
    data = request.get_json() or {}
    user = User.query.filter_by(username=data['username']).first()
    code = user.verification_code
    if code == data['code']:
        user.verify_account()
        db.session.commit()
    return jsonify({'result': code == data['code']})


@bp.route('/users/go_live_request/<int:id>', methods=['GET'])
def go_live_request(id):
    goLiveRequest = LiveRequests.query.filter_by(user_id=id).first()
    if goLiveRequest is None:
        goLiveRequest = LiveRequests(user_id=id, live_request=0)
        db.session.add(goLiveRequest)
        db.session.commit()
        return jsonify("done")

    else:
        return jsonify("done else")


@bp.route('/users/password_reset_request', methods=['POST'])
def password_reset_request():
    data = request.get_json() or {}
    user = User.query.filter_by(username=data['username']).first()
    user.verification_code = random.randint(1000, 10000)
    db.session.commit()
    send_verification_email(user)
    return jsonify({'status': 'ok'})


@bp.route('/users/forgot_password', methods=['POST'])
def password_reset():
    data = request.get_json() or {}
    user = User.query.filter_by(username=data['username']).first()
    code = user.verification_code
    if code == data['code']:
        user.set_password(data['password'])
        db.session.commit()
    return jsonify({'result': code == data['code']})


@bp.route('/users/change_password', methods=['POST'])
@token_auth.login_required
def password_change():
    data = request.get_json() or {}
    if g.current_user.check_password(data['old_password']):
        g.current_user.set_password(data['new_password'])
        db.session.commit()
        return jsonify({'result': True})
    return jsonify({'result': False})


@bp.route('/users', methods=['GET'])
@token_auth.login_required
def get_users():
    data = g.current_user.to_dict(include_email=True)
    return jsonify(data)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def random_string(string_length=20):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(string_length))


@bp.route('/users/profile_photo', methods=['POST'])
@token_auth.login_required
def upload_profile_photo():
    file = request.files['photo']
    filename = random_string() + '.' + file.filename.rsplit('.', 1)[1].lower()
    file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
    response = s3.upload_file('app/upload/' + filename, current_app.config['S3_BUCKET'], filename)
    g.current_user.avatar = filename
    db.session.commit()
    return jsonify({'uploaded': True})


@bp.route('/users/main_photo/<int:num>', methods=['POST'])
@token_auth.login_required
def upload_main_photo(num):
    file = request.files['photo']
    filename = random_string() + '.' + file.filename.rsplit('.', 1)[1].lower()
    file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
    response = s3.upload_file('app/upload/' + filename, current_app.config['S3_BUCKET'], filename)
    if num is 1:
        g.current_user.photo1 = filename
    elif num is 2:
        g.current_user.photo2 = filename
    elif num is 3:
        g.current_user.photo3 = filename
    elif num is 4:
        g.current_user.photo4 = filename
    elif num is 5:
        g.current_user.photo5 = filename
    elif num is 6:
        g.current_user.photo6 = filename
    db.session.commit()
    return jsonify({'uploaded': True})


def upload_file_to_s3(file, bucket_name, filename, acl="public-read"):
    try:
        s3.upload_fileobj(
            file,
            bucket_name,
            filename,
            ExtraArgs={
                "ACL": acl,
                "ContentType": file.content_type
            }
        )
    except Exception as e:
        print("Something Happened: ", e)
        return e

    return "{}{}".format(current_app.config["S3_LOCATION"], file.filename)


@bp.route('/users', methods=['POST'])
def create_user():
    data = request.get_json() or {}

    if 'username' not in data or 'email' not in data or 'password' not in data or 'name' not in data:
        return bad_request('must include username, email, password and name fields')
    if User.query.filter_by(username=data['username']).first():
        return bad_request('please use a different username')
    if User.query.filter_by(email=data['email']).first():
        return bad_request('please use a different email address')
    user = User()
    user.from_dict(data, new_user=True)
    user.verification_code = random.randint(1000, 10000)
    # send_verification_email(user)
    user.can_go_live = 0
    user.tokens = 50
    db.session.add(user)
    db.session.commit()
    response = jsonify(user.to_dict())
    response.status_code = 201
    response.headers['Location'] = url_for('api.get_user', id=user.id)
    return response


@bp.route('/sociallogin', methods=['POST'])
def sociallogin():
    data = request.get_json() or {}
    try:
        user = User.query.filter_by(social_id=data['social_id']).first()

        return jsonify(user.to_dict())
    except:
        return "unauthorized"


@bp.route('/users', methods=['PUT'])
@token_auth.login_required
def update_user():
    user = g.current_user
    data = request.get_json() or {}
    if 'username' in data and data['username'] != user.username and \
            User.query.filter_by(username=data['username']).first():
        return bad_request('please use a different username')
    if 'email' in data and data['email'] != user.email and \
            User.query.filter_by(email=data['email']).first():
        return bad_request('please use a different email address')
    user.from_dict(data, new_user=False)
    db.session.commit()
    return jsonify(user.to_dict())


@bp.route('/users/<string:username>', methods=['GET'])
@token_auth.login_required
def get_user_by_username(username):
    user = User.query.filter_by(username=username).first()
    return jsonify(user.to_dict())


@bp.route('/users/search/<string:username>', methods=['GET'])
@token_auth.login_required
def search_user(username):
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    data = User.to_collection_dict(User.query.filter(User.username.ilike(username + '%')), page, per_page,
                                   'api.get_users')
    return jsonify(data)


@bp.route('/fcmkey', methods=['POST'])
@token_auth.login_required
def add_fcmkey():
    data = request.get_json() or {}
    if 'fcmkey' not in data:
        return bad_request('token not in data')
    if FCMKey.query.filter(FCMKey.key == data['fcmkey']).count() > 0:
        return jsonify({'response': 'already in database'})
    fcmkey = FCMKey(key=data['fcmkey'], receiving_user=g.current_user)
    db.session.add(fcmkey)
    db.session.commit()
    return jsonify({'response': 'okay'})


@bp.route('/updateTokensInDB', methods=['POST'])
def updateTokensInDB():
    data = request.get_json() or {}
    user = User.query.filter_by(id=data['id']).first()
    user.tokens = data["tokens"]
    db.session.commit()

    return jsonify({'response': 'okay'})
