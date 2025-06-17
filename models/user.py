import pymysql
from db import db

class User:
    @staticmethod
    def fetchAllUsers():
        try:
            with db.cursor() as cursor:
                cursor.execute("SELECT * FROM User;")
                users = cursor.fetchall()
            return users
        except pymysql.MySQLError as e:
            print("数据库错误：", e)
            
    @staticmethod
    def fetchUser(userId):
        try:
            with db.cursor() as cursor:
                cursor.execute("SELECT * FROM User WHERE userId=%s;", (userId,))
                user = cursor.fetchone()
            return user
        except pymysql.MySQLError as e:
            print("数据库错误：", e)   

    @staticmethod
    def fetchUserWithUsername(username):
        try:
            with db.cursor() as cursor:
                cursor.execute("SELECT * FROM User WHERE username=%s;", (username,))
                user = cursor.fetchone()
            return user
        except pymysql.MySQLError as e:
            print("数据库错误：", e) 

    @staticmethod
    def fetchUserWithUsernameAndRole(username, role):
        try:
            with db.cursor() as cursor:
                cursor.execute("SELECT * FROM User WHERE username = %s AND role = %s", (username, role))
                user = cursor.fetchone()
            return user
        except pymysql.MySQLError as e:
            print("数据库错误：", e) 

    @staticmethod
    def addUser(username, password, role):
        try:
            with db.cursor() as cursor:
                cursor.execute("INSERT INTO User (username, password, role) VALUES (%s, %s, %s)",
                        (username, password, role))
                db.commit()
        except pymysql.MySQLError as e:
            print("数据库错误：", e) 

            
    @staticmethod
    def updatePassword(userId, password):
        try:
            with db.cursor() as cursor:
                cursor.execute("UPDATE User SET password=%s WHERE userId=%s", (password, userId))
                db.commit()
        except pymysql.MySQLError as e:
            print("数据库错误：", e)
                    
    @staticmethod
    def fetchUsersWithCondition(search):
        try:
            query = "SELECT * FROM User WHERE 1=1"
            params = []

            if search:
                query += " AND username LIKE %s"
                params.append(f"%{search}%")


            with db.cursor() as cursor:
                cursor.execute(query, params)
                users = cursor.fetchall()
                
            return users

        except pymysql.MySQLError as e:
            print("数据库错误：", e)   

    @staticmethod
    def deleteUser(userId):
        try:
            with db.cursor() as cursor:
                cursor.execute("DELETE FROM User WHERE userId = %s;", (userId, ))
                db.commit()
                print(f"成功删除 userID 为 {userId} 的用户。")
        except pymysql.MySQLError as e:
            print("数据库错误：", e)
    

    @staticmethod
    def deleteUsers(userIds):
        if not userIds:
            print("userIds 为空，未执行任何操作。")
            return 
        try:
            placeholders = ', '.join(['%s'] * len(userIds))
            print(placeholders)
            sql = f"DELETE FROM User WHERE userId IN ({placeholders});"
            with db.cursor() as cursor:
                cursor.execute(sql, userIds)
                db.commit()
                print(f"成功删除 {cursor.rowcount} 条记录")
        except pymysql.MySQLError as e:
            print("数据库操作失败：", e)
                        
            