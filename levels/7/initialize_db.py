#!/usr/bin/env python
import sys
from datetime import datetime
from random import SystemRandom

import bcrypt
import sqlite3

import client
import db
import settings

conn = db.DB(settings.database)
conn.debug = True
c = conn.cursor

db.rewrite_entropy_file(settings.entropy_file)

rand = SystemRandom()

def rand_choice(alphabet, length):
    return ''.join(rand.choice(alphabet) for i in range(length))

alphanum = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
def rand_alnum(length):
    return rand_choice(alphanum, length)

def main(level_password):
    create_tables()
    add_users()
    add_waffles(level_password)
    add_logs()

def add_users():
    add_user(1, 'larry', rand_alnum(16), 1)
    add_user(2, 'randall', rand_alnum(16), 1)
    add_user(3, 'alice', rand_alnum(16), 0)
    add_user(4, 'bob', rand_alnum(16), 0)
    add_user(5, 'ctf', 'password', 0)

def add_waffles(level_password):
    add_waffle('liege', 1, level_password)
    add_waffle('dream', 1, rand_alnum(14))
    add_waffle('veritaffle', 0, rand_alnum(14))
    add_waffle('chicken', 1, rand_alnum(14))
    add_waffle('belgian', 0, rand_alnum(14))
    add_waffle('brussels', 0, rand_alnum(14))
    add_waffle('eggo', 0, rand_alnum(14))

def add_logs():
    gen_log(1, '/orders', {'waffle': 'eggo', 'count': 10,
                           'lat': 37.351, 'long': -119.827})
    gen_log(1, '/orders', {'waffle': 'chicken', 'count': 2,
                           'lat': 37.351, 'long': -119.827})
    gen_log(2, '/orders', {'waffle': 'dream', 'count': 2,
                           'lat': 42.39561, 'long': -71.13051},
            date=datetime(2007, 9, 23, 14, 38, 00))
    gen_log(3, '/orders', {'waffle': 'veritaffle', 'count': 1,
                           'lat': 42.376, 'long': -71.116})

def create_tables():
    c.execute('drop table if exists users')
    c.execute('''
    CREATE TABLE users(
    id int not null primary key,
    name varchar(255) not null,
    password varchar(255) not null,
    premium int not null,
    secret varchar(255) not null,
    unique (name)
    )
    ''')

    c.execute('drop table if exists waffles')
    c.execute('''
    CREATE TABLE waffles(
    name varchar(255) not null primary key,
    premium int not null,
    confirm varchar(255) not null
    )
    ''')

    c.execute('drop table if exists logs')
    c.execute('''
    CREATE TABLE logs(
    user_id int not null,
    path varchar(255) not null,
    body text not null,
    date timestamp not null default current_timestamp
    )
    ''')
    c.execute('create index user_id on logs (user_id)')
    c.execute('create index date on logs (date)')

def add_user(uid, username, password, premium):
    hashed = bcrypt.hashpw(password, bcrypt.gensalt(10))
    secret = rand_alnum(14)
    data = {'id': uid, 'name': username, 'password': hashed,
            'premium': premium, 'secret': secret}
    conn.insert('users', data)

def get_user(uid):
    return conn.select_one('users', {'id': uid})

def add_waffle(name, premium, confirm):
    data = {'name': name, 'premium': premium, 'confirm': confirm}
    conn.insert('waffles', data)

def gen_log(user_id, path, params, date=None):
    user = get_user(user_id)

    # generate signature using client library
    cl = client.Client(None, user_id, user['secret'])
    body = cl._make_post(params)

    # prepare data for insert
    data = {'user_id': user_id, 'path': path, 'body': body}

    if date:
        data['date'] = date

    conn.insert('logs', data)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print 'usage: initialize_db.py LEVEL_PASSWORD'
        sys.exit(1)

    main(sys.argv[1])
