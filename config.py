# -*- coding:utf-8 -*-
import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_RECORD_QUERIES = True
    MAIL_SERVER = 'smtp.163.com'          # 配置163邮箱的smtp服务,首先你的邮箱要开启smtp服务
    MAIL_PORT = 465                       # 端口为465
    MAIL_USE_SSL = True                   # TLS服务失败，要用SSL
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    FLASK_ADMIN = os.environ.get('FLASK_ADMIN')
    POSTS_PER_PAGE = os.environ.get('POSTS_PER_PAGE')
    FLASKY_SLOW_DB_QUERY_TIME = 0.5

    @staticmethod
    def init_app(app):
        pass

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
                              'sqlite:///' + os.path.join(basedir, 'data-test.sqlite')
    WTF_CSRF_ENABLED = False

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'db.sqlite')


conifg = {
    'testing': TestingConfig,
    'default': DevelopmentConfig
}