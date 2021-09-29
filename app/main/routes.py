from flask import render_template
from app.models import User, LiveRequests
from app.main import bp
from flask import jsonify, request, redirect, url_for
from app import db


@bp.route('/')
@bp.route('/index')
def index():
    number_of_users = User.query.count()
    return render_template('index.html', number_of_users=number_of_users)


@bp.route('/admin')
def admin():
    users = User.query.order_by(User.id.desc())
    all_users = [{'id': user.id,
                  'name': user.name,
                  'username': user.username,
                  'email': user.email,
                  'photo': user.avatar,
                  'country': user.country,
                  'gender': user.gender,
                  'login_type': user.login_type,
                  'creation_date': user.creation_date,
                  } for user in users]

    # return jsonify({"users": all_users})
    return render_template('admin.html', all_users=all_users)


@bp.route('/liverequests')
def liverequests():
    # requests = LiveRequests.query.order_by(LiveRequests.id.desc())
    requests = db.engine.execute(
        "SELECT user.username,user.id,user.email,user.name,user.country,user.avatar,user.gender, "
        "live_requests.live_request  from user, live_requests where live_requests.user_id=user.id")

    # users=User.query.filter_by(id=30).first()
    # return user
    all_requestss = [{
        'id': request.id,
        'username': request.username,
        'photo': request.avatar,
        'email': request.email,
        'live_request': request.live_request,
        'gender': request.gender,
        'country': request.country,
        'name': request.name,

    } for request in requests]

    # return jsonify({"users": all_users})
    return render_template('liverequests.html', all_requests=all_requestss)


@bp.route('/approveRequest/<int:userid>')
def approveRequest(userid):
    user = User.query.filter_by(id=userid).first()
    liverequests = LiveRequests.query.filter_by(user_id=userid).first()
    liverequests.live_request = 1
    user.can_go_live = 1
    db.session.commit()
    return redirect(url_for('main.liverequests'))


@bp.route('/unapproveRequest/<int:userid>')
def unapproveRequest(userid):
    user = User.query.filter_by(id=userid).first()
    liverequests = LiveRequests.query.filter_by(user_id=userid).first()
    liverequests.live_request = 0
    user.can_go_live = 0
    db.session.commit()
    return redirect(url_for('main.liverequests'))


'''
@bp.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.post.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post is now live!')
        return redirect(url_for('main.index'))
    page = request.args.get('page', 1, type=int)
    posts = current_user.followed_posts().paginate(
        page, current_app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('main.index', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('main.index', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('index.html', title='Home', form=form,
                           posts=posts.items, next_url=next_url,
                           prev_url=prev_url)


@bp.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    posts = user.posts.order_by(Post.timestamp.desc()).paginate(
        page, current_app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('main.user', username=user.username, page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('main.user', username=user.username, page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('user.html', user=user, posts=posts.items,
                           next_url=next_url, prev_url=prev_url)


@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('main.edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile',
                           form=form)


@bp.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found.'.format(username))
        return redirect(url_for('index'))
    if user == current_user:
        flash('You cannot follow yourself!')
        return redirect(url_for('main.user', username=username))
    current_user.follow(user)
    db.session.commit()
    flash('You are following {}!'.format(username))
    return redirect(url_for('main.user', username=username))


@bp.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found.'.format(username))
        return redirect(url_for('main.index'))
    if user == current_user:
        flash('You cannot unfollow yourself!')
        return redirect(url_for('main.user', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash('You are not following {}.'.format(username))
    return redirect(url_for('main.user', username=username))


@bp.route('/explore')
@login_required
def explore():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, current_app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('main.explore', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('main.explore', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template("index.html", title='Explore', posts=posts.items,
                           next_url=next_url, prev_url=prev_url)'''
