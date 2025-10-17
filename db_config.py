# -*- coding: utf-8 -*-

# db_config.py
import pymysql# -*- coding: utf-8 -*-

# db_config.py
import pymysql

def get_connection():
    return pymysql.connect(
        host='localhost',
        user='root',             # ← 네 MySQL 사용
        password='1234',       # ← 네 MySQL 비밀번호
        db='apartment',          # ← 사용할 데이터
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

def get_connection():
    return pymysql.connect(
        host='localhost',
        user='root',             # ← 네 MySQL 사용
        password='1234',       # ← 네 MySQL 비밀번호
        db='apartment',          # ← 사용할 데이터
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )