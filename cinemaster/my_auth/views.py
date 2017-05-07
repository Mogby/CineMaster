from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse

import sqlite3
import datetime
import hashlib

def get_connection():
    return sqlite3.connect('database.sqlite3')


def end_expired_sessions():
    with get_connection() as con:
        con.execute('DELETE FROM auth_tokens WHERE expiration_date <= ? ', (str(datetime.datetime.now()),))


def end_session_by_token(auth_token):
    with get_connection() as con:
        con.execute('DELETE FROM auth_tokens WHERE token = ?;',
                    (auth_token,))
        con.commit()
        con.close()


def retrieve_auth_token(user_id):
    with get_connection() as con:
        result = con.execute('SELECT auth_token FROM auth_tokens WHERE user_id = ?', (user_id,))
        token = result.fetchone() if result.arraysize else None
        con.close()
    return token


def end_session(request):
    if 'auth_token' in request.COOKIES:
        end_session_by_token(request.COOKIES['auth_token'])
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def register(request):
    return render(request, 'my_auth/register.html', {'error_messages':[]})


def add_user(request):
    error_messages = []

    login = request.POST['login']
    display_name = request.POST['display-name']
    password = request.POST['password']

    if password != request.POST['double-check-password']:
        error_messages.append('Пароли не совпадают!')

    with get_connection() as con:
        with open('log', 'w') as fout:
            fout.write(str(con.execute('SELECT user_id FROM users WHERE login = ?', (login, )).fetchone()))

        result = con.execute('SELECT user_id FROM users WHERE login = ?', (login, ))
        if result.arraysize:
            error_messages.append('Пользователь с таким логином уже существует')
        elif not error_messages:
            result = con.execute('SELECT count(*) FROM users').fetchone()

            hasher = hashlib.sha256()
            hasher.update(password)
            con.execute('INSERT INTO users VALUES (?, ?, ?, ?)',
                        (result[0] + 1, hasher.hexdigest(), display_name, login))
            con.commit()

    if error_messages:
        return render(request, 'my_auth/register.html', {'error_messages':error_messages})
    else:
        return HttpResponseRedirect(reverse('movies:index'))