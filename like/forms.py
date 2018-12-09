# coding: utf-8
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import Email, Regexp, DataRequired, EqualTo, ValidationError
from like.utils import Memcached
from like.models import User


class SignUpForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired('请输入用户名')])
    email = StringField('邮箱', validators=[Email('请输入正确格式的邮箱'),
                                          DataRequired('请输入邮箱')])
    password = PasswordField('密码', validators=[DataRequired('密码不能为空')])
    password_repeat = PasswordField('重复密码', validators=[EqualTo('password', '密码输入不一致')])
    captcha = StringField('验证码', validators=[DataRequired('请输入验证码'),
                                             Regexp(r'^\d{6}$', message='验证码格式不正确')])
    submit = SubmitField('提交')

    def validate_captcha(self, field):
        email = self.email.data
        captcha_cached = Memcached.get(email)
        if not captcha_cached or captcha_cached != field.data:
            raise ValidationError('验证码错误')


class LoginForm(FlaskForm):
    email = StringField('邮箱', validators=[Email('请输入正确格式的邮箱'),
                                          DataRequired('请输入邮箱')])
    password = PasswordField('密码', validators=[DataRequired('密码不能为空')])
    submit = SubmitField('登录')

    def validate_password(self, field):
        email = self.email.data
        password = field.data
        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(password):
            raise ValidationError('用户名或密码错误')
        else:
            self.user = user