import io
import json

from flask import url_for, render_template, session, Response, request, jsonify
from flask_login import login_user, login_required, logout_user
from flask_wtf import csrf
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import redirect

from apps import db, login_manager

from main import app
from apps.user.models import User


@app.route('/login', methods=['POST'])
def login():
    resp = {'result': 'success', 'status': 200, 'msg': 'success'}
    data = json.loads(request.data)
    email = data['email'] if 'email' in data else ''
    password = data['password'] if 'password' in data else ''
    remember = data['remember'] if 'remember' in data else ''
    checkcode = data['checkcode'] if 'checkcode' in data else ''

    if checkcode.upper() != session['valicode'].upper():
        resp['result'] = 'failed'
        resp['msg'] = "验证码不正确"
        resp['status'] = 401
        return jsonify(resp)

    user = User.query.filter_by(email=email).first()

    if user is None:
        resp['result'] = 'failed'
        resp['msg'] = "用户不存在"
        resp['status'] = 401
        return jsonify(resp)

    if not check_password_hash(user.password_hash, password):
        resp['result'] = 'failed'
        resp['msg'] = "密码错误"
        resp['status'] = 401
        return jsonify(resp)

    login_user(user, remember)

    return jsonify(resp)


@app.route('/register', methods=['POST'])
def register():
    resp = {'result': 'success', 'status': 200, 'msg': 'success'}
    data = json.loads(request.data)
    email = data['email'] if 'email' in data else ''
    password = data['password'] if 'password' in data else ''
    checkcode = data['checkcode'] if 'checkcode' in data else ''

    if checkcode.upper() != session['valicode'].upper():
        resp['result'] = 'failed'
        resp['msg'] = "验证码不正确"
        resp['status'] = 401
        return jsonify(resp)

    user = User.query.filter_by(email=email).first()
    if user:
        resp['result'] = 'failed'
        resp['msg'] = "邮箱已注册"
        resp['status'] = 401
        return jsonify(resp)

    new_user = User()
    new_user.email = email
    new_user.password_hash = generate_password_hash(password)
    db.session.add(new_user)
    db.session.commit()

    login_user(new_user, True)

    return jsonify(resp)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/edit')
@login_required
def edit():
    return render_template('account/edit.html')

@login_manager.unauthorized_handler
def unauthorized():

    return redirect(url_for('index'))

@app.route('/valicode')
def valicode():
    from libs.valicode import create_validate_code

    mstream = io.BytesIO()
    validate_code = create_validate_code()
    img = validate_code[0]
    img.save(mstream, "GIF")

    session['valicode'] = validate_code[1]
    return Response(response=mstream.getvalue(), status=200, mimetype='image/gif')

