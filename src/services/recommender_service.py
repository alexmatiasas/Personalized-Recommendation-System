"""
Recommender Service Module

This module provides functions to generate movie recommendations based on collaborative filtering.
It loads precomputed user-item and similarity matrices and offers functionality to find similar users
and recommend items based on their preferences.
"""

import logging
import os
import sys

# Add src/ to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from typing import List

import numpy as np
import pandas as pd
from dotenv import load_dotenv
from scipy.sparse import csr_matrix

from backend.core.config import DB_PATH
from src.collaborative_filtering import ensure_matrices_exist

# Import get_valid_ratings from repository
from src.db.repository import get_top_rated_movies, get_valid_ratings
from src.db.sqlite_client import get_connection

logging.basicConfig(level=logging.INFO)  # Change to DEBUG for more verbose output
logger = logging.getLogger(__name__)

ensure_matrices_exist()

load_dotenv()
DATA_MODE = os.getenv("DATA_MODE", "full").lower()
MATRIX_DIR = "data/processed_demo" if DATA_MODE == "demo" else "data/processed"
USER_ITEM_MATRIX_PATH = os.path.join(MATRIX_DIR, "user_item_matrix.npz")
USER_SIMILARITY_MATRIX_PATH = os.path.join(MATRIX_DIR, "similarity_matrix.npy")


data = np.load(USER_ITEM_MATRIX_PATH)
# Reconstruct real user and movie ID lists from the database
conn = get_connection(DB_PATH)

ratings = pd.DataFrame(get_valid_ratings(conn), columns=["userId", "movieId", "rating"])
user_ids = sorted(ratings["userId"].unique())
movie_ids = sorted(ratings["movieId"].unique())

user_item_sparse = csr_matrix(
    (data["data"], data["indices"], data["indptr"]), shape=data["shape"]
)
# Build the DataFrame using real IDs as index and columns
user_item_matrix = pd.DataFrame.sparse.from_spmatrix(
    user_item_sparse, index=user_ids, columns=movie_ids
)
user_similarity = np.load(USER_SIMILARITY_MATRIX_PATH)


def get_top_similar_users(user_id: int, top_n: int = 5) -> List[int]:
    """
    Return the top N users most similar to the given user.

    Args:
        user_id (int): The ID of the target user.
        top_n (int): Number of similar users to return. Default is 5.

    Returns:
        List[int]: List of user IDs most similar to the given user.

    Raises:
        ValueError: If the user_id is not found in the user-item matrix.
    """
    if user_id not in user_item_matrix.index:
        raise ValueError(f"User ID {user_id} not found in user-item matrix.")
    user_vector = user_similarity[user_id - 1]
    similar_user_indices = np.argsort(user_vector)[::-1]
    similar_user_ids = [
        user_item_matrix.index[i]
        for i in similar_user_indices
        if user_item_matrix.index[i] != user_id
    ]
    return similar_user_ids[:top_n]


def get_user_recommendations(user_id: int, top_n: int = 10) -> List[int]:
    """
    Recommend movie IDs to a user based on collaborative filtering.

    Args:
        user_id (int): The ID of the user for whom to generate recommendations.
        top_n (int): Number of movie recommendations to return. Default is 10.

    Returns:
        List[int]: List of recommended movie IDs.

    Raises:
        ValueError: If the user_id is not found in the user-item matrix.
    """
    if user_id not in user_item_matrix.index:
        # Cold-start fallback: return global top-rated movies if user not found
        conn = get_connection(DB_PATH)
        top_movies = get_top_rated_movies(conn, limit=top_n)
        return [row[0] for row in top_movies]
    logger.debug(f"user_ids = {list(user_item_matrix.index)}")
    user_idx = list(user_item_matrix.index).index(user_id)
    logger.debug(f"user_id {user_id} at index {user_idx}")
    similar_users = get_top_similar_users(user_id, top_n=top_n)

    # Aggregate ratings of similar users
    movie_scores = user_item_matrix.loc[similar_users].mean(axis=0)
    logger.debug(f"raw movie_scores for similar users head: {movie_scores.head()}")
    user_seen_movies = user_item_matrix.loc[user_id]
    unseen_scores = movie_scores[user_seen_movies == 0]
    logger.debug(f"unseen_scores head: {unseen_scores.head()}")

    top_movie_ids = (
        unseen_scores.sort_values(ascending=False).head(top_n).index.tolist()
    )
    logger.debug(f"top_movie_ids = {top_movie_ids}")
    return top_movie_ids
