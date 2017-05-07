from django.conf.urls import url

from . import views

app_name = 'session'
urlpatterns = [
    url('^$', views.index, name='index'),
    url('^book/(?P<session_id>[0-9]+)$', views.book, name='book'),
    url('^buy_tickets/(?P<session_id>[0-9]+)$', views.buy_tickets, name='buy_tickets'),
]