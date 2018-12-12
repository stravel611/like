# coding: utf-8
from flask import (
    Blueprint,
    render_template,
    current_app,
    request
    )
from like.models import Post, Topic, Comment, User
from flask_login import login_required, current_user
from sqlalchemy.sql.expression import func
from like.exts import db
from like.utils import Restful


user_bp = Blueprint('user', __name__, url_prefix='/user')


@user_bp.app_template_test()
def is_current_user(user):
    return user.id == current_user.id


@user_bp.route('/<int:user_id>')
@login_required
def index(user_id):
    user = User.query.get(user_id)
    return render_template('user/index.html', user=user, stream='post')


@user_bp.route('/post')
@login_required
def post():
    pass


@user_bp.route('/<int:user_id>/topic')
@login_required
def topic(user_id):
    user = User.query.get(user_id)
    topics = Topic.query.join(Topic.followers).filter(User.id==user_id).all()
    return render_template('user/topic.html', user=user, topics=topics)


@user_bp.route('/<int:user_id>/followers')
@login_required
def followers(user_id):
    user = User.query.get(user_id)
    followers = user.followers
    return render_template('user/follower.html', user=user, followers=followers)


@user_bp.route('/<int:user_id>/followed')
@login_required
def followed(user_id):
    user = User.query.get(user_id)
    followed = user.followed
    return render_template('user/followed.html', user=user, followed=followed)


@user_bp.route('/action/<string:target_type>/<string:action>')
def act(target_type, action):
    q_map = {
        'topic': {'like': 'followed_topics'},
        'post': {
            'like': 'liked_posts',
            'collect': 'collected_posts'
        },
        'comment': {'liked': 'liked_comments'}
    }

    model_map = {'topic': Topic, 'post': Post, 'comment': Comment}

    if current_user.is_authenticated:
        target_id = request.args.get('id', type=int)
        item = model_map[target_type].query.get(target_id)
        q = getattr(current_user, q_map[target_type][action])
        if item in q:
            q.remove(item)
            db.session.commit()
            return Restful.success('取消成功')
        else:
            q.append(item)
            db.session.commit()
            return Restful.success('关注成功')
    else:
        return Restful.unauth_error()