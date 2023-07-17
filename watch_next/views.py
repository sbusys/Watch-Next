import spacy
import requests
import os

from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render

url = "https://api.themoviedb.org/3/search/multi"
api_key = "736ed3567de99709070b801464a1513f"  # Replace with your MovieDB API key

nlp = spacy.load('en_core_web_md')


def index(request):
    return render(request, 'watch_next/index.html')


def search_movies(query):
    query_params = {
        "api_key": api_key,
        "query": query
    }
    response = requests.get(url, params=query_params)
    if response.status_code == 200:
        data = response.json().get("results", [])
        for result in data:
            media_type = result.get("media_type")
            if media_type == "movie":
                return extract_movie_data(result)
            elif media_type == "tv":
                return extract_series_data(result)
    return None, None, None, None, None, None


def extract_movie_data(result):
    movie_title = result.get("title")
    movie_overview = result.get("overview")
    movie_rating = result.get("vote_average")
    movie_genre_ids = result.get("genre_ids")
    movie_poster = get_image_url(result.get("poster_path"))
    movie_trailer = get_movie_trailer(result.get("id"))
    return movie_title, movie_overview, movie_rating, movie_genre_ids, movie_poster, movie_trailer    


def extract_series_data(result):
    series_title = result.get("name")
    series_overview = result.get("overview")
    series_rating = result.get("vote_average")
    series_genre_ids = result.get("genre_ids")
    series_poster = get_image_url(result.get("poster_path"))
    series_trailer = get_series_trailer(result.get("id"))
    return series_title, series_overview, series_rating, series_genre_ids, series_poster, series_trailer


def get_image_url(image_path):
    if image_path:
        return f"https://image.tmdb.org/t/p/w500/{image_path}"
    else:
        default_image_path = "static/assets/img/popcorn.jpg"
        if os.path.exists(default_image_path):
            return default_image_path
    return None


"""def get_image_url(image_path):
    if image_path:
        return f"https://image.tmdb.org/t/p/w500/{image_path}"
    return "static/assets/img/popcorn.jpg"
    
"""
def get_movie_trailer(movie_id):
    trailer_url = f"https://api.themoviedb.org/3/movie/{movie_id}/videos"
    query_params = {"api_key": api_key}
    response = requests.get(trailer_url, params=query_params)

    if response.status_code == 200:
        data = response.json().get("results", [])
        for result in data:
            trailer_key = result.get("key")
            if trailer_key:
                return f"https://www.youtube.com/watch?v={trailer_key}"
    return None
    
    

def get_series_trailer(series_id):
    trailer_url = f"https://api.themoviedb.org/3/tv/{series_id}/videos"
    query_params = {"api_key": api_key}
    response = requests.get(trailer_url, params=query_params)
    if response.status_code == 200:
        data = response.json().get("results", [])
        for result in data:
            trailer_key = result.get("key")
            if trailer_key:
                return f"https://www.youtube.com/watch?v={trailer_key}"
            
    return None

def trailer(request):
    
        return render(request, 'watch_next/trailer.html')
  
    

def recommend_movies(movie_title, movie_overview, movie_rating, movie_genre_ids, movie_poster, movie_trailer):
    if movie_title is None:
        movie_title = "Title Unknown"

    query_params = {
        "api_key": api_key,
        "query": movie_title,
        "overview": movie_overview,
        "vote_average": movie_rating,
        "with_genres": ",".join(str(genre_id) for genre_id in movie_genre_ids)
    }
    response = requests.get(url, params=query_params)
    if response.status_code == 200:
        data = response.json().get("results", [])
        recommended_movies = []
        for result in data:
            title = result.get("title")
            overview = result.get("overview")
            rating = result.get("vote_average")
            poster = get_image_url(result.get("poster_path"))
            trailer = get_movie_trailer(result.get("id"))
            
            if overview is not None:
                similarity = nlp(movie_overview).similarity(nlp(overview))
                if title != movie_title and similarity > 0.7:
                    if title is None:
                        title = "We couldnt find thr title of the movie, sorry"
                    rating = round(rating, 1)
                    recommended_movies.append({
                        "title": title,
                        "overview": overview,
                        "rating": rating,
                        "poster": poster,
                        "trailer": trailer
                    })

        
        return sorted(recommended_movies, key=lambda x: x["rating"], reverse=True)[:3]
    
    return "No recommended movies found, sorry"
    

@csrf_exempt
def search(request):
    if request.method == 'POST':
        user_input = request.POST.get('series_or_movie')
        movie_title, movie_overview, movie_rating, movie_genre_ids, movie_poster, movie_trailer = search_movies(user_input)
        if movie_title:
            recommended_movies = recommend_movies(movie_title, movie_overview, movie_rating, movie_genre_ids, movie_poster, movie_trailer)
            movie_rating = round(movie_rating, 1) 
            
            context = {
                'movie_found': True,
                'movie_title': movie_title,
                'movie_overview': movie_overview,
                'movie_rating': movie_rating,
                'movie_genre_ids': movie_genre_ids,
                'movie_poster': movie_poster,
                'movie_trailer': movie_trailer,
                'recommended_movies': recommended_movies,
            }
            
            return render(request, 'watch_next/results.html', context)

        else:
            return HttpResponse("Movie not found, please try a different title ")

    return HttpResponse("Invalid request")

'''
                             THINGS TO FIX !!!
- RATING SHOULD BE ROUNDED OFF TO TWO DECIMAL PLACES
- IF THE TRAILER OF THE MOVIE IS NOT AVALABLE,REPLACE WITH A STRING
- POSTER IMAGE PLACEHOLDER, IF THE POSTER S NULL
'''