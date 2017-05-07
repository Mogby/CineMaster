from django.shortcuts import get_object_or_404, render
from django.views import generic

from .models import Movie, Review

class IndexView(generic.ListView):
    template_name = 'movies/index.html'
    context_object_name = 'movies_list'

    def get_queryset(self):
        return Movie.objects.all()

def detail(request, movie_id):
    movie = get_object_or_404(Movie, pk=movie_id)
    rating = 0.0 if not movie.reviews_count else movie.rating_sum / movie.reviews_count
    reviews = Review.objects.filter(movie_id=movie_id)
    return render(request, 'movies/detail.html',
                  {'movie':movie,
                   'rating':rating,
                   'reviews': reviews})