#!/usr/bin/env python  
# -*- coding:utf-8 -*- 

""" 
@version: v1.0 
@author: Harp
@contact: liutao25@baidu.com 
@software: PyCharm 
@file: validate.py 
@time: 2018/2/3 0003 23:54 
"""

import re
from flask_login import login_user
from models import Users

reg = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"


def validate_user(infos, _type):
    if _type == 'log':
        eml, psw, rem, *_ = infos
        if re.match(reg, eml) is None:
            return "邮箱格式不正确"
        if len(psw) < 6 or len(psw) > 18:
            return "请输入6～18位密码"
        user = Users.query.filter(Users.eml == eml).first()
        if user is not None and user.check_psw(psw):
            login_user(user, remember=rem)
            return "OK"
        return "用户名或密码错误"
    elif _type == 'reg':
        eml, psw1, psw2, *_ = infos
        if re.match(reg, eml) is None:
            return "邮箱格式不正确"
        if Users.query.filter(Users.eml == eml).first() is not None:
            return "邮箱已注册"
        if psw1 != psw2:
            return "两次密码不一致"
        if len(psw1) < 6 or len(psw1) > 18:
            return "请输入6～18位密码"
        return "OK"
    elif _type == 'eml':
        eml, *_ = infos
        if re.match(reg, eml) is None:
            return "邮箱格式不正确"
        user = Users.query.filter(Users.eml == eml).first()
        if user is None:
            return "用户不存在"
        return user.id
    elif _type == 'psw':
        psw1, psw2, *_ = infos
        if psw1 != psw2:
            return "两次密码不一致"
        if len(psw1) < 6 or len(psw1) > 18:
            return "请输入6～18位密码"
        return "OK"
    else:
        return "未知错误"


if __name__ == "__main__":
    pass
