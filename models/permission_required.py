from functools import wraps
from flask import session, abort
from db import db

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('role') != 'admin':
            print("权限不通过。")
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

def hotel_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('role') != 'hotel':
            print("权限不通过。")
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

def customer_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('role') != 'customer':
            print("权限不通过。")
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

def permission_required(endpoint):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            userId = session.get('userId')
            if not userId:
                abort(401)  # 用户未登录，返回 401 未授权

            with db.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT * FROM UserPermission u 
                    LEFT JOIN Permission p ON u.permissionId = p.permissionId
                    WHERE userId = %s AND endpoint = %s
                    """,
                    (userId, endpoint)
                )
                existing = cursor.fetchone()

            if not existing:
                print("权限不通过。")
                abort(403)
            return f(*args, **kwargs)  # 正确地调用原始函数
        return decorated_function
    return decorator