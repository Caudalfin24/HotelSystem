import pymysql
from db import db

class Customer:
    @staticmethod
    def fetchCustomer(customerId):
        try:
            with db.cursor() as cursor:
                cursor.execute("SELECT * FROM Customer WHERE customerId=%s;", (customerId,))
                customer = cursor.fetchone()
            return customer
        except pymysql.MySQLError as e:
            print("数据库错误：", e)    
 
    @staticmethod    
    def fetchCustomers(search, min_age, max_age, sex):
        try:
            query = "SELECT * FROM Customer WHERE 1=1"
            params = []

            if search:
                query += " AND customerName LIKE %s"
                params.append(f"%{search}%")

            if min_age:
                query += " AND age >= %s"
                params.append(min_age)

            if max_age:
                query += " AND age <= %s"
                params.append(max_age)
                
            if sex:
                query += " AND sex = %s"
                params.append(sex)                
            
            with db.cursor() as cursor:
                cursor.execute(query, params)
                customers = cursor.fetchall()

            return customers

        except pymysql.MySQLError as e:
            print("数据库错误：", e)   
                        
    @staticmethod
    def updateCustomer(customerId, customerName, email, customerPhone, age, sex):
        try:
            with db.cursor() as cursor:
                cursor.execute("""
                               UPDATE Customer
                               SET customerName=%s, email=%s, customerPhone=%s, age=%s, sex=%s
                               WHERE customerId=%s;
                               """, (customerName, email, customerPhone, age, sex, customerId))
                db.commit()
        except pymysql.MySQLError as e:
            print("数据库错误：", e)        