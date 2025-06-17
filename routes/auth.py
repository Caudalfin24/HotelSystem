from flask import render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from . import auth_bp
from db import db
from models.user import User

# 首页重定向到客户登录页面
@auth_bp.route('/')
def index():
    if 'userId' in session and 'role' in session:
        role = session['role']
        print(role)
        return redirect(url_for(f'dashboard.dashboard_{role}'))
    # 未登录默认跳转到客户登录
    return redirect(url_for('auth.login_customer'))

# 注册页面
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])
        role = request.form['role']

        existing_user = User.fetchUser(username)

        if existing_user:
            return '用户名已存在，请选择其他用户名。'
        else:
            User.addUser(username, password, role)
            return redirect(url_for('auth.index'))
    return render_template('register.html')

# 登录（通用逻辑）
def login_user(role):
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.fetchUserWithUsernameAndRole(username, role)
        if user and check_password_hash(user['password'], password):
            session['userId'] = user['userId']
            session['username'] = user['username']
            session['role'] = user['role']
            role = user['role']
            return redirect(url_for(f'dashboard.dashboard_{role}'))
        else:
            return "登录失败，请检查用户名或密码。"
    return render_template(f'login_{role}.html')

# 客户登录页面
@auth_bp.route('/login/customer', methods=['GET', 'POST'])
def login_customer():
    return login_user('customer')

# 酒店登录页面
@auth_bp.route('/login/hotel', methods=['GET', 'POST'])
def login_hotel():
    return login_user('hotel')

# 管理员登录页面
@auth_bp.route('/login/admin', methods=['GET', 'POST'])
def login_admin():
    return login_user('admin')



@auth_bp.route('/logout', methods=['GET', 'POST'])
def logout():
    session.clear()
    return redirect(url_for('auth.index'))