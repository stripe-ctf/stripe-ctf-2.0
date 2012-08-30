#!/usr/bin/env python
import hashlib
import json
import os
import random
import sqlite3
import string
import sys

def random_string(length=7):
    return ''.join(random.choice(string.ascii_lowercase) for x in range(length))

def main(basedir, level03, proof, plans):
    print 'Generating users.db'
    conn = sqlite3.connect(os.path.join(basedir, 'users.db'))
    cursor = conn.cursor()

    cursor.execute("DROP TABLE IF EXISTS users")
    cursor.execute("""
    CREATE TABLE users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username VARCHAR(255),
        password_hash VARCHAR(255),
        salt VARCHAR(255)
    );""")

    id = 1
    dict = {}

    list = [('bob', level03), ('eve', proof), ('mallory', plans)]
    random.shuffle(list)
    for username, secret in list:
        password = random_string()
        salt = random_string()
        password_hash = hashlib.sha256(password + salt).hexdigest()
        print '- Adding {0}'.format(username)
        cursor.execute("INSERT INTO users (username, password_hash, salt) VALUES (?, ?, ?)", (username, password_hash, salt))

        dict[id] = secret
        id += 1

    conn.commit()

    print 'Generating secrets.json'
    f = open(os.path.join(basedir, 'secrets.json'), 'w')
    json.dump(dict,
              f,
              indent=2)
    f.write('\n')

    print 'Generating entropy.dat'
    f = open(os.path.join(basedir, 'entropy.dat'), 'w')
    f.write(os.urandom(24))

if __name__ == '__main__':
    if not len(sys.argv) == 5:
        print 'Usage: %s <basedir> <level03> <proof> <plans>' % sys.argv[0]
        sys.exit(1)
    main(*sys.argv[1:])
