# -*- coding:utf-8 -*-
from selenium import webdriver
import unittest
from app import create_app, db
from app.models import User, Role, Post
import threading
import time

class SeleniumTestCase(unittest.TestCase):
    client = None

    @classmethod
    def setUpClass(cls):
        # 启动浏览器
        try:
            cls.client = webdriver.Safari()
        except:
            pass
        if cls.client:
            print 'nfjdjakkasfmaf'
            # 创建程序
            cls.app = create_app('testing')
            cls.app_context = cls.app.app_context()
            cls.app_context.push()

            # 禁止日志，保持输出简介
            import logging
            logger = logging.getLogger('werkzeug')
            logger.setLevel("ERROR")

            # 创建数据库，模拟数据填充
            db.create_all()
            Role.insert_roles()
            User.generate_fake(count=10)
            Post.generate_fake(count=10)

            # 添加管理员
            role_admin = Role.query.filter_by(permissions=0xff).first()
            admin = User(email='zs@example.com',
                         username='zs',
                         password='111',
                         itsrole=role_admin,
                         confirmed=True)
            db.session.add(admin)
            db.session.commit()

            # 在一个线程中启动Flask服务器
            # threading.Thread(target=cls.app.run).start()
            threading.Thread.__init__(target=cls.app.run).start()
            time.sleep(1)

    @classmethod
    def tearDownClass(cls):
        if cls.client:
            # 第一个关闭Flask服务器，第二个关闭浏览器(即客户端)
            cls.client.get('http://localhost:5000/shutdown')
            cls.client.close()

            db.drop_all()
            db.session.remove()
            cls.app_context.pop()

    def setUp(self):
        if not self.client:
            self.skipTest('Web browser not available')

    def tearDown(self):
        pass

    def test_admin_home_page(self):
        pass
