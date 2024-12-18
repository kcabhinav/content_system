# Create your views here.
import csv
from .models import Movie
from datetime import datetime
from rest_framework.decorators import api_view
from rest_framework import generics
from rest_framework.pagination import PageNumberPagination
from .serializers import MovieSerializer
from rest_framework.response import Response
from django.db import transaction


@api_view(["POST"])
def upload_file(request):
    if request.method == 'POST' and request.FILES['file']:
        csv_file = request.FILES['file']

        # Check file type (ensure it's CSV)
        if not csv_file.name.endswith('.csv'):
            return Response({"error": "This is not a CSV file."}, status=400)

        csv_reader = csv.DictReader(csv_file.read().decode('utf-8').splitlines())
        
        failed_rows = []
        movie_titles_and_dates = []
        movie_instances = []
        for idx, row in enumerate(csv_reader, start=1):  # Include the row number for debugging
            try:
                release_date_str = row['release_date']
                try:
                    release_date = datetime.fromisoformat(release_date_str).date()
                except (ValueError, TypeError):
                    release_date = None  

                title = row.get('title', '').strip() or ''
                original_language = row.get('original_language', '').strip() or ''
                overview = row.get('overview', '').strip() or ''
                budget = row.get('budget', '0')
                revenue = row.get('revenue', '0')
                runtime = row.get('runtime', '0')
                status = row.get('status', '').strip() or ''
                vote_average = row.get('vote_average', '0')
                vote_count = row.get('vote_count', '0')
                production_company_id = row.get('production_company_id', '0')
                genre_id = row.get('genre_id', '0')
                languages = row.get('languages', '').strip() or ''
                movie_titles_and_dates = [(title, release_date)]

                movie_instances.append(
                    Movie(
                        title=title,
                        original_language=original_language,
                        overview=overview,
                        release_date=release_date,
                        budget=budget,
                        revenue=revenue,
                        runtime=runtime,
                        status=status,
                        vote_average=vote_average,
                        vote_count=vote_count,
                        production_company_id=production_company_id,
                        genre_id=genre_id,
                        languages=languages  # Assumes this is in a valid format already
                    )
                )

            except Exception as e:
                # Log the error with the row index and store it in the failed_rows list
                error_message = f"Error processing row {idx}: {str(e)}"
                failed_rows.append({"row": idx, "error": error_message, "row_data": row})


        # If there were any errors, return a response indicating which rows failed
        if failed_rows:
            return Response({
                "message": "Some rows failed to process.",
                "failed_rows": failed_rows
            }, status=400)

        existing_movies = Movie.objects.filter(
            title__in=[movie[0] for movie in movie_titles_and_dates],
            release_date__in=[movie[1] for movie in movie_titles_and_dates]
        )

        # Create a set of (title, release_date) for easy lookups
        existing_titles_and_dates = {(movie.title, movie.release_date) for movie in existing_movies}

        # Filter out duplicates from the movie_instances list
        unique_movie_instances = [
            movie for movie in movie_instances if (movie.title, movie.release_date) not in existing_titles_and_dates
        ]


        if not unique_movie_instances or unique_movie_instances == failed_rows:
            return Response({"message": "No new movies to insert"}, status=201)
        try:
            with transaction.atomic():
                Movie.objects.bulk_create(movie_instances, batch_size=100, ignore_conflicts=True)  # Batch size of 100 for bulk inserts
        except Exception as e:
            print(f"Error during bulk insert: {str(e)}")
            return Response({"error": "Error during bulk insert"}, status=500)

        return Response({"message": "File successfully uploaded and processed"}, status=201)
    
    return Response({"error": "No file uploaded"}, status=400)

class MoviePagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "per_page"
    max_page_size = 100


class MovieListView(generics.ListAPIView):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer
    pagination_class = MoviePagination

    def get_queryset(self):
        queryset = super().get_queryset()

        year = self.request.query_params.get("year")
        language = self.request.query_params.get("language")
        sort_by = self.request.query_params.get("sort_by", "release_date")
        sort_order = self.request.query_params.get("sort_order", "asc")
        
        if year:
            queryset = queryset.filter(release_date__year=year)

        if language:
            queryset = queryset.filter(languages__icontains=language)

        if sort_by == "release_date":
            queryset = queryset.order_by("release_date" if sort_order == "asc" else "-release_date")
        elif sort_by == "ratings":
            queryset = queryset.order_by("vote_average" if sort_order == "asc" else "-vote_average")

        return queryset

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        
        if response.data.get('count'):
            total_items = response.data['count']
            page_size = self.pagination_class.page_size
            total_pages = (total_items // page_size) + (1 if total_items % page_size > 0 else 0)

            response.data['total_pages'] = total_pages

        return response
