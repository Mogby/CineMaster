from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponseRedirect

import sqlite3
import datetime

from .utilities import *

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