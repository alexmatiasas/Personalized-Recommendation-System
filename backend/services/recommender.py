"""
backend/services/recommender.py

Service layer for movie recommendations.
Provides functions for content-based and collaborative filtering recommendations,
and utilities to load movie data from the SQLite database.
"""

import os
import sys

# Add src/ to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import sqlite3
from pathlib import Path
from typing import List

import pandas as pd

from backend.core.config import DB_PATH
from backend.models.movie import RecommendationItem
from src.services.recommender_service import get_user_recommendations


def load_movies_from_db() -> pd.DataFrame:
    """
    Load movies from the SQLite database.

    Returns:
        pd.DataFrame: DataFrame with columns movieId, title, genres.
    """
    with sqlite3.connect(DB_PATH) as conn:
        return pd.read_sql_query("SELECT movieId, title, genres FROM movies", conn)


def get_content_recommendations(movie_id: int, top_n: int = 5) -> List[dict]:
    """
    Generate content-based recommendations using Jaccard similarity on genres.

    Args:
        movie_id (int): The movie ID to base similarity on.
        top_n (int): Number of recommendations to return.

    Returns:
        List[dict]: Recommended movies with movieId, title, genres, and similarity.
    """
    df = load_movies_from_db()
    if movie_id not in df["movieId"].values:
        raise ValueError(f"Movie ID {movie_id} not found in dataset")
    target = df[df["movieId"] == movie_id].iloc[0]
    target_genres = set(target["genres"].split("|"))

    def jaccard_similarity(genres_str: str) -> float:
        genres_set = set(genres_str.split("|"))
        intersection = target_genres & genres_set
        union = target_genres | genres_set
        return len(intersection) / len(union) if union else 0.0

    df["similarity"] = df["genres"].apply(jaccard_similarity)
    recs = (
        df[df["movieId"] != movie_id]
        .sort_values("similarity", ascending=False)
        .head(top_n)
    )
    return recs[["movieId", "title", "genres", "similarity"]].to_dict(orient="records")


def get_collaborative_recommendations(user_id: int, top_n: int = 10) -> List[int]:
    """
    Retrieve collaborative filtering recommendations for a user.

    Args:
        user_id (int): The user ID to recommend for.
        top_n (int): Number of recommendations to return.

    Returns:
        List[int]: List of recommended movie IDs.
    """
    return get_user_recommendations(user_id=user_id, top_n=top_n)


class ContentBasedRecommender:
    """
    Object-oriented interface for content-based recommendations.
    """

    def __init__(self, db_path: Path = DB_PATH):
        """
        Args:
            db_path (Path): Path to SQLite database file.
        """
        self.db_path = db_path
        self.movies_df = load_movies_from_db()

    def recommend_movies(self, movie_id: int, top_n: int = 5) -> List[dict]:
        """
        Recommend movies using content-based filtering.

        Args:
            movie_id (int): Movie ID for similarity.
            top_n (int): Number of recommendations.

        Returns:
            List[dict]: List of recommendation entries.
        """
        return get_content_recommendations(movie_id, top_n)

    def get_all_movies(self) -> List[RecommendationItem]:
        """
        Retrieve all movies as RecommendationItem list.

        Returns:
            List[RecommendationItem]: List of movie items.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT movieId, title FROM movies")
        rows = cursor.fetchall()
        conn.close()
        return [RecommendationItem(movieId=row[0], title=row[1]) for row in rows]
