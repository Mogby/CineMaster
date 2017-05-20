import sqlite3
import hashlib
import datetime

def get_hash(*args):
    hasher = hashlib.sha256()
    for arg in args:
        hasher.update(str(arg).encode('windows-1251'))
    return hasher.hexdigest()


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


def connect(default_factory = False):
    con = sqlite3.connect('database.sqlite3')
    if not default_factory:
        con.row_factory = dict_factory
    return con

def end_expired_sessions():
    with connect() as con:
        con.execute('DELETE FROM auth_tokens WHERE expiration_date <= ? ', (str(datetime.datetime.now()),))


def retrieve_auth_token(user_id):
    with connect() as con:
        result = con.execute('SELECT auth_token FROM auth_tokens WHERE user_id = ?', (user_id,))
        token = result.fetchone()
    return token


def end_session_by_token(auth_token):
    with connect() as con:
        con.execute('DELETE FROM auth_tokens WHERE token = ?;',
                    (auth_token,))
        con.commit()

def verify_token_belongs_to_user(auth_token, user_id):
    end_expired_sessions()
    with connect() as con:
        result = con.execute('SELECT user_id FROM auth_tokens WHERE token = ? AND user_id = ?',
                             (auth_token, user_id)).fetchall()
    return True if result else False
