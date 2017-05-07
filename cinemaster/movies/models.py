from django.db import models


class User(models.Model):
    password = models.CharField(max_length=64)
    display_name = models.CharField(max_length=30)


class Movie(models.Model):
    title = models.CharField(max_length=200)
    release_date = models.DateField()
    director = models.CharField(max_length=200)
    language = models.CharField(max_length=60)
    subtitles = models.CharField(max_length=60)
    age_restriction = models.IntegerField()
    duration = models.IntegerField()
    box_office = models.FloatField()
    rating_sum = models.IntegerField(default=0)
    reviews_count = models.IntegerField(default=0)

    def __str__(self):
        return self.title


class Session(models.Model):
    movie_id = models.ForeignKey(Movie, on_delete=models.CASCADE)
    begin_time = models.DateTimeField()
    end_time = models.DateTimeField()
    hall_no = models.IntegerField()


class Review(models.Model):
    movie_id = models.ForeignKey(Movie, on_delete=models.CASCADE)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField()
    review = models.TextField()
    pub_date = models.DateTimeField()
