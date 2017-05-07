from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponseRedirect

import sqlite3
import datetime


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

def verify_token_belongs_to_user(auth_token, user_id):
    end_expired_sessions()
    with connect() as con:
        result = con.execute('SELECT user_id FROM auth_tokens WHERE token = ? AND user_id = ?',
                             (auth_token, user_id)).fetchall()
    return True if result else False

def index(request):
    with connect() as con:
        sessions = con.execute('SELECT * FROM sessions NATURAL JOIN movies').fetchall()

    return render(request, 'session/index.html', {'sessions': sessions})


def book(request, session_id):
    with connect() as con:
        free_seats = con.execute('SELECT * FROM tickets NATURAL JOIN seats '
                                 'WHERE session_id = ? AND sold = 0', (session_id,)).fetchall()
    return render(request, 'session/book.html',
                  {'free_seats':free_seats,
                   'session_id':session_id})


def buy_tickets(request, session_id):
    tickets = request.POST.getlist('seat_id')

    if not tickets or not verify_token_belongs_to_user(request.COOKIES['auth_token'],
                                                       request.COOKIES['user_id']):
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    with connect() as con:
        for ticket in tickets:
            con.execute('UPDATE tickets SET sold = 1, user_id = ? WHERE seat_id = ? AND session_id = ?',
                        (request.COOKIES['user_id'], ticket, session_id))
        con.commit()

    return HttpResponseRedirect(reverse('session:index'))