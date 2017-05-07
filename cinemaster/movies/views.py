from django.shortcuts import render
from django.views import generic

from .models import Movie

class IndexView(generic.ListView):
    template_name = 'movies/index.html'
    context_object_name = 'movies_list'

    def get_queryset(self):
        return Movie.objects.all()