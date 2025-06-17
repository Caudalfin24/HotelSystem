import pymysql
from db import db


class Booking:
    @staticmethod
    def addBooking(customerId, roomId, checkIn, checkOut, totalPrice):
        try:
            with db.cursor() as cursor:
                cursor.execute("""
                               INSERT INTO Booking (customerId, roomId, checkIn, checkOut, totalPrice, status)
                               VALUES (%s, %s, %s, %s, %s, %s);
                               """,(customerId, roomId, checkIn, checkOut, totalPrice, 'notCheckIn'))
                cursor.execute("""
                               UPDATE Room
                               SET available = GREATEST(0, available - 1)
                               WHERE roomId=%s;
                               """, (roomId,))
                db.commit()
        except pymysql.MySQLError as e:
            print("数据库错误：", e)  
            
    @staticmethod
    def fetchBookings(customerId=None, search=None, status_filter=None, checkin_from=None, checkin_to=None, checkout_from=None, checkout_to=None, hotelId=None):
        try:
            query = """
                    SELECT * FROM Booking b
                    LEFT JOIN Room r ON b.roomId=r.roomId 
                    LEFT JOIN Hotel h ON r.hotelId=h.hotelId
                    WHERE 1=1
                    """
            params = []
            if customerId:
                query += " AND customerId=%s"
                params.append(customerId)
            
            if search:
                query += " AND (h.hotelName LIKE %s OR r.roomType LIKE %s)"
                params.append(f"%{search}%")
                params.append(f"%{search}%")

            if status_filter:
                query += " AND b.status = %s"
                params.append(status_filter)

            if checkin_from:
                query += " AND b.checkIn >= %s"
                params.append(checkin_from)
            
            if checkin_to:
                query += "AND b.checkIn <= %s"
                params.append(checkin_to)
            
            if checkout_from:
                query += " AND b.checkOut >= %s"
                params.append(checkout_from)
            
            if checkout_to:
                query += "AND b.checkOut <= %s"
                params.append(checkout_to)            
                
            if hotelId:
                query += "AND h.hotelId = %s"
                params.append(hotelId)
            with db.cursor() as cursor:
                cursor.execute(query, params)
                bookings = cursor.fetchall()
            return bookings
        except pymysql.MySQLError as e:
            print("数据库错误：", e) 
            
    @staticmethod
    def fetchBooking(bookingId):
        try:
            with db.cursor() as cursor:
                cursor.execute("SELECT * FROM Booking WHERE bookingId=%s;", (bookingId,))
                booking = cursor.fetchone()
            return booking
        except pymysql.MySQLError as e:
            print("数据库错误：", e) 
            
    def updateStatus(bookingId, status):
        try:
            with db.cursor() as cursor:
                cursor.execute("UPDATE Booking SET status=%s WHERE bookingID=%s", (status, bookingId))
                if status == "checkOut":
                    cursor.execute("""
                                   UPDATE Room
                                   SET available = LEAST(totalNum, available + 1)
                                   WHERE roomId IN (SELECT roomId FROM Booking WHERE bookingId=%s);
                                   """, (bookingId,))
                db.commit()
        except pymysql.MySQLError as e:
            print("数据库错误：", e)         