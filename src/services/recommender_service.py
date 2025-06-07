"""
Recommender Service Module

This module provides functions to generate movie recommendations based on collaborative filtering.
It loads precomputed user-item and similarity matrices and offers functionality to find similar users
and recommend items based on their preferences.
"""

import os
import sys

# Add src/ to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from typing import List

import numpy as np
import pandas as pd
from dotenv import load_dotenv
from scipy.sparse import csr_matrix

from src.collaborative_filtering import ensure_matrices_exist

ensure_matrices_exist()

load_dotenv()
DATA_MODE = os.getenv("DATA_MODE", "full").lower()
MATRIX_DIR = "data/processed_demo" if DATA_MODE == "demo" else "data/processed"
USER_ITEM_MATRIX_PATH = os.path.join(MATRIX_DIR, "user_item_matrix.npz")
USER_SIMILARITY_MATRIX_PATH = os.path.join(MATRIX_DIR, "similarity_matrix.npy")

data = np.load(USER_ITEM_MATRIX_PATH)
user_item_sparse = csr_matrix(
    (data["data"], data["indices"], data["indptr"]), shape=data["shape"]
)
user_item_matrix = pd.DataFrame.sparse.from_spmatrix(user_item_sparse)
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
        raise ValueError(f"User ID {user_id} not found in user-item matrix.")
    similar_users = get_top_similar_users(user_id, top_n=top_n)

    # Aggregate ratings of similar users
    movie_scores = user_item_matrix.loc[similar_users].mean(axis=0)
    user_seen_movies = user_item_matrix.loc[user_id]
    movie_scores = movie_scores[user_seen_movies == 0]  # Filter out already seen movies

    top_movie_ids = movie_scores.sort_values(ascending=False).head(top_n).index.tolist()
    return top_movie_ids
