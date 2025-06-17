import pymysql
from db import db

class Room:
    @staticmethod
    def fetchAllRooms(hotelId):
        try:
            with db.cursor() as cursor:
                cursor.execute("SELECT * FROM Room WHERE hotelId=%s;", (hotelId,))
                rooms = cursor.fetchall()
            return rooms
        except pymysql.MySQLError as e:
            print("数据库错误：", e) 
            
    @staticmethod
    def fetchRoomsWithKeyword(hotelId, keyword):
        try:
            with db.cursor() as cursor:
                cursor.execute("SELECT * FROM Room WHERE hotelId=%s AND roomType LIKE %s;", (hotelId, f"%{keyword}%"))
                rooms = cursor.fetchall()
            return rooms
        except pymysql.MySQLError as e:
            print("数据库错误：", e) 
            
    @staticmethod
    def fetchRoom(roomId):
        try:
            with db.cursor() as cursor:
                cursor.execute("SELECT * FROM Room WHERE roomId=%s", (roomId,))
                room = cursor.fetchone()
            return room
        except pymysql.MySQLError as e:
            print("数据库错误：", e)             
    
    @staticmethod    
    def addRoom(hotelId, roomType, price, total, desc):
        try:
            with db.cursor() as cursor:
                cursor.execute("""
                               INSERT INTO Room (hotelId, roomType, price, totalNum, available, description)
                               VALUES (%s, %s, %s, %s, %s, %s);
                               """,(hotelId, roomType, price, total, total, desc))
                db.commit()
        except pymysql.MySQLError as e:
            print("数据库错误：", e)  
        
    @staticmethod   
    def editRoom(roomId, roomType, price, total, desc):
        try:
            with db.cursor() as cursor:
                cursor.execute("""
                               UPDATE Room 
                               SET roomType=%s, price=%s, totalNum=%s, available=%s, description=%s
                               WHERE roomId=%s;
                               """,(roomType, price, total, total, desc, roomId))
                db.commit()
        except pymysql.MySQLError as e:
            print("数据库错误：", e) 
            
    @staticmethod   
    def deleteRoom(roomId):
        try:
            with db.cursor() as cursor:
                cursor.execute("DELETE FROM Room WHERE roomId=%s;",(roomId,))
                db.commit()
        except pymysql.MySQLError as e:
            print("数据库错误：", e)