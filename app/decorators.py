# -*- coding:utf-8 -*-
from functools import wraps
from flask import abort
from flask_login import current_user
from .models import Permission


# 装饰器函数,带参数，3层函数
def permission_required(permissions):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if not current_user.can(permissions):
                abort(403)
            return f(*args, **kwargs)
        return wrapper
    return decorator

# 调用上面装饰器函数
def admin_required(f):
    return permission_required(Permission.ADMINISTRATOR)(f)     # 带参数，且传递函数