# -*- coding: utf-8 -*-

import functools
import json

from flask import Flask, Response, request

import db

app = Flask(__name__)
app.secret_key = b'Xc-Z3NG@kw*PWAkN5m3!Km6evYnjTEy]sctMQ=eDsUv139.Ghd4*=6~=WYTVQUN.'

dbm = db.DBManager()


def response(func):
    @functools.wraps(func)
    def response_wrapper(*args, **kwds):
        code, data = func(*args, **kwds)
        if code == 200:
            json_text = json.dumps({'response': data})
        else:
            json_text = json.dumps({'error': {
                'error_code': code,
                'error_msg': data
            }})
        return Response(status=code, mimetype='application/json', response=json_text)
    return response_wrapper


def check_token(token):
    if not token:
        return (403, 'Permission denied!')
    code, text = dbm.check_token(token)
    return (code, text)


@app.route('/')
@response
def main():
    return 200, {}


# Users


@app.route('/auth')
@response
def auth():
    args = request.args
    try:
        result = dbm.authorization(args['email'], args['pwd'])
    except KeyError:
        return 400, 'Invalid request!'
    return result


@app.route('/add_user')
@response
def add_users():
    check = check_token(request.args.get('token'))
    if 403 in check:
        return check
    # Params
    args = request.args
    try:
        name = args['surname'], args['name'], args['patronymic']
        user_data = {'email': args['email'], 'pwd': args['pwd'], 'name': name, 'position': args['position']}
    except KeyError:
        return 400, 'Invalid request!'
    return dbm.add_user(user_data)


@app.route('/del_user')
@response
def del_users():
    check = check_token(request.args.get('token'))
    if 403 in check:
        return check
    # Params
    email = request.args.get('email')
    return dbm.del_user(email)


@app.route('/edit_user')
@response
def edit_users():
    token = request.args.get('token')
    check = check_token(token)
    if 403 in check:
        return check
    # Params
    get = request.args.get
    email = get('email')
    pwd = get('pwd')
    name = [get('surname'), get('name'), get('patronymic')]
    position = get('position')
    if None in (email, pwd, *name, position):
        return 400, 'Invalid request!'
    userdata = {'email': email, 'pwd': pwd, 'name': name, 'position': position}
    return dbm.edit_user(userdata)


@app.route('/get_all_users')
@response
def get_all_users():
    token = request.args.get('token')
    check = check_token(token)
    if 403 in check:
        return check
    return dbm.get_all_users()


# Projects


@app.route('/add_project')
@response
def add_project():
    check = check_token(request.args.get('token'))
    if 403 in check:
        return check
    # Params
    args = request.args
    try:
        project_data = {'name': args['name'], 'deadline': args['deadline']}
    except KeyError:
        return 400, 'Invalid request!'
    return dbm.add_project(project_data)


@app.route('/del_project')
@response
def del_project():
    check = check_token(request.args.get('token'))
    if 403 in check:
        return check
    # Params
    args = request.args
    try:
        name = args['name']
    except KeyError:
        return 400, 'Invalid request!'
    return dbm.del_project(name)


@app.route('/edit_project')
@response
def edit_project():
    check = check_token(request.args.get('token'))
    if 403 in check:
        return check
    # Params
    args = request.args
    try:
        project_data = {'name': args['name'], 'deadline': args['deadline']}
    except KeyError:
        return 400, 'Invalid request!'
    return dbm.edit_project(project_data)


@app.route('/get_all_projects')
@response
def get_all_projects():
    check = check_token(request.args.get('token'))
    if 403 in check:
        return check
    return dbm.get_all_projects()


if __name__ == "__main__":
    app.run(host='0.0.0.0')
