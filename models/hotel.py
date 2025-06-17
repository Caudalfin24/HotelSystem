import pymysql
from db import db

class Hotel:
    @staticmethod
    def fetchOwnerHotels(ownerId):
        try:
            with db.cursor() as cursor:
                cursor.execute("SELECT * FROM Hotel WHERE ownerId=%s;", (ownerId,))
                hotels = cursor.fetchall()
            return hotels
        except pymysql.MySQLError as e:
            print("数据库错误：", e) 
    
    @staticmethod
    def fetchHotel(hotelId):
        try:
            with db.cursor() as cursor:
                cursor.execute("SELECT * FROM Hotel WHERE hotelId=%s;", (hotelId,))
                hotel = cursor.fetchone()
            return hotel
        except pymysql.MySQLError as e:
            print("数据库错误：", e)   

    @staticmethod
    def fetchAllHotels():
        try:
            with db.cursor() as cursor:
                cursor.execute("SELECT * FROM Hotel;", ())
                hotels = cursor.fetchall()
            return hotels
        except pymysql.MySQLError as e:
            print("数据库错误：", e) 
    
    @staticmethod
    def fetchHotelsWithCondition(search, city, ownerId=None):
        try:
            query = "SELECT * FROM Hotel WHERE 1=1"
            params = []

            if search:
                query += " AND hotelName LIKE %s"
                params.append(f"%{search}%")

            if city:
                query += " AND city = %s"
                params.append(city)

            if ownerId:
                query += " AND ownerId = %s"
                params.append(ownerId)
                
            with db.cursor() as cursor:
                cursor.execute(query, params)
                hotels = cursor.fetchall()

            return hotels

        except pymysql.MySQLError as e:
            print("数据库错误：", e)   
            
            
    @staticmethod
    def fetchAllCities():
        try:
            with db.cursor() as cursor:
                cursor.execute("""
                               SELECT DISTINCT city
                               FROM Hotel
                               ORDER BY city ASC
                               """)
                cities = cursor.fetchall()
            return cities
        except pymysql.MySQLError as e:
            print("数据库错误：", e)
                             
    @staticmethod
    def addHotel(hotelName, ownerId, city, address, hotelPhone, rating):
        try:
            with db.cursor() as cursor:
                cursor.execute("""
                               INSERT INTO Hotel (hotelName, ownerId, city, address, hotelPhone, rating)
                               VALUES (%s, %s, %s, %s, %s, %s);
                               """,(hotelName, ownerId, city, address, hotelPhone, rating))
                db.commit()
        except pymysql.MySQLError as e:
            print("数据库错误：", e)           
    
    @staticmethod
    def editHotel(hotelId, hotelName, city, address, hotelPhone, rating):
        try:
            with db.cursor() as cursor:
                cursor.execute("""
                               UPDATE Hotel 
                               SET hotelName=%s, city=%s, address=%s, hotelPhone=%s, rating=%s
                               WHERE hotelId=%s;
                               """,(hotelName, city, address, hotelPhone, rating, hotelId))
                db.commit()
        except pymysql.MySQLError as e:
            print("数据库错误：", e) 

    @staticmethod
    def deleteHotel(hotelId):
        try:
            with db.cursor() as cursor:
                cursor.execute("DELETE FROM Hotel WHERE hotelId=%s;", (hotelId,))
                db.commit()
        except pymysql.MySQLError as e:
            print("数据库错误：", e) 
            
    @staticmethod
    def deleteHotels(hotelIds):
        if not hotelIds:
            print("hotelIds 为空，未执行任何操作。")
            return 
        try:
            placeholders = ', '.join(['%s'] * len(hotelIds))
            print(placeholders)
            sql = f"DELETE FROM Hotel WHERE hotelId IN ({placeholders});"
            with db.cursor() as cursor:
                cursor.execute(sql, hotelIds)
                db.commit()
                print(f"成功删除 {cursor.rowcount} 条记录")
        except pymysql.MySQLError as e:
            print("数据库操作失败：", e)