from django.http import Http404
from django.shortcuts import render

import sqlite3


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


def index(request):
    with connect() as con:
        movies_list = con.execute('SELECT * FROM movies').fetchall()
        return render(request, 'movies/index.html', {'movies_list':movies_list})


def detail(request, movie_id):
    with connect() as con:
        movie = con.execute('SELECT * FROM movies WHERE movie_id = ?', (movie_id,)).fetchone()
        reviews = con.execute('SELECT * FROM reviews NATURAL JOIN users WHERE movie_id = ?', (movie_id,)).fetchall()
        reviews_count = len(reviews)
        rating_sum = con.execute('SELECT sum(rating) as rating_sum FROM reviews').fetchone()['rating_sum']

    if not movie:
        raise Http404("Фильм не существует")

    rating = rating_sum / reviews_count

    return render(request, 'movies/detail.html',
                  {'movie':movie,
                   'rating':rating,
                   'reviews': reviews})
