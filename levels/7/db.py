import os
import sqlite3
import sys

class NotFound(Exception):
    pass
class ManyFound(Exception):
    pass

# for app.secret_key
def rewrite_entropy_file(path):
    f = open(path, 'w')
    f.write(os.urandom(24))
    f.close()

class DB(object):
    def __init__(self, database):
        self.conn = sqlite3.connect(database,
                                    detect_types=sqlite3.PARSE_DECLTYPES)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        self.debug = False

    def log(self, *args):
        if self.debug:
            for i in args:
                sys.stderr.write(str(i))
            sys.stderr.write('\n')

    def commit(self):
        self.conn.commit()

    def close(self):
        self.cursor.close()
        self.conn.close()

    def select(self, table, where=None):
        if where is None:
            where = {}
        self.do_select(table, where)
        return map(dict, self.cursor.fetchall())

    def select_one(self, table, where=None):
        where = where or {}
        self.do_select(table, where)

        row = self.cursor.fetchone()
        if row is None:
            raise NotFound

        if self.cursor.fetchone() is not None:
            raise ManyFound

        return dict(row)

    def do_select(self, table, where=None):
        where = where or {}
        where_clause = ' AND '.join('%s=?' % key for key in where.iterkeys())
        values = where.values()
        q = 'select * from ' + str(table)
        if where_clause:
            q += ' where ' + where_clause
        self.log(q, '<==', values)
        self.cursor.execute(q, values)

    def insert(self, table, data):
        cols = ', '.join(data.keys())
        vals = data.values()
        placeholders = ', '.join('?' for i in data)
        q = 'insert into %s (%s) values (%s)' % (table, cols, placeholders)
        self.log(q, '<==', vals)
        self.cursor.execute(q, vals)
        self.commit()
        return self.cursor.rowcount
