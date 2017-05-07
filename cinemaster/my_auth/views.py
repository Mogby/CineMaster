from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse

import sqlite3
import datetime
import hashlib


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


def end_session(request):
    if 'auth_token' in request.COOKIES:
        end_session_by_token(request.COOKIES['auth_token'])
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def add_user(request):
    error_messages = []

    login = request.POST['login']
    display_name = request.POST['display-name']
    password = request.POST['password']

    if password != request.POST['double-check-password']:
        error_messages.append('Пароли не совпадают')

    with connect() as con:
        result = con.execute('SELECT user_id FROM users WHERE login = ?', (login, )).fetchone()

        if result:
            error_messages.append('Пользователь с таким логином уже существует')
        elif not error_messages:
            result = con.execute('SELECT max(user_id) as prev_id FROM users').fetchone()

            con.execute('INSERT INTO users VALUES (?, ?, ?, ?)',
                        (result['prev_id'] + 1, get_hash(password), display_name, login))
            con.commit()

    if error_messages:
        return render(request, 'my_auth/register.html', {'error_messages':error_messages})
    else:
        return HttpResponseRedirect(reverse('movies:index'))


def register(request):
    return render(request, 'my_auth/register.html', {'error_messages':[]})


def update_auth_token(user):
    end_expired_sessions()
    with connect() as con:
        con.execute('DELETE FROM auth_tokens WHERE user_id = ?', (user['user_id'],))
        con.commit()

    new_token = get_hash(user['login'], user['password'], datetime.datetime.now())

    with connect() as con:
        con.execute('INSERT INTO auth_tokens VALUES (?, ?, ?)',
                    (user['user_id'], new_token, datetime.datetime.now() + datetime.timedelta(days=30)))
        con.commit()

    return new_token


def login(request):
    end_session(request)
    login = request.POST['login']
    password = request.POST['password']

    with connect() as con:
        user = con.execute('SELECT * FROM users WHERE login = ?', (login,)).fetchone()

    if not user or get_hash(password) != user['password']:
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    response = HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    response.set_cookie('display_name', user['display_name'],
                        max_age=datetime.timedelta(days=30).total_seconds())
    response.set_cookie('user_id', str(user['user_id']),
                        max_age=datetime.timedelta(days=30).total_seconds())
    response.set_cookie('auth_token', str(update_auth_token(user)),
                        max_age=datetime.timedelta(days=30).total_seconds())

    return response


def logout(request):
    end_session(request)

    response = HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    response.delete_cookie('display_name')
    response.delete_cookie('user_id')
    response.delete_cookie('auth_token')

    return response