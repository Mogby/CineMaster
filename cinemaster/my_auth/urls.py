from django.conf.urls import url

from . import views

app_name = 'my_auth'
urlpatterns = [
    url('^register$', views.register, name='register'),
    url('^adduser$', views.add_user, name='add_user'),
    url('^login$', views.login, name='login'),
    url('^logout$', views.logout, name='logout'),
]