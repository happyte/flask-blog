# -*- coding:utf-8 -*-
from threading import Thread
from flask_mail import Message
from flask import render_template
from . import mail
from flask import current_app    # 这样就不用使用from manager import app
import os

def send_async_mail(app, msg):
    with app.app_context():
        mail.send(msg)


# 四个参数分别为(1.接收者邮箱地址 2.主题 3.模板 4.可变参数)
def send_mail(to, subject, template, **kw):
    print '='*50
    print os.environ.get('MAIL_USERNAME')
    print os.environ.get('MAIL_PASSWORD')
    app = current_app._get_current_object()
    msg = Message(subject=subject, sender='zs511129@163.com',
                  recipients=[to])                               # 主题,发送者(从环境变量中读出),接收者
    msg.body = render_template(template + '.txt', **kw)          # 文本内容
    msg.html = render_template(template + '.html', **kw)         # 文本渲染
    thr = Thread(target=send_async_mail, args=[app, msg])
    thr.start()
    return thr