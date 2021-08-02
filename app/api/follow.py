from app.api import bp
from app.api.auth import token_auth
from flask import request, jsonify, g
from app.models import User
from app import db


@bp.route('/users/<int:id>/followers', methods=['GET'])
@token_auth.login_required
def get_followers(id):
    user = User.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    data = User.to_collection_dict(user.followers, page, per_page, 'api.get_followers', id=id)
    return jsonify(data)


@bp.route('/users/<id>/following', methods=['GET'])
@token_auth.login_required
def get_following(id):
    user = User.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    data = User.to_collection_dict(user.followed, page, per_page, 'api.get_following', id=id)
    return jsonify(data)


@bp.route('/feed', methods=['GET'])
@token_auth.login_required
def get_igs():
    followings = g.current_user.followed.all()
    users = []
    for f in followings:
        users.append(f.instagram)
    return jsonify(users)


@bp.route('/users/<int:id>/following/<int:target_id>', methods=['GET'])
@token_auth.login_required
def is_following(id, target_id):
    user = User.query.get_or_404(id)
    target_user = User.query.get_or_404(target_id)
    fdict = {"following": False}
    if user.is_following(target_user):
        fdict["following"] = True
    return jsonify(fdict)


@bp.route('/users/<int:id>/follow', methods=['GET'])
@token_auth.login_required
def follow(id):
    target_user = User.query.get_or_404(id)
    g.current_user.follow(target_user)
    db.session.commit()
    return jsonify(target_user.to_dict())


@bp.route('/users/<int:id>/unfollow', methods=['GET'])
@token_auth.login_required
def unfollow(id):
    target_user = User.query.get_or_404(id)
    g.current_user.unfollow(target_user)
    db.session.commit()
    return jsonify(target_user.to_dict())