from django.conf.urls import url

from . import views


app_name = 'movies'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^movie/(?P<movie_id>[0-9]+)$', views.detail, name='detail'),
    url('^edit_review/(?P<movie_id>[0-9]+)', views.edit_review, name='edit_review'),
    url('^post_review/(?P<movie_id>[0-9]+)', views.post_review, name='post_review'),
    url('^delete_review/(?P<movie_id>[0-9]+)', views.delete_review, name='delete_review'),
]