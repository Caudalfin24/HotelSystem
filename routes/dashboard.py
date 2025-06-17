from flask import render_template, url_for, redirect, request, flash, session, abort
from datetime import datetime
from werkzeug.security import check_password_hash, generate_password_hash
from . import dashboard_bp
from . import auth_bp
from db import db
from models.user import User
from models.permission import Permission, UserPermission
from models.customer import Customer
from models.hotel import Hotel
from models.room import Room
from models.booking import Booking
from models.permission_required import *

""" CUSTOMER """

@dashboard_bp.route('/dashboard/customer')
@customer_required
def dashboard_customer():
    userId = session.get('userId')
    role = session.get('role')
    print(role)
    if role != 'customer':
        abort(403)
        
    if not userId:
        return redirect(url_for('auth.index'))
    
    
    customer = Customer.fetchCustomer(userId)
    if not customer:
        abort(404)
    
    return render_template('customer_dashboard.html', customer=customer)

@dashboard_bp.route('/dashboard/customer/edit', methods=['GET', 'POST'])
@customer_required
def customer_edit():
    userId = session.get('userId')
    customer = Customer.fetchCustomer(userId)
    if not customer:
        abort(404)
            
    if request.method == 'POST':
        customerName = request.form.get('customerName')
        email = request.form.get('email')
        customerPhone = request.form.get('customerPhone')
        age = request.form.get('age')
        sex = request.form.get('sex')
        Customer.updateCustomer(userId, customerName, email, customerPhone, age, sex)
        flash("更新完成")
        return redirect(url_for('dashboard.customer_edit'))
    return render_template('customer_edit.html', customer=customer)

@dashboard_bp.route('/dashboard/customer/hotels')
@customer_required
@permission_required('customer.booking_hotels')
def list_hotels():
    search = request.args.get('search', '').strip()
    city = request.args.get('city', '').strip()
    
    
    if search or city:
        hotels = Hotel.fetchHotelsWithCondition(search, city)
    else:
        hotels = Hotel.fetchAllHotels()
    
    cities = Hotel.fetchAllCities()
    city_list = [c['city'] for c in cities]
    return render_template('customer_hotels.html', hotels=hotels, search=search, cities=city_list, selected_city=city)

@dashboard_bp.route('/dashboard/customer/hotels/<int:hotel_id>/book', methods=['GET', 'POST'])
@customer_required
@permission_required('customer.booking_hotels')
def book_hotel(hotel_id):
    hotel = Hotel.fetchHotel(hotel_id)
    if not hotel:
        abort(404)
    rooms = Room.fetchAllRooms(hotel_id)
    if not rooms:
        abort(404)
        
    if request.method == 'POST':
        room_id = request.form.get('room_id')
        check_in = request.form.get('check_in')
        check_out = request.form.get('check_out')
        room = Room.fetchRoom(room_id)

        if not room or room['available'] < 1:
            flash("房间不可用", "error")
            return redirect(request.url)
        
        days = (datetime.strptime(check_out, '%Y-%m-%d') - datetime.strptime(check_in, '%Y-%m-%d')).days
        total_price = room['price'] * days
        customer_id = session.get('userId')
        Booking.addBooking(customer_id, room_id, check_in, check_out, total_price)
        
        flash("预定成功")
        return redirect(url_for('dashboard.list_hotels'))

    return render_template('customer_book_hotel.html', hotel=hotel, rooms=rooms)

@dashboard_bp.route('/customer/bookings')
@customer_required
@permission_required('customer.view_bookings')
def view_bookings():
    customer_id = session.get('userId')
    if not customer_id:
        abort(401)
        
    search = request.args.get('search', '').strip()
    status_filter = request.args.get('status', '')
    checkin_from = request.args.get('checkin_from', '')
    checkin_to = request.args.get('checkin_to', '')
    checkout_from = request.args.get('checkout_from', '')
    checkout_to = request.args.get('checkout_to', '')


    bookings = Booking.fetchBookings(customer_id, search, status_filter, checkin_from, checkin_to, checkout_from, checkout_to)
    return render_template('customer_bookings.html', 
        bookings=bookings,
        search=search,
        status_filter=status_filter,
        checkin_from=checkin_from,
        checkin_to=checkin_to,
        checkout_from=checkout_from,
        checkout_to=checkout_to)

@dashboard_bp.route('/customer/bookings/<int:booking_id>/update', methods=['POST'])
@customer_required
@permission_required('customer.view_bookings')
def update_order_status(booking_id):
    booking = Booking.fetchBooking(booking_id)
    if booking['status'] == 'notCheckIn':
        Booking.updateStatus(booking_id, 'checkIn')
        flash("已办理入住。")
    elif booking['status'] == 'checkIn':
        Booking.updateStatus(booking_id, 'checkOut')
        flash("已退房。")
    else:
        flash("订单已完成。")

    return redirect(url_for('dashboard.view_bookings'))

@dashboard_bp.route('/customer/change_password/<role>', methods=['GET', 'POST'])
@permission_required('user.change_password')
def change_password(role):
    if request.method == 'POST':
        old_password = request.form.get('old_password').strip()
        new_password = request.form.get('new_password').strip()
        confirm_password = request.form.get('confirm_password').strip()
        userId = session.get('userId')
        
        cur_password = User.fetchUser(userId)['password']
        if not check_password_hash(cur_password, old_password):
            flash('旧密码错误！', 'error')
            return redirect(url_for('dashboard.change_password', role=role))

        if new_password != confirm_password:
            flash('两次输入的新密码不一致！', 'error')
            return redirect(url_for('dashboard.change_password', role=role))

        if len(new_password) < 6:
            flash('新密码长度至少6位！', 'error')
            return redirect(url_for('dashboard.change_password', role=role))

        # 更新密码
        User.updatePassword(userId, generate_password_hash(new_password))

        flash('密码修改成功！请重新登录。', 'success')
        return redirect(url_for('auth.logout')) 

    if role == 'customer':
        return render_template('customer_change_password.html')
    elif role == 'hotel':
        return render_template('hotel_change_password.html')
    else:
        return render_template('admin_change_password.html')


""" HOTEL """

@dashboard_bp.route('/dashboard/hotel')
@hotel_required
def dashboard_hotel():
    userId = session.get('userId')
    if not userId:
        abort(401)
    search = request.args.get('search', '').strip()
    city = request.args.get('city', '').strip()
    
    
    if search or city:
        hotels = Hotel.fetchHotelsWithCondition(search, city, userId)
    else:
        hotels = Hotel.fetchOwnerHotels(userId)
    
    cities = Hotel.fetchAllCities()
    city_list = [c['city'] for c in cities]
    return render_template('hotel_dashboard.html', hotels=hotels, cities=city_list, search=search, selected_city=city)

@dashboard_bp.route('/dashboard/hotel/<int:hotel_id>')
@hotel_required
def hotel_detail(hotel_id):
    userId = session.get('userId')
    if not userId:
        abort(401)    
    hotel = Hotel.fetchHotel(hotel_id)
    if not hotel:
        abort(404)
    
    keyword = request.args.get('search', '')
    if not keyword:
        rooms = Room.fetchAllRooms(hotel_id)
    else:
        rooms = Room.fetchRoomsWithKeyword(hotel_id, keyword)
    return render_template('hotel_detail.html', hotel=hotel, rooms=rooms, keyword=keyword)

@dashboard_bp.route('/dashboard/hotel/add', methods=['GET', 'POST'])
@hotel_required
@permission_required('hotel.manage_hotel')
def add_hotel():
    userId = session.get('userId')
    if not userId:
        abort(401)
    
    if request.method == 'POST':
        hotelName = request.form.get('hotelName')
        city = request.form.get('city')
        address = request.form.get('address')
        phone = request.form.get('hotelPhone')
        rating = request.form.get('rating')    
        
        Hotel.addHotel(hotelName, userId, city, address, phone, rating)
        flash("添加成功")
        return redirect(url_for('dashboard.dashboard_hotel'))
    return render_template('hotel_add.html')    

@dashboard_bp.route('/dashboard/hotel/<int:hotel_id>/edit', methods=['GET', 'POST'])
@hotel_required
@permission_required('hotel.manage_hotel')
def edit_hotel(hotel_id):
    userId = session.get('userId')
    if not userId:
        abort(401)
    hotel = Hotel.fetchHotel(hotel_id)
    if not hotel:
        abort(404)        
    if request.method == 'POST':
        hotelName = request.form.get('hotelName')
        city = request.form.get('city')
        address = request.form.get('address')
        phone = request.form.get('hotelPhone')
        rating = request.form.get('rating')    
        
        Hotel.editHotel(hotel_id, hotelName, city, address, phone, rating)
        flash("修改成功")
        return redirect(url_for('dashboard.dashboard_hotel'))
    return render_template('hotel_edit.html', hotel=hotel)   

@dashboard_bp.route('/dashboard/hotel/<int:hotel_id>/delete', methods=['POST'])
@hotel_required
@permission_required('hotel.manage_hotel')
def delete_hotel(hotel_id):
    userId = session.get('userId')
    if not userId:
        abort(401)
       
    Hotel.deleteHotel(hotel_id)
    flash("删除成功")
    return redirect(url_for('dashboard.dashboard_hotel'))

@dashboard_bp.route('/dashboard/hotel/<int:hotel_id>/room/add', methods=['GET', 'POST'])
@hotel_required
@permission_required('hotel.manage_hotel')
def add_room(hotel_id):
    userId = session.get('userId')
    if not userId:
        abort(401)
    hotel = Hotel.fetchHotel(hotel_id)
    if not hotel:
        abort(404)

    if request.method == 'POST':
        room_type = request.form.get('roomType')
        price = request.form.get('price')
        total = request.form.get('totalNum')
        desc = request.form.get('description')
        
        Room.addRoom(hotel_id, room_type, price, total, desc)
        
        flash("添加成功")
        return redirect(url_for('dashboard.hotel_detail', hotel_id=hotel_id))
    return render_template('room_add.html', hotel=hotel)

@dashboard_bp.route('/dashboard/hotel/<int:hotel_id>/room/<int:room_id>/edit', methods=['GET', 'POST'])
@hotel_required
@permission_required('hotel.manage_hotel')
def edit_room(hotel_id, room_id):
    userId = session.get('userId')
    if not userId:
        abort(401)
    hotel = Hotel.fetchHotel(hotel_id)
    if not hotel:
        abort(404)
    room = Room.fetchRoom(room_id)
    if not room:
        abort(404)
        
    if request.method == 'POST':
        room_type = request.form.get('roomType')
        price = request.form.get('price')
        total = request.form.get('totalNum')
        desc = request.form.get('description')
        
        Room.editRoom(room_id, room_type, price, total, desc)
        
        flash("修改成功")
        return redirect(url_for('dashboard.hotel_detail', hotel_id=hotel_id))
    return render_template('room_edit.html', hotel=hotel, room=room)        
     
@dashboard_bp.route('/dashboard/hotel/<int:hotel_id>/room/<int:room_id>/delete', methods=['POST'])
@hotel_required
@permission_required('hotel.manage_hotel')
def delete_room(hotel_id, room_id):
    userId = session.get('userId')
    if not userId:
        abort(401)
    hotel = Hotel.fetchHotel(hotel_id)
    if not hotel:
        abort(404)
    
    Room.deleteRoom(room_id)
    return redirect(url_for('dashboard.hotel_detail', hotel_id=hotel_id))

@dashboard_bp.route('/dashboard/hotel/<int:hotel_id>/bookings')
def hotel_bookings(hotel_id):
    user_id = session.get('userId')
    if not user_id:
        abort(401)

    hotel = Hotel.fetchHotel(hotel_id)
    if not hotel:
        abort(404)

    checkin_start = request.args.get('checkin_start')
    checkin_end = request.args.get('checkin_end')
    status = request.args.get('status')

    # 查询该酒店下所有订单
    bookings = Booking.fetchBookings(checkin_from=checkin_start, checkin_to=checkin_end, status_filter=status, hotelId=hotel_id)

    return render_template('hotel_bookings.html', hotel=hotel, bookings=bookings, checkin_start=checkin_start, checkin_end=checkin_end, selected_status=status)



""" ADMIN """
@dashboard_bp.route('/dashboard/admin')
@admin_required
def dashboard_admin():
    return redirect(url_for('dashboard.admin_user_manage'))

# 用户管理
@dashboard_bp.route('/dashboard/admin/user_manage')
@admin_required
def admin_user_manage():
    keyword = request.args.get('search', '')
    
    if keyword:
        users = User.fetchUsersWithCondition(keyword)
    else:
        users = User.fetchAllUsers()
    return render_template('admin_user_manage.html', users=users, search=keyword)

@dashboard_bp.route('/dashboard/admin/delete_user/<int:userId>', methods=['POST'])
@admin_required
def admin_delete_user(userId):
    User.deleteUser(userId)
    return redirect(url_for('dashboard.admin_user_manage'))

@dashboard_bp.route('/dashboard/admin/delete_users', methods=['POST'])
@admin_required
def admin_delete_users():
    ids = request.form.getlist('userIds')
    User.deleteUsers(ids)
    return redirect(url_for('dashboard.admin_user_manage'))


@dashboard_bp.route('/dashboard/admin/edit_permissions/<int:userId>')
@admin_required
def admin_edit_permissions(userId):
    allPermissions = Permission.fetchAllPermissions()
    userPermissions = UserPermission.fetchUserPermissions(userId)
    return render_template('admin_edit_permission.html',
                           user_id=userId,
                           all_permissions=allPermissions,
                           user_permissions=userPermissions)
    
@dashboard_bp.route('/dashboard/admin/add_permission', methods=['POST'])
@admin_required
def admin_add_permission():
    userId = request.form.get('userId')
    permissionId = request.form.get('permissionId')
    ret = UserPermission.addPermission(userId, permissionId)
    flash(ret)
    return redirect(url_for('dashboard.admin_edit_permissions', userId=userId))


@dashboard_bp.route('/dashboard/admin/delete_permission', methods=['POST'])
@admin_required
def admin_delete_permission():
    userId = request.form.get('userId')
    permissionId = request.form.get('permissionId')
    print(userId, permissionId)
    UserPermission.deletePermission(userId, permissionId)
    return redirect(url_for('dashboard.admin_edit_permissions', userId=userId))


# 酒店管理
@dashboard_bp.route('/dashboard/admin/hotel_manage')
@admin_required
def admin_hotel_manage():
    hotels = Hotel.fetchAllHotels()
    search = request.args.get('search', '').strip()
    city = request.args.get('city', '').strip()
    
    
    if search or city:
        hotels = Hotel.fetchHotelsWithCondition(search, city)
    else:
        hotels = Hotel.fetchAllHotels()
    
    cities = Hotel.fetchAllCities()
    city_list = [c['city'] for c in cities]
    return render_template('admin_hotel_manage.html', hotels=hotels, cities=city_list, search=search, selected_city=city)


@dashboard_bp.route('/dashboard/admin/delete_hotel/<int:hotelId>', methods=['POST'])
@admin_required
def admin_delete_hotel(hotelId):
    Hotel.deleteHotel(hotelId)
    return redirect(url_for('dashboard.admin_hotel_manage'))


@dashboard_bp.route('/dashboard/admin/delete_hotels', methods=['POST'])
@admin_required
def admin_delete_hotels():
    ids = request.form.getlist('hotelIds')
    Hotel.deleteHotels(ids)
    return redirect(url_for('dashboard.admin_hotel_manage'))

@dashboard_bp.route('/dashboard/admin/edit_hotel/<int:hotelId>', methods=['GET', 'POST'])
@admin_required
def admin_edit_hotel(hotelId):
    hotel = Hotel.fetchHotel(hotelId)
    if not hotel:
        abort(404) 
               
    if request.method == 'POST':
        hotelName = request.form.get('hotelName')
        city = request.form.get('city')
        address = request.form.get('address')
        phone = request.form.get('hotelPhone')
        rating = request.form.get('rating')    
        
        Hotel.editHotel(hotelId, hotelName, city, address, phone, rating)
        flash("修改成功")
        return redirect(url_for('dashboard.admin_hotel_manage'))
    return render_template('admin_edit_hotel.html', hotel=hotel)


# 客户管理
@dashboard_bp.route('/dashboard/admin/customer_manage')
@admin_required
def admin_customer_manage():
    search = request.args.get('search', '').strip()
    min_age = request.args.get('min_age', '')
    max_age = request.args.get('max_age', '')
    sex = request.args.get('sex', '').strip()
    
    customers = Customer.fetchCustomers(search, min_age, max_age, sex)
    return render_template('admin_customer_manage.html', customers=customers, search=search, min_age=min_age, max_age=max_age, sex=sex)



@dashboard_bp.route('/dashboard/admin/edit_customer/<int:customerId>', methods=['GET', 'POST'])
@admin_required
def admin_edit_customer(customerId):
    customer = Customer.fetchCustomer(customerId)
    if not customer:
        abort(404)
            
    if request.method == 'POST':
        customerName = request.form.get('customerName')
        email = request.form.get('email')
        customerPhone = request.form.get('customerPhone')
        age = request.form.get('age')
        sex = request.form.get('sex')
        Customer.updateCustomer(customerId, customerName, email, customerPhone, age, sex)
        flash("更新完成")
        return redirect(url_for('dashboard.admin_customer_manage'))
    return render_template('admin_edit_customer.html', customer=customer)

