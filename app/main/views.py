# -*- coding:utf-8 -*-
from flask import render_template, flash, abort, redirect, url_for, request, current_app, make_response
from flask_login import login_required, current_user
from ..decorators import admin_required, permission_required
from ..models import Permission, User, Role, Post
from . import main
from .forms import EditProfileForm, EditProfileAdministratorForm, PostForm
from .. import db


@main.route('/', methods=['GET','POST'])
def index():
    form = PostForm()
    if current_user.can(Permission.WRITE_ARTICLES) and \
            form.validate_on_submit():
        post = Post(body=form.body.data, author=current_user._get_current_object())
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('main.index'))
    show_followed = False
    if current_user.is_authenticated:
        show_followed = bool(request.cookies.get('show_followed'))   # 判断cookie是否大于0
    if show_followed:
        query = current_user.followed_posts
    else:
        query = Post.query
    page = request.args.get('page',1, type=int)       # 1代表如果没有明确指定，则默认渲染第一页,为2的话默认来到第二页
    pagination = query.order_by(Post.timestamp.desc()).paginate(
                                    page, per_page=10,
                                    error_out=False)  # error_out=True页数超出范围返回404错误,False返回空列表
    posts = pagination.items
    return render_template('index.html', show_followed=show_followed, form=form, posts=posts, pagination=pagination)

@main.route('/all')
@login_required
def show_all():
    response = make_response(redirect(url_for('main.index')))
    response.set_cookie('show_followed','',max_age=30*24*60*60)    # 通过cookie的值判断点击了all还是followed
    return response

@main.route('/followed')
@login_required
def show_followed():
    response = make_response(redirect(url_for('main.index')))
    response.set_cookie('show_followed','2',max_age=30*24*60*60)
    return response

# 首页中文章固定链接路由
@main.route('/post/<int:id>')
def post(id):
    post = Post.query.get_or_404(id)
    return render_template('post.html', posts=[post])

@main.route('/about')
def about():
    return 'About'


@main.route('/admin')      # 在登陆状态下只允许管理者进入，否则来到403禁止登陆界面
@login_required
@admin_required
def for_admin_only():
    return u'管理者进入'

@main.route('/moderator')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def for_moderator_only():
    return u'管理者进入'

@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        abort(404)
    posts = user.posts.order_by(Post.timestamp.desc()).all()
    return render_template('user.html', user=user, posts=posts)

# 关注用户
@main.route('/follow/<username>')
def follow(username):
    u = User.query.filter_by(username=username).first()
    if u is None:
        flash(u'没有该用户')
        return redirect(url_for('main.index'))
    if current_user.is_following(u):
        flash(u'已经关注了该用户')
        return redirect(url_for('main.user', username=username))
    current_user.follow(u)
    flash(u'关注了 %s' % username)
    return redirect(url_for('main.user', username=username))

# 取消关注
@main.route('/unfollow/<username>')
def unfollow(username):
    u = User.query.filter_by(username=username).first()
    if u is None:
        flash(u'没有该用户')
        return redirect(url_for('main.index'))
    if u.is_followed_by(current_user):
        current_user.unfollow(u)
        flash(u'取消对 %s 的关注' % username)
        return redirect(url_for('main.user', username=username))

# 列出所有的粉丝
@main.route('/followers/<username>')
def followers(username):
    u = User.query.filter_by(username=username).first()
    page = request.args.get('page', 1, type=int)
    pagination = u.followers.paginate(page, per_page=10, error_out=False)
    follows = [{'user':item.follower,'timestamp':item.timestamp}
               for item in pagination.items]                      # 转换成一个字典列表
    return render_template('followers.html', title=u'的粉丝',user=u, pagination=pagination, follows=follows)

# 列出所有我的关注
@main.route('/followed-by/<username>')
def followed_by(username):
    u = User.query.filter_by(username=username).first()
    page = request.args.get('page', 1, type=int)
    pagination = u.followed.paginate(page, per_page=10, error_out=False)
    follows = [{'user':item.followed,'timestamp':item.timestamp}
               for item in pagination.items]                      # 转换成一个字典列表
    return render_template('followers.html', title=u'的关注',user=u, pagination=pagination, follows=follows)


# 普通用户级别的编辑
@main.route('/edit-profile',methods=['GET','POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        flash(u'你的个人信息已经被更改')
        db.session.add(current_user)              # 更新个人资料
        db.session.commit()
        return redirect(url_for('main.user', username=current_user.username))
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html',form=form)

# 管理员级别的编辑
@main.route('/edit-profile/<int:id>',methods=['GET','POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id)  # 查找这个用户
    form = EditProfileAdministratorForm(user=user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        user.itsrole = Role.query.get(form.role.data)
        user.name = form.name.data
        user.location = form.location.data
        user.about_me = form.about_me.data
        db.session.add(user)
        db.session.commit()
        flash(u'该用户的信息已经更新了')
        return redirect(url_for('main.user',username=user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id          # role_id 与 itsrole是关联的
    form.name.data = user.name
    form.location.data = user.location
    form.about_me.data = user.about_me
    return render_template('edit_profile.html',form=form,user=user)

# 编辑博客文章路由
@main.route('/edit/<int:id>', methods=['GET','POST'])
@login_required
def edit(id):
    post = Post.query.get_or_404(id)
    if current_user != post.author and \
            not current_user.can(Permission.ADMINISTRATOR):       # 当前作者不是发表博客的人且不是管理员
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.body = form.body.dataa
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('main.post',id=post.id))
    form = PostForm()
    form.body.data = post.body
    return render_template('edit_post.html', form=form)


@main.app_context_processor
def inject_permissions():
    return dict(Permission=Permission)


@main.app_errorhandler(404)
def page_not_found(error):
    return render_template('404.html'),404

@main.app_errorhandler(403)
def forbidden_enter(error):
    return render_template('403.html'),403


# @main.route('/upload',methods=['GET','POST'])
# def upload():
#     if request.method == 'POST':
#         f = request.files['file']
#         basepath = path.abspath(path.dirname(__file__))
#         print basepath
#         uploadpath = path.join(basepath,'static/uploads/')
#         print uploadpath
#         f.save(uploadpath+secure_filename(f.filename))
#         return redirect(url_for('upload'))
#     return render_template('upload.html')


# @main.route('/user/<regex("[a-z]{3}"):username>')
# def user(username):
#     return 'User %s' % username
