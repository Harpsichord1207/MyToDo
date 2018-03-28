#!/usr/bin/env python  
# -*- coding:utf-8 -*- 

""" 
@version: v1.0 
@author: Harp
@contact: liutao25@baidu.com 
@software: PyCharm 
@file: normalize.py 
@time: 2018/3/28 0028 23:36 
"""


def orm_normalize(data, orm_type):
    if hasattr(data, '__iter__'):
        return [_orm_to_dict(orm, orm_type) for orm in data]
    else:
        return _orm_to_dict(data, orm_type)


def _orm_to_dict(orm, orm_type):
    dic = {}
    if orm_type == 'todo':
        dic = {
            'id': orm.id,
            'content': orm.content,
            'create_time': str(orm.create_time),
            'status': orm.status,
            'remark': orm.remark,
            # 'user_id': orm.user_id,
            'category_id': orm.category_id
        }
    elif orm_type == 'category':
        todo_count = orm.total_todo
        if todo_count > 0 and todo_count % 15 == 0:
            page = todo_count // 15
        else:
            page = todo_count // 15 + 1
        dic = {
            'id': orm.id,
            'name': orm.name,
            'total_todo': todo_count,
            'completed_todo': orm.completed_todo,
            'page':  page
        }
    return dic


if __name__ == "__main__":
    pass
