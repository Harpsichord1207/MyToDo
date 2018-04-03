import config
from flask import Flask, render_template, flash
from flask import request, send_file, redirect, url_for
from flask_login import LoginManager, login_required, current_user, logout_user
from flask_mail import Mail, Message
from utils.validate import validate_user
from models import db
from models import get_user, add_user, reset_psw
from models import get_todo, add_todo, edit_todo, delete_todo
from models import get_category, add_category, edit_category, delete_category
from models import generate_token, verify_token
from json import loads
from threading import Thread


app = Flask(__name__)
app.config.from_object(config)
login_manager = LoginManager()
login_manager.init_app(app)
db.init_app(app)
mail = Mail(app)

# login_manager.session_protection = 'strong'
login_manager.login_view = 'page_login'
login_manager.login_message = '请先登录'


@login_manager.user_loader
def load_user(user_id):
    return get_user(user_id)


@app.route('/favicon.ico')
def favicon():
    return send_file('static/images/favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.route('/')
def page_home():
    if current_user.is_authenticated:
        # print("当前用户", current_user.eml)
        return redirect(url_for('page_task'))
    return render_template('home.html')


@app.route('/register/', methods=['GET', 'POST'])
def page_register():
    if current_user.is_authenticated:
        return redirect(url_for('page_task'))
    if request.method == 'POST':
        eml = request.form.get('eml')
        psw1 = request.form.get('psw1')
        psw2 = request.form.get('psw2')
        result = validate_user([eml, psw1, psw2], 'reg')
        flash(result)
        if result == 'OK':
            add_user(eml, psw1)
            return redirect(url_for('page_login'))
    return render_template('register.html')


@app.route('/login/', methods=['GET', 'POST'])
def page_login():
    if current_user.is_authenticated:
        return redirect(url_for('page_task'))
    if request.method == 'POST':
        rem = True if request.form.get('rem') else False
        eml = request.form.get('eml')
        psw = request.form.get('psw')
        result = validate_user([eml, psw, rem], 'log')
        if result == 'OK':
            return redirect(url_for('page_task'))
        flash(result)
    return render_template('login.html')


@app.route('/security/', methods=['GET'])
def page_security():
    if current_user.is_authenticated:
        return redirect(url_for('page_task'))
    if request.method == 'GET':
        return render_template('security.html')


@app.route('/mail/', methods=['POST'])
def send_mail():
    def send_async_mail(m):
        with app.app_context():
            mail.send(m)
    eml = request.form.get('eml')
    validate_result = validate_user([eml], 'eml')
    if isinstance(validate_result, int):
        token_string = generate_token(validate_result)
        if token_string is None:
            return render_template('tip.html', tip='已达到当天重置次数上限或存在未失效的重置链接', target='page_security')
        msg = Message('【重要】MyToDo重置密码', recipients=[eml])
        msg.html = '重置链接：http://127.0.0.1:5000/reset?token=' + token_string
        Thread(target=send_async_mail, args=[msg]).start()
        return render_template('tip.html', tip='重置链接已发送到您的邮箱', target='page_home')
    flash(validate_result)
    return redirect(url_for('page_security'))


@app.route('/reset', methods=['GET', 'POST'])
def page_reset():
    if request.method == 'GET':
        token_string = request.args.get('token')
        result = verify_token(token_string, False)
        if result:
            return render_template('reset.html', ts=token_string, eml=result)
        return render_template('tip.html', tip='无效的链接', target='page_security')
    else:
        psw1 = request.form.get('psw1')
        psw2 = request.form.get('psw2')
        v_psw = validate_user([psw1, psw2], 'psw')
        token_string = request.form.get('ts')
        if v_psw != "OK":
            flash(v_psw)
            return redirect('/reset?token='+token_string)
        else:
            result = verify_token(token_string, True)
            if result:
                reset_psw(result, psw1)
                return render_template('tip.html', tip='密码已重置', target='page_login')
        return render_template('tip.html', tip='已失效', target='page_security')


@app.route('/logout/')
def page_logout():
    logout_user()
    return redirect(url_for('page_login'))


@app.route('/todo/')
@login_required
def page_task():
    return render_template('mytodo.html')


@app.route('/todo/get/', methods=['GET'])
@login_required
def api_get_todo():
    page = int(request.args.get('page', 1))
    sort_type = request.args.get('sort_type', 'time_desc')
    category_id = request.args.get('category_id')
    kw = request.args.get('kw')
    return get_todo(current_user.id, page, sort_type, category_id, kw)


@app.route('/category/get/', methods=['GET'])
@login_required
def api_get_category():
    return get_category(current_user)


@app.route('/todo/add/', methods=['POST'])
@login_required
def api_add_todo():
    form_data = loads(request.get_data().decode('utf-8'))
    category_id = int(form_data.get('category_id'))
    content = form_data.get('content')
    result = add_todo(current_user.id, category_id, content)
    if result is not None:
        return "", 200


@app.route('/category/add/', methods=['POST'])
@login_required
def api_add_category():
    return add_category(current_user.id)


@app.route('/todo/edit/', methods=['POST'])
@login_required
def api_edit_todo():
    form_data = loads(request.get_data().decode('utf-8'))
    todo_id = form_data.get('todo_id')
    status = form_data.get('status')
    content = form_data.get('content')
    remark = form_data.get('remark')
    response = edit_todo(current_user.id, todo_id, status, content, remark)
    if response:
        return response


@app.route('/category/edit/', methods=['POST'])
@login_required
def api_edit_category():
    form_data = loads(request.get_data().decode('utf-8'))
    category_id = form_data.get('category_id')
    name = form_data.get('name')
    response = edit_category(current_user.id, category_id, name)
    if response:
        return "", 200


@app.route('/todo/delete/', methods=['POST'])
@login_required
def api_delete_todo():
    form_data = loads(request.get_data().decode('utf-8'))
    todo_id = form_data.get('todo_id')
    if delete_todo(current_user.id, todo_id):
        return "", 200


@app.route('/category/delete/', methods=['POST'])
@login_required
def api_delete_category():
    form_data = loads(request.get_data().decode('utf-8'))
    category_id = form_data.get('category_id')
    if delete_category(current_user.id, category_id):
        return "", 200


if __name__ == '__main__':
    app.run()
