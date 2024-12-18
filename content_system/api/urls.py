from django.urls import path
from . import views

urlpatterns = [
    path('movies', views.MovieListView.as_view(), name='movie-list'),
    path('upload', views.upload_file, name='upload'),
]

