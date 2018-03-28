#!/usr/bin/env python  
# -*- coding:utf-8 -*- 

""" 
@version: v1.0 
@author: Harp
@contact: liutao25@baidu.com 
@software: PyCharm 
@file: config.py.py 
@time: 2018/2/3 0003 20:18 
"""

SECRET_KEY = "*ya)j8a?@+22^da791)_Qj%aw3A3'"

DEBUG = True

HOST = "127.0.0.1"
PORT = "3306"
DB = "mytodo"
USER = "root"
PASS = "123456"  # Harp@1207MySQL
CHARSET = "utf8"
DB_URI = "mysql+pymysql://{}:{}@{}:{}/{}?charset={}".format(USER, PASS, HOST, PORT, DB, CHARSET)
SQLALCHEMY_DATABASE_URI = DB_URI

SQLALCHEMY_TRACK_MODIFICATIONS = False


MAIL_SERVER = 'smtp.sina.com'
MAIL_USERNAME = 'mytodovip@sina.com'
MAIL_PASSWORD = 'MyFlaskApp123'
MAIL_DEFAULT_SENDER = 'mytodovip@sina.com'


if __name__ == "__main__":
    print(SQLALCHEMY_DATABASE_URI)
