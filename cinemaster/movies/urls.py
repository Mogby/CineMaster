from django.conf.urls import url

from . import views

app_name = 'movies'
urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^movie/(?P<movie_id>[0-9]+)$', views.detail, name='detail'),
]