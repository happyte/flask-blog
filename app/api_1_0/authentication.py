# -*- coding:utf-8 -*-
from flask import g, jsonify
from flask_httpauth import HTTPBasicAuth
from ..models import User, AnonymousUser
from . import api
from .errors import unauthorized, forbidden


auth = HTTPBasicAuth()

# api验证用户是否登陆,每次验证api先来到这个装饰器函数,在来到before_request函数
@auth.verify_password
def verify_password(email_or_token, password):
    if email_or_token == '':                  # 匿名用户
        g.current_user = AnonymousUser()
        return True
    if password == '':              # 用token进行验证
        g.current_user = User.verify_auth_token(email_or_token)
        g.token_used = True
        return g.current_user is not None
    user = User.query.filter_by(email=email_or_token).first()   # 按正常的邮箱查询
    if not user:
        return False
    g.current_user = user
    g.token_used = False
    return user.verify_password(password)


@api.route('/token')
def get_token():
    if g.current_user.is_anonymous or g.token_used:  # 匿名用户或者令牌已经被使用
        return unauthorized('Invalid credentials')
    return jsonify({'token': g.current_user.generate_auth_token(expiration=3600), 'expiration': 3600})

# 在每次请求前检查该用户是否已经通过验证
@api.before_app_request
@auth.login_required
def before_request():
    if not g.current_user.is_anonymous and not g.current_user.confirmed:
        return forbidden('Unconfirmed account')

@auth.error_handler
def auth_error():
    return unauthorized('Invalid credentials')