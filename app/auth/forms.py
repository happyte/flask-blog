# -*- coding:utf-8 -*-
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField
from wtforms.validators import DataRequired, Email, Length, EqualTo

#登陆表
class LoginForm(FlaskForm):
    email = StringField(label=u'邮箱',validators=[DataRequired(), Length(1,64), Email()], id='loginlength')
    password = PasswordField(label=u'密码',validators=[DataRequired()], id='loginlength')
    remember_me = BooleanField(label=u'记住我', id='loginlength')
    submit = SubmitField(label=u'登陆')

#注册表
class RegisterForm(FlaskForm):
    email = StringField(label=u'邮箱地址',validators=[DataRequired(), Length(1,64), Email()], id='registerlength')
    username = StringField(label=u'用户名',validators=[DataRequired(), Length(1,64)],
                           id='registerlength')
    password = PasswordField(label=u'密码',validators=[DataRequired(),
                            EqualTo('password2', message=u'密码必须相同')], id='registerlength')
    password2 = PasswordField(label=u'确认密码',validators=[DataRequired()], id='registerlength')
    submit = SubmitField(label=u'马上注册')