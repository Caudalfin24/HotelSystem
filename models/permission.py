import pymysql
from db import db

class Permission:
    @staticmethod
    def fetchAllPermissions():
        try:
            with db.cursor() as cursor:
                cursor.execute("SELECT * FROM Permission;")
                permissions = cursor.fetchall()
            return permissions
        except pymysql.MySQLError as e:
            print("数据库错误：", e)        
            
            
class UserPermission:
    @staticmethod   
    def fetchUserPermissions(userId):
        try:
            with db.cursor() as cursor:
                cursor.execute("""
                                SELECT * FROM Permission 
                                WHERE permissionId IN (
                                    SELECT permissionId FROM UserPermission
                                    WHERE userId = %s
                                );
                               """, (userId, ))
                permissions = cursor.fetchall()
            return permissions
        except pymysql.MySQLError as e:
            print("数据库错误：", e)
    
    @staticmethod
    def addPermission(userId, permissionId):
        try:
            with db.cursor() as cursor:
                print(userId, permissionId)
                cursor.execute("INSERT INTO UserPermission (userId, permissionId) VALUES (%s, %s);", (userId, permissionId))
                db.commit()
                return "权限添加成功"
        except pymysql.err.IntegrityError:
            return "该权限已存在"
        except pymysql.MySQLError as e:
            print("数据库错误：", e)
            
    @staticmethod
    def deletePermission(userId, permissionId):
        try:
            with db.cursor() as cursor:
                cursor.execute("DELETE FROM UserPermission WHERE userId = %s and permissionId = %s;", (userId, permissionId))
                db.commit()
        except pymysql.MySQLError as e:
            print("数据库错误：", e)