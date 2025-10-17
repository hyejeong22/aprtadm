<<<<<<< HEAD
import pymysql

def get_connection():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='너의비번',
        db='vaprt_db',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )
=======
import pymysql

def get_connection():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='너의비번',
        db='vaprt_db',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )
>>>>>>> 8da52f5 (Initial commit for V Apartment admin page)
