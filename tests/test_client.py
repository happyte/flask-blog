# -*- coding:utf-8 -*-
import unittest
from app import create_app, db
from app.models import User, Role
from flask import url_for
import re

class FlaskClientTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        Role.insert_roles()
        self.client = self.app.test_client(use_cookies=True)

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    # 测试主页
    def test_home_page(self):
        response = self.client.get(url_for('main.index'))    # 获得的响应就是index.html
        self.assertTrue(u'请先登陆' in response.get_data(as_text=True))

    # 测试注册与登陆
    def test_register_and_login(self):
        # 注册新用户
        response = self.client.post(url_for('auth.register'), data={
            'email': 'zs@example.com',
            'username': 'zs',
            'password': 'aa',
            'password2': 'aa'
        })
        self.assertTrue(response.status_code == 302)

        # 使用注册的新用户登陆
        response = self.client.post(url_for('auth.login'), data={
            'email': 'zs@example.com',
            'password': 'aa'
        }, follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertTrue(re.search(u'您好,\s*zs', data))   # 正则表达式匹配
        self.assertTrue(u'您至今还未确认您的帐号' in data)

        # 发送确认令牌
        user = User.query.filter_by(email='zs@example.com').first()
        token = user.generate_confirm_token()
        response = self.client.get(url_for('auth.confirm', token=token),
                                   follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertTrue(u'感谢您的确认' in data)

        # 退出登陆
        response = self.client.get(url_for('auth.logout'), follow_redirects=True)
        self.assertTrue(u'您已退出登陆' in response.data.decode('utf-8'))
