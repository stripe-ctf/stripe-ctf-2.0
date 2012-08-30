#!/usr/bin/env python
#
# Welcome to the Secret Safe!
#
# - users/users.db stores authentication info with the schema:
#
# CREATE TABLE users (
#   id VARCHAR(255) PRIMARY KEY AUTOINCREMENT,
#   username VARCHAR(255),
#   password_hash VARCHAR(255),
#   salt VARCHAR(255)
# );
#
# - For extra security, the dictionary of secrets lives
#   data/secrets.json (so a compromise of the database won't
#   compromise the secrets themselves)

import flask
import hashlib
import json
import logging
import os
import sqlite3
import subprocess
import sys
from werkzeug import debug

# Generate test data when running locally
data_dir = os.path.join(os.path.dirname(__file__), 'data')
if not os.path.exists(data_dir):
    import generate_data
    os.mkdir(data_dir)
    generate_data.main(data_dir, 'dummy-password', 'dummy-proof', 'dummy-plans')

secrets = json.load(open(os.path.join(data_dir, 'secrets.json')))
index_html = open('index.html').read()
app = flask.Flask(__name__)

# Turn on backtraces, but turn off code execution (that'd be an easy level!)
app.config['PROPAGATE_EXCEPTIONS'] = True
app.wsgi_app = debug.DebuggedApplication(app.wsgi_app, evalex=False)

app.logger.addHandler(logging.StreamHandler(sys.stderr))
# use persistent entropy file for secret_key
app.secret_key = open(os.path.join(data_dir, 'entropy.dat')).read()

# Allow setting url_root if needed
try:
    from local_settings import url_root
except ImportError:
    pass

def absolute_url(path):
    return url_root + path

@app.route('/')
def index():
    try:
        user_id = flask.session['user_id']
    except KeyError:
        return index_html
    else:
        secret = secrets[str(user_id)]
        return (u'Welcome back! Your secret is: "{0}"'.format(secret) +
                u' (<a href="./logout">Log out</a>)\n')

@app.route('/logout')
def logout():
    flask.session.pop('user_id', None)
    return flask.redirect(absolute_url('/'))

@app.route('/login', methods=['POST'])
def login():
    username = flask.request.form.get('username')
    password = flask.request.form.get('password')

    if not username:
        return "Must provide username\n"

    if not password:
        return "Must provide password\n"

    conn = sqlite3.connect(os.path.join(data_dir, 'users.db'))
    cursor = conn.cursor()

    query = """SELECT id, password_hash, salt FROM users
               WHERE username = '{0}' LIMIT 1""".format(username)
    cursor.execute(query)

    res = cursor.fetchone()
    if not res:
        return "There's no such user {0}!\n".format(username)
    user_id, password_hash, salt = res

    calculated_hash = hashlib.sha256(password + salt)
    if calculated_hash.hexdigest() != password_hash:
        return "That's not the password for {0}!\n".format(username)

    flask.session['user_id'] = user_id
    return flask.redirect(absolute_url('/'))

if __name__ == '__main__':
    # In development: app.run(debug=True)
    app.run()
