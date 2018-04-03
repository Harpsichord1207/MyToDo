# MyToDo - 我的待办
### You can now [visit website](https://mytodo.vip)


## 功能
- 记录待办事项，切换完成状态，分组等;
- 对待办事项搜索、排序等;
- 注册、登录、邮箱重置密码;

## 后端
- Python/Flask + MySQL
- Flask-Mail用于重置密码
- Flask-Login用于用户登录、验证相关
- 待办的增删查改通过Json API

## 前端
- Bootstrap + AngularJS
- 主页面大量依赖JS，做到了单页面应用


## 部署
- Linux + Nginx + Gunicorn + Supervisor
- 使用了https/SSL

