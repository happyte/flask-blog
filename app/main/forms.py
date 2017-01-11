# -*- coding:utf-8 -*-
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Email, Length
from flask_pagedown.fields import PageDownField
from ..models import Role

# 首页的博客文章表单
class PostForm(FlaskForm):
    title = StringField(label=u'博客标题', validators=[DataRequired()], id='titlecode')
    body = PageDownField(label=u'博客内容', validators=[DataRequired()],
                         render_kw={'rows': 20})
    submit = SubmitField(label=u'提交')

class CommentForm(FlaskForm):
    body = PageDownField(label=u'发表评论', validators=[DataRequired()])
    submit = SubmitField(label=u'提交')


# 普通用户登陆表单
class EditProfileForm(FlaskForm):
    name = StringField(label=u'真实姓名', validators=[Length(0,64)])
    location = StringField(label=u'地址', validators=[Length(0,64)])
    about_me = TextAreaField(label=u'关于我')
    submit = SubmitField(label=u'提交')


# 管理员登陆表单,能编辑用户的电子邮件，用户名，确认状态和角色
class EditProfileAdministratorForm(FlaskForm):
    email = StringField(label=u'邮箱', validators=[DataRequired(), Length(1,64), Email()])
    username = StringField(label=u'用户名', validators=[DataRequired(), Length(1, 64)])
    confirmed = BooleanField(label=u'确认')
    role = SelectField(label=u'角色', coerce=int)

    name = StringField(label=u'真实姓名', validators=[Length(0, 64)])
    location = StringField(label=u'地址', validators=[Length(0, 64)])
    about_me = TextAreaField(label=u'关于我')
    submit = SubmitField(label=u'提交')

    # 初始化时要对role的复选框进行搭建
    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdministratorForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name) for role in Role.query.order_by(Role.name)]
        self.user = user