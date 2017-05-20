from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse

import datetime

from .utilities import *


def end_session(request):
    if 'auth_token' in request.COOKIES:
        end_session_by_token(request.COOKIES['auth_token'])
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def add_user(request):
    error_messages = []

    login = request.POST['login']
    password = request.POST['password']

    if password != request.POST['double-check-password']:
        error_messages.append('Пароли не совпадают')

    with connect() as con:
        result = con.execute('SELECT user_id FROM users WHERE login = ?', (login, )).fetchone()

        if result:
            error_messages.append('Пользователь с таким логином уже существует')
        elif not error_messages:
            con.execute('INSERT INTO users (password, login) VALUES (?, ?)',
                        (get_hash(password), login))
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
    response.set_cookie('login', user['login'],
                        max_age=datetime.timedelta(days=30).total_seconds())
    response.set_cookie('user_id', str(user['user_id']),
                        max_age=datetime.timedelta(days=30).total_seconds())
    response.set_cookie('auth_token', str(update_auth_token(user)),
                        max_age=datetime.timedelta(days=30).total_seconds())

    return response


def logout(request):
    end_session(request)

    response = HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    response.delete_cookie('login')
    response.delete_cookie('user_id')
    response.delete_cookie('auth_token')

    return response