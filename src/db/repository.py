"""
Repository module providing domain-specific data access functions
for movies and ratings from a SQLite database.
"""

import sqlite3
from typing import List, Optional, Tuple


def get_movie_by_id(conn: sqlite3.Connection, movie_id: int) -> Optional[Tuple]:
    """
    Fetch a single movie by its unique ID.

    Args:
        conn: SQLite database connection object.
        movie_id: Unique identifier for the movie.

    Returns:
        A tuple containing the movie's data if found, otherwise None.
    """
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM movies WHERE movieId = ?", (movie_id,))
    return cursor.fetchone()


def get_top_rated_movies(conn: sqlite3.Connection, limit: int = 10) -> List[Tuple]:
    """
    Retrieve a list of top-rated movies ordered by average vote descending.

    Args:
        conn: SQLite database connection object.
        limit: Maximum number of movies to return.

    Returns:
        A list of tuples, each representing a movie record.
    """
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT * FROM movies
        ORDER BY vote_average DESC
        LIMIT ?
    """,
        (limit,),
    )
    return cursor.fetchall()


def get_movies_by_genre(
    conn: sqlite3.Connection, genre: str, limit: int = 10
) -> List[Tuple]:
    """
    Retrieve movies filtered by genre (case-insensitive), ordered by average vote descending.

    Args:
        conn: SQLite database connection object.
        genre: Genre name to filter movies by.
        limit: Maximum number of movies to return.

    Returns:
        A list of tuples, each representing a movie record matching the genre.
    """
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT * FROM movies
        WHERE LOWER(genres) LIKE ?
        ORDER BY vote_average DESC
        LIMIT ?
    """,
        (f"%{genre.lower()}%", limit),
    )
    return cursor.fetchall()


def get_ratings_by_user(conn: sqlite3.Connection, user_id: int) -> List[Tuple]:
    """
    Retrieve all ratings submitted by a specific user.

    Args:
        conn: SQLite database connection object.
        user_id: Unique identifier for the user.

    Returns:
        A list of tuples representing the ratings made by the user.
    """
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM ratings WHERE userId = ?", (user_id,))
    return cursor.fetchall()


def get_all_movies(conn: sqlite3.Connection) -> List[Tuple]:
    """
    Retrieve all movies with selected metadata fields.

    Args:
        conn: SQLite database connection object.

    Returns:
        A list of tuples, each containing movie metadata fields.
    """
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT movieId, title, genres, overview, poster_path, vote_average, popularity
        FROM movies
    """
    )
    return cursor.fetchall()


def get_all_ratings(conn: sqlite3.Connection) -> List[Tuple]:
    """
    Retrieve all user-movie rating triplets.

    Args:
        conn: SQLite database connection object.

    Returns:
        A list of tuples containing userId, movieId, and rating.
    """
    cursor = conn.cursor()
    cursor.execute("SELECT userId, movieId, rating FROM ratings;")
    return cursor.fetchall()


def get_all_movie_ids(conn: sqlite3.Connection) -> List[int]:
    """
    Retrieve all distinct movie IDs from the movies table.

    Args:
        conn: SQLite database connection object.

    Returns:
        A list of unique movie IDs.
    """
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT movieId FROM movies;")
    rows = cursor.fetchall()
    return [row[0] for row in rows]


def get_valid_ratings(conn: sqlite3.Connection) -> List[Tuple]:
    """
    Retrieve ratings only for movies that exist in the movies table (validated by inner join).

    Args:
        conn: SQLite database connection object.

    Returns:
        A list of tuples containing userId, movieId, and rating for valid movie ratings.
    """
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT r.userId, r.movieId, r.rating
        FROM ratings r
        INNER JOIN movies m ON r.movieId = m.movieId
    """
    )
    return cursor.fetchall()
