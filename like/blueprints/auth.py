# coding: utf-8
from flask import Blueprint, redirect, url_for, render_template, request, current_app
from flask_login import current_user, login_user, logout_user, login_required
from like.forms import SignUpForm, LoginForm
from like.models import User
from like.exts import db
from like.utils import generate_captcha, Memcached, Restful
from like.tasks import send_email


auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/sign_up', methods=['GET', 'POST'])
def sign_up():
    if current_user.is_authenticated:
        return redirect(url_for('front.index'))
    form = SignUpForm()
    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = form.password.data
        user = User(username=username, email=email)
        user.password = password
        user.set_role('USER')
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect(url_for('front.index'))
    else:
        return render_template('auth/signup.html', form=form)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('front.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = form.user
        login_user(user)
        current_app.logger.info(f'User<id: {current_user.id}> logged in.')
        return redirect(url_for('front.index'))
    else:
        return render_template('auth/login.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    current_app.logger.info(f'User<id: {current_user.id}> logged out.')
    logout_user()
    return redirect(url_for('front.index'))


@auth_bp.route('/email_captcha')
def email_captcha():
    email = request.args.get('email')
    captcha = generate_captcha()
    send_email.delay('验证码', recipients=[email], body='验证码为：'+captcha)
    Memcached.set(email, captcha)
    return Restful.success()
