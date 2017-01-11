# -*- coding:utf-8 -*-
from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, logout_user, login_required, current_user

from ..email import send_mail
from . import auth
from .. import db
from ..models import User


@auth.route('/login', methods=['GET', 'POST'])
def login():
    from app.auth.forms import LoginForm
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):  # 密码验证成功
            login_user(user, form.remember_me.data)
            return redirect(url_for('main.index'))
        flash(u'帐号或者密码错误')
    return render_template('login.html', title=u'登陆', form=form)

@auth.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    flash(u'您已退出登陆')
    return redirect(url_for('auth.login'))


@auth.route('/register', methods=['GET', 'POST'])
def register():
    from app.auth.forms import RegisterForm
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(username=form.username.data,
                    password=form.password.data, email=form.email.data)  # 新添加一个用户到数据库中
        db.session.add(user)
        db.session.commit()
        User.add_self_follows()           # 把自己添加成自己的关注
        token = user.generate_confirm_token()                            # 产生一个令牌
        send_mail(user.email, u'请确认您的帐号', 'confirm', user=user, token=token)   # 发送邮件
        flash(u'有一份邮件已经发往您的邮箱')
        return redirect(url_for('auth.login'))    # 这一步一直有问题，无法重定向，直接跳到下面去了
    else:
        return render_template('register.html', title=u'注册', form=form)

@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.index'))          # 重复点击邮箱的令牌
    if current_user.confirm(token):
        flash(u'感谢您的确认')
    else:
        flash(u'链接已经失效或者过期')
    return redirect(url_for('main.index'))

@auth.before_app_request          # 用户已登陆、用户帐号还未确认、请求的的端点不在auth认证蓝本中
def before_request():
    if current_user.is_authenticated:
        current_user.ping()              # 在每次请求前刷新上次访问时间
        if not current_user.confirmed \
            and request.endpoint[:5] != 'auth.':
            return redirect(url_for('auth.unconfirmed'))

@auth.route('/unconfirmed')      # 如果当前是匿名帐号活着已经确认，直接返回首页，否则显示未确认
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('unconfirmed.html')

@auth.route('/resend_email')
@login_required
def resend_email():
    token = current_user.generate_confirm_token()
    send_mail(current_user.email, u'确认您的帐号', 'confirm', user=current_user, token=token)
    flash(u'一份新的邮件已经发往您的邮箱')
    return redirect(url_for('main.index'))