from django.http import Http404, HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import render

from .utilities import *

def index(request):
    with connect() as con:
        movies_list = con.execute('SELECT * FROM movies').fetchall()
        return render(request, 'movies/index.html', {'movies_list':movies_list})


def detail(request, movie_id):

    user_id = request.COOKIES.get('user_id')
    have_review = False

    with connect() as con:
        if user_id:
            have_review = True if con.execute('SELECT * FROM reviews WHERE movie_id = ? AND user_id = ?',
                                             (movie_id, user_id)).fetchone() else False
        movie = con.execute('SELECT * FROM movies WHERE movie_id = ?', (movie_id,)).fetchone()
        reviews = con.execute('SELECT * FROM reviews NATURAL JOIN users WHERE movie_id = ?', (movie_id,)).fetchall()
        reviews_count = len(reviews)
        rating_sum = con.execute('SELECT sum(rating) as rating_sum FROM reviews').fetchone()['rating_sum']

    if not movie:
        raise Http404("Фильм не существует")

    if reviews_count:
        rating = rating_sum / reviews_count
    else:
        rating = None

    return render(request, 'movies/detail.html',
                  {'movie':movie,
                   'rating':rating,
                   'reviews': reviews,
                   'have_review': have_review})


def edit_review(request, movie_id):
    user_id = request.COOKIES.get('user_id')
    if not user_id:
        return HttpResponseRedirect(reverse('movies:index'))

    with connect() as con:
        review = con.execute('SELECT * FROM reviews WHERE movie_id = ? AND user_id = ?',
                             (movie_id, user_id)).fetchone()
        movie = con.execute('SELECT * FROM movies WHERE movie_id = ?', (movie_id,)).fetchone()

    return render(request, 'movies/edit_review.html', {'movie':movie, 'review':review})


def post_review(request, movie_id):
    user_id = request.COOKIES.get('user_id')
    auth_token = request.COOKIES.get('auth_token')

    if not user_id or not auth_token or not verify_token_belongs_to_user(auth_token, user_id):
        return HttpResponseRedirect(reverse('movies:detail', kwargs={'movie_id':movie_id}))

    with connect() as con:
        review = con.execute('SELECT * FROM reviews WHERE movie_id = ? AND user_id = ?',
                             (movie_id, user_id)).fetchone()
        if review:
            con.execute('UPDATE reviews SET rating = ?, review = ? WHERE user_id = ? AND movie_id = ?;',
                        (request.POST['rating'], request.POST['review'], user_id, movie_id))
        else:
            con.execute('INSERT INTO reviews VALUES (?, ?, ?, ?);',
                        (movie_id, user_id, request.POST['rating'], request.POST['review']))

        con.commit()

    return HttpResponseRedirect(reverse('movies:detail', kwargs={'movie_id':movie_id}))


def delete_review(request, movie_id):
    user_id = request.COOKIES.get('user_id')
    auth_token = request.COOKIES.get('auth_token')

    if not user_id or not auth_token or not verify_token_belongs_to_user(auth_token, user_id):
        return HttpResponseRedirect(reverse('movies:detail', kwargs={'movie_id': movie_id}))

    with connect() as con:
        con.execute('DELETE FROM reviews WHERE user_id = ? AND movie_id = ?;', (user_id, movie_id))
        con.commit()

    return HttpResponseRedirect(reverse('movies:detail', kwargs={'movie_id': movie_id}))