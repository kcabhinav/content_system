from django.db import models


class Movie(models.Model):
    budget = models.IntegerField()
    homepage = models.URLField()
    original_language = models.CharField(max_length=2)
    overview = models.TextField()
    release_date = models.DateField(blank=True, null=True)
    revenue = models.IntegerField()
    runtime = models.IntegerField()
    status = models.CharField(max_length=10)
    title = models.CharField(max_length=255, unique=True)
    vote_average = models.FloatField()
    vote_count = models.IntegerField()
    production_company_id = models.IntegerField()
    genre_id = models.IntegerField()
    languages = models.JSONField(default=list, blank=True)

    class Meta:
        db_table = "movies"

    def __str__(self):
        return self.title
