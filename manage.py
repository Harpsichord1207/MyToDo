#!/usr/bin/env python  
# -*- coding:utf-8 -*- 

""" 
@version: v1.0 
@author: Harp
@contact: liutao25@baidu.com 
@software: PyCharm 
@file: manage.py 
@time: 2018/2/4 0004 10:21 
"""

from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from MyToDo import app, db
from models import Users, Todos, Categories, Tokens

manager = Manager(app)

migrate = Migrate(app, db)

manager.add_command('db', MigrateCommand)


if __name__ == '__main__':
    manager.run()
