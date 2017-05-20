import urllib.request
import re
import time
import html
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


def get_url(url):
    time.sleep(10)
    return ' '.encode('cp1251').join(urllib.request.urlopen(url).read().split())


def retrieve_pages(pages_count):
    response = get_url('https://www.kinopoisk.ru/afisha/new/')
    links = re.findall(r'<div class="name"> <a href="(.*?)">'.encode('cp1251'), response)[:pages_count]

    for index, link in enumerate(links):
        movie_info = get_url(''.join(['https://www.kinopoisk.ru', link.decode('cp1251')]))
        with open(''.join([str(index + 1), '.html']), 'wb') as fout:
            fout.write(movie_info)


def clear_movies():
    with connect() as con:
        con.execute('DELETE FROM movies WHERE 1=1;')
        con.commit()


def insertMovies(movies_count):
    name_pattern = re.compile(r'<h1 class="moviename-big" itemprop="name">(.*)</h1>'.encode('cp1251'))
    year_pattern = re.compile(r'<td class="type">год</td>.*?<a.*?>(.*?)</a>'.encode('cp1251'))
    director_pattern = re.compile(r'<td class="type">режиссер</td>.*?<a.*?>(.*?)</a>'.encode('cp1251'))
    age_pattern = re.compile(r'"ageLimit age(.*?)"'.encode('cp1251'))
    box_office_pattern = re.compile(r'"div_rus_box_td2".*?>.*?<a.*?>(.*?)</a>'.encode('cp1251'))
    description_pattern = re.compile(r'<div class="brand_words film-synopsys".*?>(.*?)<'.encode('cp1251'))
    poster_pattern = re.compile(r'class="popupBigImage cloud-zoom".*?href="(.*?)"'.encode('cp1251'))
    duration_pattern = re.compile(r'id="runtime">([0-9]*)'.encode('cp1251'))
    for index in range(1, movies_count + 1):
        with open(''.join(['pages/', str(index), '.html']), 'rb') as fin:
            movie_info = ' '.encode('cp1251').join(fin.read().split())
            title = html.unescape(name_pattern.findall(movie_info)[0].decode('cp1251'))
            year = html.unescape(year_pattern.findall(movie_info)[0].decode('cp1251'))
            director = html.unescape(director_pattern.findall(movie_info)[0].decode('cp1251'))
            age_restriction = html.unescape(age_pattern.findall(movie_info)[0].decode('cp1251'))
            age_restriction = ''.join([age_restriction, '+'])
            box_match = box_office_pattern.findall(movie_info)
            if not box_match:
                box_office = 'неизвестно'
            else:
                box_office = html.unescape(box_match[0].decode('cp1251'))
            description = html.unescape(description_pattern.findall(movie_info)[0].decode('cp1251'))
            poster = html.unescape(poster_pattern.findall(movie_info)[0].decode('cp1251'))
            if poster[0] == '/':
                poster = ''.join(['https://www.kinopoisk.ru', poster])
            duration = html.unescape(duration_pattern.findall(movie_info)[0].decode('cp1251'))

            with connect() as con:
                con.execute("INSERT INTO movies VALUES (NULL, ?, ?, ?, ?, ?, ? , ?, ?, ?, ?)",
                            (title, year, director, 'русский', 'нет', age_restriction, duration, box_office,
                             description, poster))
                con.commit()


def create_seats(*halls):
    with connect() as con:
        con.execute('DELETE FROM seats WHERE 1=1;')
        for hall_no, hall in enumerate(halls):
            for row_no, row in enumerate(hall):
                for seat_no, seat in enumerate(row):
                    special = 'NULL'
                    if seat == 'd':
                        special = 'кресло D-Box'
                    if seat == 'i':
                        special = 'место для инвалидов'
                    con.execute('INSERT INTO seats VALUES (NULL, ?, ?, ?, ?);', (hall_no+1, row_no+1, seat_no+1, special))
        con.commit()

def schedule_sessions(*halls):
    start_time = datetime.datetime.now() + datetime.timedelta(days=1)
    start_time = start_time.replace(hour=9, minute=0, second=0, microsecond=0)

    with connect() as con:
        con.execute('DELETE FROM sessions WHERE 1=1;')
        con.execute('DELETE FROM tickets WHERE 1=1;')
        movies = con.execute('SELECT movie_id, duration FROM movies;').fetchall()
        for hall_no in halls:
            current_time = start_time
            for movie in movies:
                end_time = current_time + datetime.timedelta(minutes = movie['duration'] + 15)
                con.execute('INSERT INTO sessions VALUES(NULL, ?, datetime(?), datetime(?), ?);',
                            (movie['movie_id'], current_time, end_time, hall_no))
                current_time = end_time + datetime.timedelta(minutes = 10)

                session_id = con.execute('SELECT max(session_id) as id FROM sessions').fetchone()['id']
                seats = con.execute('SELECT seat_id, special_features FROM seats WHERE hall_no = ?', (hall_no,))
                for seat in seats:
                    cost = 220 if seat['special_features'] == 'кресло D-Box' else 160
                    if movie['duration'] >= 120:
                        cost += 60
                    con.execute('INSERT INTO tickets VALUES(NULL, ?, ?, ?, 0)',
                                (seat['seat_id'], session_id, cost))

            movies = movies[1:] + movies[:1]

        con.commit()



if __name__ == '__main__':
    movies_count = 6
    #retrieve_pages(movies_count)
    clear_movies()
    insertMovies(movies_count)

    hall_1 = [
        'iiiii',
        'uuuuuuuuuuuuuuuu',
        'uuuuuuuuuuuuuuuu',
        'uuuuuuuuuuuuuuuu',
        'uuuuuuuuuuuuuuuu',
        'uuuuuudddduuuuuu',
        'uuuuuudddduuuuuu',
        'uuuuuuuuuuuuuuuu',
        'uuuuuuuuuuuuuuuu',
        'uuuuuuuuuuuuuuuu'
    ]

    hall_2 = [
        'uuuuuuuuuuuuuu',
        'uuuuuuuuuuuuuu',
        'uuuuuuuuuuuuu',
        'uuuuuuuuuuuuu',
        'uuuuuudddduuu',
        'uuuuuudddduuu',
        'uuuuuuuuuuuuu',
        'uuuuuuuuuuuuu',
        'uuuuuuuuuuuuu'
    ]

    #create_seats(hall_1, hall_2)
    schedule_sessions(1, 2)