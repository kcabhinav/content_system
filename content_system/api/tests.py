from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from .models import Movie
import tempfile
import os

class MovieApiTests(TestCase):

    def setUp(self):
        """
        Set up movie instances using the provided sample data.
        """
        # Create movie instances
        self.movie1 = Movie.objects.create(
            budget=30000000,
            homepage="http://toystory.disney.com/toy-story",
            original_language="en",
            original_title="Toy Story",
            overview="Led by Woody, Andy's toys live happily in his room until Andy's birthday brings Buzz Lightyear onto the scene. Afraid of losing his place in Andy's heart, Woody plots against Buzz. But when circumstances separate Buzz and Woody from their owner, the duo eventually learns to put aside their differences.",
            release_date="1995-10-30",
            revenue=373554033,
            runtime=81,
            status="Released",
            title="Toy Story",
            vote_average=7.7,
            vote_count=5415,
            production_company_id=3,
            genre_id=16,
            languages=["English"],
        )

        self.movie2 = Movie.objects.create(
            budget=65000000,
            homepage="http://toystory.disney.com/jumanji",
            original_language="en",
            original_title="Jumanji",
            overview="When siblings Judy and Peter discover an enchanted board game that opens the door to a magical world, they unwittingly invite Alan -- an adult who's been trapped inside the game for 26 years -- into their living room. Alan's only hope for freedom is to finish the game, which proves risky as all three find themselves running from giant rhinoceroses, evil monkeys and other terrifying creatures.",
            release_date="1995-12-15",
            revenue=262797249,
            runtime=104,
            status="Released",
            title="Jumanji",
            vote_average=6.9,
            vote_count=2413,
            production_company_id=559,
            genre_id=12,
            languages=["English", "Français"],
        )

        self.movie3 = Movie.objects.create(
            budget=0,
            homepage="http://toystory.disney.com/grumpier-old-men",
            original_language="en",
            original_title="Grumpier Old Men",
            overview="A family wedding reignites the ancient feud between next-door neighbors and fishing buddies John and Max. Meanwhile, a sultry Italian divorcée opens a restaurant at the local bait shop, alarming the locals who worry she'll scare the fish away. But she's less interested in seafood than she is in cooking up a hot time with Max.",
            release_date="1995-12-22",
            revenue=0,
            runtime=101,
            status="Released",
            title="Grumpier Old Men",
            vote_average=6.5,
            vote_count=92,
            production_company_id=6194,
            genre_id=10749,
            languages=["English"],
        )

    def test_upload_csv(self):
        """
        Test the CSV file upload API.
        """
        # Create a temporary CSV file for testing
        file_content = "budget,homepage,original_language,original_title,overview,release_date,revenue,runtime,status,title,vote_average,vote_count,production_company_id,genre_id,languages\n"
        file_content += "30000000,http://toystory.disney.com/toy-story,en,Toy Story,\"Led by Woody, Andy's toys live happily in his room until Andy's birthday brings Buzz Lightyear onto the scene. Afraid of losing his place in Andy's heart, Woody plots against Buzz. But when circumstances separate Buzz and Woody from their owner, the duo eventually learns to put aside their differences.\",1995-10-30,373554033,81,Released,Toy Story,7.7,5415,3,16,\"['English']\"\n"
        file_content += "65000000,,en,Jumanji,\"When siblings Judy and Peter discover an enchanted board game that opens the door to a magical world, they unwittingly invite Alan -- an adult who's been trapped inside the game for 26 years -- into their living room. Alan's only hope for freedom is to finish the game, which proves risky as all three find themselves running from giant rhinoceroses, evil monkeys and other terrifying creatures.\",1995-12-15,262797249,104,Released,Jumanji,6.9,2413,559,12,\"['English', 'Français']\"\n"

        # Create a SimpleUploadedFile object
        temp_csv = tempfile.NamedTemporaryFile(delete=False, mode='w', newline='', encoding='utf-8')
        temp_csv.write(file_content)
        temp_csv.close()
        # Open and upload the CSV file to the endpoint
        with open(temp_csv.name, 'rb') as file:
            response = self.client.post(reverse('upload'), {'file': file}, format='multipart')

        # Assert that the response status is 201 (Created)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['message'], 'File uploaded and saved successfully.')

        # Clean up the temporary file
        os.remove(temp_csv.name)

    def test_movie_list(self):
        """
        Test the movie list API with pagination, filtering, and sorting.
        """
        # Test basic movie list without any filters or sorting
        response = self.client.get(reverse('movie-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 3)  # Should return 3 movies

        # Test pagination (per_page=2, page=1)
        response = self.client.get(reverse('movie-list') + '?per_page=2&page=1')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)  # Should return 2 movies
        self.assertIsNotNone(response.data['next'])  # Should have a next page

        # Test filtering by year_of_release
        response = self.client.get(reverse('movie-list') + '?year=1995')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 3)  # Should return 3 movies
        self.assertEqual(response.data['results'][0]['title'], "Toy Story")  # First movie is Toy Story

        # Test filtering by language
        response = self.client.get(reverse('movie-list') + '?language=English')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 3)  # Should return all 3 movies

        # Test sorting by release_date (ascending)
        response = self.client.get(reverse('movie-list') + '?sort_by=release_date&sort_order=asc')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'][0]['title'], "Toy Story")  # 1995 movie comes first

        # Test sorting by ratings (descending)
        response = self.client.get(reverse('movie-list') + '?sort_by=ratings&sort_order=desc')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'][0]['title'], "Toy Story")  # Highest rating first

        # Test sorting by revenue (descending)
        response = self.client.get(reverse('movie-list') + '?sort_by=revenue&sort_order=desc')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'][0]['title'], "Toy Story")  # Highest revenue first

