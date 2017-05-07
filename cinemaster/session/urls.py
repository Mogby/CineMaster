from django.conf.urls import url

from . import views

app_name = 'session'
urlpatterns = [
    url('^$', views.index, name='index'),
]