import os

import requests
from dotenv import load_dotenv

load_dotenv()  # Load TMDB_API_KEY from .env

TMDB_API_KEY = os.getenv("TMDB_API_KEY")
TMDB_API_URL = "https://api.themoviedb.org/3"


def get_movie_id(movie_title: str) -> int | None:
    """
    Search for a movie by title using the TMDb API and return its TMDb movie ID.

    Parameters:
        movie_title (str): The title of the movie.

    Returns:
        int | None: The TMDb movie ID if found, else None.
    """
    if not TMDB_API_KEY:
        raise ValueError("TMDB_API_KEY is not set in environment variables.")
    search_url = f"{TMDB_API_URL}/search/movie"
    search_params = {
        "api_key": TMDB_API_KEY,
        "query": movie_title,
        "include_adult": False,
    }
    response = requests.get(search_url, params=search_params)
    if response.status_code != 200:
        return None
    results = response.json().get("results")
    if not results:
        return None
    return results[0]["id"]


def get_movie_trailers(movie_id: int) -> list[dict]:
    """
    Retrieve the list of video trailers for a given TMDb movie ID.

    Parameters:
        movie_id (int): The TMDb movie ID.

    Returns:
        list[dict]: A list of video dicts (trailers) for the movie.
    """
    if not TMDB_API_KEY:
        raise ValueError("TMDB_API_KEY is not set in environment variables.")
    videos_url = f"{TMDB_API_URL}/movie/{movie_id}/videos"
    videos_params = {"api_key": TMDB_API_KEY}
    response = requests.get(videos_url, params=videos_params)
    if response.status_code != 200:
        return []
    return response.json().get("results", [])


def get_movie_trailer_url(movie_title: str) -> str | None:
    """
    Get the YouTube trailer URL for a given movie title using the TMDb API.

    Parameters:
        movie_title (str): The title of the movie.

    Returns:
        str | None: A YouTube URL for the trailer, or None if not found.
    """
    movie_id = get_movie_id(movie_title)
    if not movie_id:
        return None
    videos = get_movie_trailers(movie_id)
    for video in videos:
        if video.get("site") == "YouTube" and video.get("type") == "Trailer":
            return f"https://www.youtube.com/watch?v={video['key']}"
    return None


def get_poster_url(poster_path: str) -> str:
    """
    Construct the full URL to a movie poster image from its TMDb path.

    Parameters:
        poster_path (str): The poster path as returned by TMDb (e.g., '/abc123.jpg').

    Returns:
        str: The complete URL to the poster image.
    """
    base_url = "https://image.tmdb.org/t/p/w500"
    return f"{base_url}{poster_path}" if poster_path else ""
