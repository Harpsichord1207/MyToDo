#!/usr/bin/env python  
# -*- coding:utf-8 -*- 

""" 
@version: v1.0 
@author: Harp
@contact: liutao25@baidu.com 
@software: PyCharm 
@file: users.py 
@time: 2018/2/4 0004 9:59 
"""

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime, timedelta
from json import dumps
from werkzeug.security import generate_password_hash, check_password_hash
from config import SECRET_KEY
from utils.normalize import orm_normalize

db = SQLAlchemy()


class Users(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    eml = db.Column(db.String(64), nullable=False)
    psw = db.Column(db.String(128), nullable=False)
    register_time = db.Column(db.DateTime, nullable=False, default=datetime.now)

    def __init__(self, eml, psw):
        hashed_psw = generate_password_hash(SECRET_KEY+psw)
        self.eml = eml
        self.psw = hashed_psw

    def check_psw(self, psw):
        return check_password_hash(self.psw, SECRET_KEY+psw)

    def set_psw(self, psw):
        self.psw = generate_password_hash(SECRET_KEY+psw)


class Todos(db.Model):
    __tablename__ = 'todos'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    content = db.Column(db.String(256), nullable=False)
    create_time = db.Column(db.DateTime, nullable=False, default=datetime.now)
    status = db.Column(db.Boolean, nullable=False, default=False)
    deleted = db.Column(db.Integer, nullable=False, default=0)
    remark = db.Column(db.Text, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)

    user = db.relationship('Users', backref=db.backref('todos', order_by=create_time.desc()))
    category = db.relationship('Categories', backref=db.backref('todos', order_by=create_time.desc()))


class Categories(db.Model):
    __table__name = 'categories'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(32), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    create_time = db.Column(db.DateTime, nullable=False, default=datetime.now)
    deleted = db.Column(db.Integer, nullable=False, default=0)
    total_todo = db.Column(db.Integer, nullable=False, default=0)
    completed_todo = db.Column(db.Integer, nullable=False, default=0)

    user = db.relationship('Users', backref=db.backref('categories', order_by=id.desc()))


class Tokens(db.Model):
    __tablename__ = 'tokens'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, nullable=False)
    token_string = db.Column(db.String(100), nullable=False)
    create_time = db.Column(db.DateTime, nullable=False, default=datetime.now)
    expire_time = db.Column(db.DateTime, nullable=False)


# functions of User
def get_user(user_id):      # Get a user object by id
    return Users.query.filter(Users.id == user_id).first()


def add_user(eml, psw):     # Add a user with verified eml
    new_user = Users(eml=eml, psw=psw)
    db.session.add(new_user)
    db.session.commit()
    new_category = Categories(name="我的待办", user_id=new_user.id)     # Mixed with Category
    db.session.add(new_category)
    db.session.commit()
    return True


def reset_psw(eml, psw):    # Reset psw of a user
    user = Users.query.filter(Users.eml == eml).first()
    user.set_psw(psw)
    db.session.commit()
    return True


# functions of Task
def get_todo(user_id, page, sort_type, category_id, kw):
    todos = None
    n = None
    if kw is None:
        todos_query = Todos.query.filter(Todos.category_id == category_id, Todos.user_id == user_id, Todos.deleted == 0)
    else:
        todos_query = Todos.query.filter(Todos.content.contains(kw), Todos.user_id == user_id, Todos.deleted == 0)
        n = len(todos_query.all())
    if sort_type == 'time_asc':
        todos = todos_query.order_by(Todos.create_time).limit(15).offset((page-1)*15)
    elif sort_type == 'time_desc':
        todos = todos_query.order_by(Todos.create_time.desc()).limit(15).offset((page - 1) * 15)
    elif sort_type == 'complete_asc':
        todos = todos_query.order_by(Todos.status, Todos.create_time.desc()).limit(15).offset((page - 1) * 15)
    elif sort_type == 'complete_desc':
        todos = todos_query.order_by(Todos.status.desc(), Todos.create_time.desc()).limit(15).offset((page - 1) * 15)
    result = orm_normalize(todos, 'todo')
    if n is not None:
        result = {
            'todos_list': result,
            'total_result': n
        }
    return dumps(result, ensure_ascii=False)


def add_todo(user_id, category_id, content):
    category = None
    if len(content) > 0:
        category = Categories.query.filter(Categories.id == category_id, Categories.user_id == user_id).first()
    if category:
        todo = Todos(content=content, remark=content, user_id=user_id, category_id=category_id)
        db.session.add(todo)
        category.total_todo += 1
        db.session.commit()
        return True


def edit_todo(user_id, todo_id, status=None, content=None, remark=None):
    todo = Todos.query.filter(Todos.id == todo_id, Todos.user_id == user_id, Todos.deleted == 0).first()
    if todo:
        if status is not None:
            category = todo.category
            if todo.status:
                todo.status = False
                category.completed_todo -= 1
            else:
                todo.status = True
                category.completed_todo += 1
        if content is not None:
            todo.content = content
        if remark is not None:
            todo.remark = remark
        db.session.commit()
        return dumps({'status': todo.status}, ensure_ascii=False)


def delete_todo(user_id, todo_id):
    todo = Todos.query.filter(Todos.id == todo_id, Todos.user_id == user_id).first()
    if todo:
        todo.deleted = 1
        todo.category.total_todo -= 1
        if todo.status:
            todo.category.completed_todo -= 1
        db.session.commit()
        return True


# functions of Category
def get_category(user):
    categories = Categories.query.filter(Categories.user_id == user.id, Categories.deleted == 0).\
        order_by(Categories.create_time, Categories.id).all()
    return dumps(orm_normalize(categories, 'category'), ensure_ascii=False)


def add_category(user_id):
    if len(Categories.query.filter(Categories.user_id == user_id, Categories.deleted == 0).all()) < 10:
        category = Categories(user_id=user_id, name="我的清单")
        db.session.add(category)
        db.session.commit()
        return dumps({'id': category.id}, ensure_ascii=False)


def edit_category(user_id, category_id, name):
    category = Categories.query.filter(Categories.id == category_id,
                                       Categories.user_id == user_id, Categories.deleted == 0).first()
    if category:
        category.name = name
        db.session.commit()
        return True


def delete_category(user_id, category_id):
    category = Categories.query.filter(Categories.id == category_id, Categories.user_id == user_id).first()
    if category and len(Categories.query.filter(Categories.deleted == 0, Categories.user_id == user_id).all()) > 1:
        category.deleted = 1
        for todo in category.todos:
            todo.deleted = 1
        db.session.commit()
        return True


# functions of Token
def generate_token(user_id):
    current_time = datetime.now()
    c = 0
    for t in Tokens.query.filter(Tokens.user_id == user_id,
                                 db.cast(Tokens.create_time, db.DATE) == db.cast(current_time, db.DATE)).all():
        c += 1
        if t.expire_time > current_time or c >= 3:
            return None
    expire_time = current_time + timedelta(minutes=10)
    token = Tokens(user_id=user_id,
                   token_string=generate_password_hash(SECRET_KEY+str(user_id)+str(current_time))[20:],
                   create_time=current_time,
                   expire_time=expire_time)
    db.session.add(token)
    db.session.commit()
    return token.token_string


def verify_token(token_string, set_null=False):
    current_time = datetime.now()
    token = Tokens.query.filter(Tokens.token_string == token_string,
                                Tokens.expire_time >= current_time).first()
    if token:
        if set_null:
            token.expire_time = current_time
            db.session.commit()
            return Users.query.filter(Users.id == token.user_id).first().eml
        else:
            return Users.query.filter(Users.id == token.user_id).first().eml
    return None


if __name__ == "__main__":
    pass
