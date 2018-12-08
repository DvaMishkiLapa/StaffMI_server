# -*- coding: utf-8 -*-

import functools
import json

from flask import Flask, Response, request
from jsonschema import FormatChecker, ValidationError, validate

import db

app = Flask(__name__)
app.secret_key = b'Xc-Z3NG@kw*PWAkN5m3!Km6evYnjTEy]sctMQ=eDsUv139.Ghd4*=6~=WYTVQUN.'
app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024

dbm = db.DBManager()

with open('schema.json', 'r') as f:
    json_schema = json.load(f)


def response_formatter(response):
    if isinstance(response, tuple): # TODO: Refactor this
        ok, content, code = response
        return {'ok': ok, 'content': content} if ok else {'ok': ok, 'content': content, 'error_code': code}
    result = []
    for r in response:
        ok, content, code = r
        result.append({'ok': ok, 'content': content} if ok else {'ok': ok, 'content': content, 'error_code': code})
    return result


def response(func):
    @functools.wraps(func)
    def response_wrapper(*args, **kwargs):
        response = func(*args, **kwargs)
        response_text = response_formatter(response)
        status = response_text.get('error_code', 0) or 200
        return Response(status=status, mimetype='application/json', response=json.dumps(response_text))
    return response_wrapper


def requests_handler(requests):
    result = [response_formatter(getattr(dbm, key)(requests[key])) for key in requests]
    return dict(zip(requests, result))


@app.route('/', methods=['GET'])
@response
def main_get():
    return False, 'Only POST requests are allowed!', 400


@app.route('/', methods=['POST'])
@response
def main_post():
    try:
        r = json.loads(request.data.decode())
    except json.decoder.JSONDecodeError:
        return False, 'Invalid JSON!', 400

    try:
        validate(r, json_schema, format_checker=FormatChecker())
    except ValidationError as e:
        return False, e.message, 400

    # TODO: Refactor this
    try:
        return True, requests_handler({'authorization': r['requests']['authorization']}), 200
    except KeyError:
        pass

    ok, text, code = dbm.check_token(r['token'])
    if not ok:
        return ok, text, code

    return True, requests_handler(r['requests']), 200


if __name__ == "__main__":
    app.run(host='0.0.0.0')
