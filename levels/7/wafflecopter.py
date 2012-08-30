#!/usr/bin/env python
import hashlib
import json
import logging
import os
import sys
import urllib
from functools import wraps

import bcrypt
import sqlite3
from flask import Flask, session, request, redirect, render_template, g, abort
from flask import make_response

import db
import settings

app = Flask(__name__)
app.config.from_object(settings)
app.logger.addHandler(logging.StreamHandler(sys.stderr))


if not os.path.exists(settings.entropy_file):
    print 'Entropy file not found. Have you run initialize_db.py?'

# use persistent entropy file for secret_key
app.secret_key = open(settings.entropy_file, 'r').read()

class BadSignature(Exception):
    pass
class BadRequest(Exception):
    pass

def valid_user(user, passwd):
    try:
        row = g.db.select_one('users', {'name': user})
    except db.NotFound:
        print 'Invalid user', repr(user)
        return False
    if bcrypt.hashpw(passwd, row['password']) == row['password']:
        print 'Valid user:', repr(user)
        return row
    else:
        print 'Invalid password for', repr(user)
        return False

def log_in(user, row):
    session['user'] = row
    session['username'] = user

def absolute_url(path):
    return settings.url_root + path

def require_authentication(func):
    @wraps(func)
    def newfunc(*args, **kwargs):
        if 'user' not in session:
            return redirect(absolute_url('/login'))
        return func(*args, **kwargs)
    return newfunc

def json_response(obj, status_code=200):
    text = json.dumps(obj) + '\n'
    resp = make_response(text, status_code)
    resp.headers['content-type'] = 'application/json'
    return resp

def json_error(message, status_code):
    return json_response({'error': message}, status_code)

def log_api_request(user_id, path, body):
    if isinstance(body, str):
        # body is a string byte stream, but sqlite will think it's utf-8
        # convert each character to unicode so it's unambiguous
        body = ''.join(unichr(ord(c)) for c in body)
    g.db.insert('logs', {'user_id': user_id, 'path': path, 'body': body})

def get_logs(user_id):
    return g.db.select('logs', {'user_id': user_id})

def get_waffles():
    return g.db.select('waffles')

@app.before_request
def before_request():
    g.db = db.DB(settings.database)
    g.cursor = g.db.cursor

@app.teardown_request
def teardown_request(exception):
    if hasattr(g, 'db'):
        g.db.commit()
        g.db.close()

@app.route('/')
@require_authentication
def index():
    user = session['user']
    waffles = get_waffles()
    return render_template('index.html', user=user, waffles=waffles,
                           endpoint=request.url_root)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        user = request.form['username']
        password = request.form['password']
        row = valid_user(user, password)
        if row:
            log_in(user, row)
            return redirect(absolute_url('/'))
        else:
            error = 'Invalid username or password'

    return render_template('login.html', error=error)

@app.route('/logs/<int:id>')
@require_authentication
def logs(id):
    rows = get_logs(id)
    return render_template('logs.html', logs=rows)

def verify_signature(user_id, sig, raw_params):
    # get secret token for user_id
    try:
        row = g.db.select_one('users', {'id': user_id})
    except db.NotFound:
        raise BadSignature('no such user_id')
    secret = str(row['secret'])

    h = hashlib.sha1()
    h.update(secret + raw_params)
    print 'computed signature', h.hexdigest(), 'for body', repr(raw_params)
    if h.hexdigest() != sig:
        raise BadSignature('signature does not match')
    return True

def parse_params(raw_params):
    pairs = raw_params.split('&')
    params = {}
    for pair in pairs:
        key, val = pair.split('=')
        key = urllib.unquote_plus(key)
        val = urllib.unquote_plus(val)
        params[key] = val
    return params

def parse_post_body(body):
    try:
        raw_params, sig = body.strip('\n').rsplit('|sig:', 1)
    except ValueError:
        raise BadRequest('Request must be of form params|sig:da39a3ee5e6b...')

    return raw_params, sig

def process_order(params):
    user = g.db.select_one('users', {'id': params['user_id']})

    # collect query parameters
    try:
        waffle_name = params['waffle']
    except KeyError:
        return json_error('must specify waffle', 400)
    try:
        count = int(params['count'])
    except (KeyError, ValueError):
        return json_error('must specify count', 400)
    try:
        lat, long = float(params['lat']), float(params['long'])
    except (KeyError, ValueError):
        return json_error('where would you like your waffle today?', 400)

    if count < 1:
        return json_error('count must be >= 1', 400)

    # get waffle info
    try:
        waffle = g.db.select_one('waffles', {'name': waffle_name})
    except db.NotFound:
        return json_error('no such waffle: %s' % waffle_name, 404)

    # check premium status
    if waffle['premium'] and not user['premium']:
        return json_error('that waffle requires a premium subscription', 402)

    # return results
    plural = 's' if count > 1 else ''
    msg = 'Great news: %d %s waffle%s will soon be flying your way!' \
        % (count, waffle_name, plural)
    return json_response({'success': True, 'message': msg,
                          'confirm_code': waffle['confirm']})

@app.route('/orders', methods=['POST'])
def order():
    # We need the original POST body in order to check the hash, so we use
    # request.input_stream rather than request.form.
    request.shallow = True
    body = request.input_stream.read(
        request.headers.get('content-length', type=int) or 0)

    # parse POST body
    try:
        raw_params, sig = parse_post_body(body)
    except BadRequest, e:
        print 'failed to parse', repr(body)
        return json_error(e.message, 400)

    print 'raw_params:', repr(raw_params)

    try:
        params = parse_params(raw_params)
    except ValueError:
        raise BadRequest('Could not parse params')

    print 'sig:', repr(sig)

    # look for user_id and signature
    try:
        user_id = params['user_id']
    except KeyError:
        print 'user_id not provided'
        return json_error('must provide user_id', 401)

    # check that signature matches
    try:
        verify_signature(user_id, sig, raw_params)
    except BadSignature, e:
        return json_error('signature check failed: ' + e.message, 401)

    # all OK -- process the order
    log_api_request(params['user_id'], '/orders', body)
    return process_order(params)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9233)

