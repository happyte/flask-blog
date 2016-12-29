# -*- coding:utf-8 -*-
from flask import g
from .errors import forbidden
from functools import wraps


# 装饰器函数,带参数，3层函数
def permission_required(permissions):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if not g.current_user.can(permissions):
                return forbidden(u'没有相应的权限')
            return f(*args, **kwargs)
        return wrapper
    return decorator