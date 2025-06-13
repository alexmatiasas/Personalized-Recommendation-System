"""
Collaborative Filtering Recommender

This script implements a user-based collaborative filtering system using cosine similarity
on the MovieLens 1M ratings dataset. It supports loading data either from CSV files or from
a SQLite database, leveraging internal repository utilities. The script also includes functionality
to save and load precomputed user-item and similarity matrices for efficient reuse.
"""

import os
import sys

from dotenv import load_dotenv

# Add src/ to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import joblib
import pandas as pd
from scipy.sparse import csr_matrix
from sklearn.metrics.pairwise import cosine_similarity

from src.db.repository import get_valid_ratings

load_dotenv()


class CollaborativeFilteringRecommender:
    """
    A collaborative filtering recommender system based on user-user similarity.

    Attributes:
        ratings_path (str): Path to the CSV file with ratings.
        enriched_movies_path (str): Path to the CSV file with enriched movie metadata.
        ratings_df (pd.DataFrame): DataFrame containing the filtered ratings.
        user_item_matrix (csr_matrix): Sparse matrix of user-item ratings.
        similarity_matrix (np.ndarray): Matrix of cosine similarities between users.
        user_ids (List[int]): List of user IDs.
        item_ids (List[int]): List of movie IDs.
    """

    def __init__(self, ratings_path=None, enriched_movies_path=None):
        """
        Initialize the recommender system with file paths for the ratings and enriched metadata.

        Note:
            This class supports both file-based and database-driven pipelines.
        """
        self.ratings_path = ratings_path
        self.enriched_movies_path = enriched_movies_path
        self.ratings_df = None
        self.user_item_matrix = None
        self.similarity_matrix = None
        self.user_ids = None
        self.item_ids = None

    def load_data(self, ratings_df=None, enriched_df=None):
        """
        Load data from file or directly from provided DataFrames (for testing).

        Args:
            ratings_df (pd.DataFrame, optional): Ratings DataFrame for testing.
            enriched_df (pd.DataFrame, optional): Enriched movies DataFrame for testing.
        """
        if ratings_df is not None:
            self.ratings_df = ratings_df.copy()
            if enriched_df is not None:
                enriched_ids = set(enriched_df["movieId"])
                self.ratings_df = self.ratings_df[
                    self.ratings_df["movieId"].isin(enriched_ids)
                ]
        else:
            self.ratings_df = pd.read_csv(self.ratings_path)
            enriched_df = (
                pd.read_csv(self.enriched_movies_path)
                if self.enriched_movies_path
                else None
            )
            if enriched_df is not None:
                enriched_ids = set(enriched_df["movieId"])
                self.ratings_df = self.ratings_df[
                    self.ratings_df["movieId"].isin(enriched_ids)
                ]

        print(f"✅ Loaded {len(self.ratings_df)} ratings based on enriched metadata.")
        self.build_user_item_matrix()

    def load_data_from_db(self, db_path="data/recommendations.db"):
        """
        Load ratings from the SQLite database and build the user-item matrix.

        Connects to the SQLite database and uses internal repository utilities to fetch valid ratings.

        Args:
            db_path (str): Path to the SQLite database file.
        """
        from src.db.sqlite_client import get_connection

        conn = get_connection(db_path)
        rows = get_valid_ratings(conn)
        self.ratings_df = pd.DataFrame(rows, columns=["userId", "movieId", "rating"])
        print(f"✅ Loaded {len(self.ratings_df)} valid ratings directly from database.")
        self.build_user_item_matrix()

    def build_user_item_matrix(self):
        """
        Construct a sparse user-item matrix from the ratings DataFrame.

        Rows represent users, columns represent movies, and values are ratings.
        Missing ratings are filled with zeros.
        """
        # Create user-item matrix where rows = users and columns = movies
        pivot = self.ratings_df.pivot(
            index="userId", columns="movieId", values="rating"
        ).fillna(0)
        # Store the user and movie IDs for later reference
        self.user_ids = pivot.index.tolist()  # actual userId values
        self.item_ids = pivot.columns.tolist()  # actual movieId values
        # Convert to a sparse matrix preserving real indices and columns
        self.user_item_matrix = csr_matrix(pivot.values)

        # For debugging, you can reconstruct a DataFrame with real IDs:
        # self.user_item_df = pd.DataFrame.sparse.from_spmatrix(
        #     self.user_item_matrix,
        #     index=self.user_ids,
        #     columns=self.item_ids
        # )
        print(f"✅ Built user-item matrix with shape {pivot.shape}")

    def compute_user_similarity(self):
        """
        Compute cosine similarity between all users based on their ratings.

        The similarity matrix captures how similar each user is to every other user.
        """
        # Ensure the user-item matrix is initialized
        if self.user_item_matrix is None:
            raise ValueError(
                "⚠️ User-item matrix is not initialized. Did you call build_user_item_matrix()?"
            )
        # Compute similarity between users based on their rating vectors
        self.similarity_matrix = cosine_similarity(self.user_item_matrix)
        print("✅ Computed user-user similarity matrix")

    def save_matrices(self, matrix_dir="data/processed"):
        """
        Save the user-item matrix and similarity matrix as binary files.

        Args:
            matrix_dir (str): Directory path where the matrices will be saved.
        """
        import os

        import numpy as np
        from scipy.sparse import save_npz

        os.makedirs(matrix_dir, exist_ok=True)
        save_npz(
            os.path.join(matrix_dir, "user_item_matrix.npz"), self.user_item_matrix
        )
        np.save(
            os.path.join(matrix_dir, "similarity_matrix.npy"), self.similarity_matrix
        )
        print("💾 Saved user-item and similarity matrices.")

    def load_matrices(self, matrix_dir="data/processed"):
        """
        Load the user-item matrix and similarity matrix from binary files.
        If files are missing, regenerate them automatically.

        Args:
            matrix_dir (str): Directory path where the matrices are stored.
        """
        import os

        user_item_path = os.path.join(matrix_dir, "user_item_matrix.npz")
        similarity_path = os.path.join(matrix_dir, "similarity_matrix.npy")
        if not os.path.exists(user_item_path) or not os.path.exists(similarity_path):
            print("⚠️ Matrices not found. Recomputing...")
            # regenerate: load from DB, compute, then save
            self.load_data_from_db()  # default db_path or pass existing
            self.compute_user_similarity()
            self.save_matrices(matrix_dir=matrix_dir)

        import numpy as np
        from scipy.sparse import load_npz

        self.user_item_matrix = load_npz(user_item_path)
        self.similarity_matrix = np.load(similarity_path)
        # Restore user_ids and item_ids from the database
        import pandas as pd

        from src.db.repository import get_valid_ratings
        from src.db.sqlite_client import get_connection

        conn = get_connection(
            os.getenv("RECOMMENDATION_DB_PATH", "data/recommendations.db")
        )
        rows = get_valid_ratings(conn)
        ratings_df = pd.DataFrame(rows, columns=["userId", "movieId", "rating"])
        pivot = ratings_df.pivot(
            index="userId", columns="movieId", values="rating"
        ).fillna(0)
        self.user_ids = pivot.index.tolist()
        self.item_ids = pivot.columns.tolist()
        # Build a DataFrame view with real IDs for reference
        self.user_item_df = pd.DataFrame.sparse.from_spmatrix(
            self.user_item_matrix, index=self.user_ids, columns=self.item_ids
        )
        print("📥 Loaded precomputed user-item and similarity matrices.")

    def save_similarity(self, path="models/similarity_matrix.joblib"):
        """
        Save the computed similarity matrix using joblib for efficient serialization.

        Args:
            path (str): Destination file path for the similarity matrix.
        """
        if self.similarity_matrix is None:
            raise ValueError(
                "⚠️ Similarity matrix not computed. Run compute_user_similarity()."
            )
        import os

        os.makedirs(os.path.dirname(path), exist_ok=True)
        joblib.dump(self.similarity_matrix, path)
        print(f"💾 Similarity matrix saved to {path}")

    def load_similarity(self, path="models/similarity_matrix.joblib"):
        """
        Load a precomputed similarity matrix using joblib.

        Args:
            path (str): File path to the serialized similarity matrix.
        """
        self.similarity_matrix = joblib.load(path)
        print(f"📥 Similarity matrix loaded from {path}")

    def get_user_recommendations(self, user_id, top_n=5):
        """
        Return the top-N most similar users to the given user ID.

        Args:
            user_id (int): Target user ID.
            top_n (int): Number of similar users to return.

        Returns:
            List[int]: List of user IDs most similar to the input user.
        """
        if self.similarity_matrix is None:
            raise ValueError(
                "⚠️ Similarity matrix not computed. Run compute_user_similarity()."
            )

        if user_id not in self.user_ids:
            raise ValueError(f"❌ User ID {user_id} not found in dataset.")

        # Find the index of the target user
        user_idx = self.user_ids.index(user_id)
        # Get similarity scores for the user
        sim_scores = list(enumerate(self.similarity_matrix[user_idx]))
        # Sort by similarity, excluding the user itself (the first entry after sorting)
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)[1:]
        # Get the top-N most similar users' IDs
        similar_users = [self.user_ids[i] for i, _ in sim_scores[:top_n]]
        print(f"🔍 Top {top_n} similar users to user {user_id}: {similar_users}")
        return similar_users

    def recommend_movies_for_user(self, user_id, top_n=10, exclude_watched=True):
        """
        Recommend movies to a given user based on similar users' preferences.

        Args:
            user_id (int): Target user ID.
            top_n (int): Number of recommended movies to return.
            exclude_watched (bool): Whether to exclude movies already rated by the user.

        Returns:
            List[int]: List of recommended movie IDs.
        """
        if self.similarity_matrix is None:
            raise ValueError(
                "⚠️ Similarity matrix not computed. Run compute_user_similarity()."
            )
        if self.user_item_matrix is None:
            raise ValueError(
                "⚠️ User-item matrix not built. Run build_user_item_matrix()."
            )
        if user_id not in self.user_ids:
            raise ValueError(f"❌ User ID {user_id} not found in dataset.")

        # Find the index of the user
        user_idx = self.user_ids.index(user_id)
        # Get the ratings of the user as a dense array
        user_ratings = self.user_item_matrix[user_idx].toarray().flatten()
        # Get the similarity scores for this user
        sim_scores = self.similarity_matrix[user_idx]

        # Compute weighted scores for all movies using similar users' ratings
        scores = sim_scores @ self.user_item_matrix.toarray()
        # Exclude already rated movies by setting their score to -1, if requested
        if exclude_watched:
            scores[user_ratings > 0] = -1

        # Get indices of the top-N highest scoring movies
        top_indices = scores.argsort()[::-1][:top_n]
        # Map indices back to movie IDs
        top_movie_ids = [self.item_ids[i] for i in top_indices]

        print(f"🎯 Recommended movies for user {user_id}: {top_movie_ids}")
        return top_movie_ids


def ensure_matrices_exist():
    """
    Ensure that the similarity and user-item matrices exist.
    If not, regenerate them from the database.
    """
    import os

    DATA_MODE = os.getenv("DATA_MODE", "full").lower()
    db_path = (
        "data/demo/recommendations.db"
        if DATA_MODE == "demo"
        else "data/recommendations.db"
    )
    matrix_dir = "data/processed_demo" if DATA_MODE == "demo" else "data/processed"

    user_item_path = os.path.join(matrix_dir, "user_item_matrix.npz")
    similarity_path = os.path.join(matrix_dir, "similarity_matrix.npy")

    if not os.path.exists(user_item_path) or not os.path.exists(similarity_path):
        print("⚠️ Matrices not found. Recomputing...")
        recommender = CollaborativeFilteringRecommender()
        recommender.load_data_from_db(db_path=db_path)
        recommender.compute_user_similarity()
        recommender.save_matrices(matrix_dir=matrix_dir)
    else:
        print("✅ Matrices already exist.")


if __name__ == "__main__":
    ensure_matrices_exist()
    recommender = CollaborativeFilteringRecommender()
    recommender.load_matrices()
    recommender.get_user_recommendations(user_id=1, top_n=5)
    recommender.recommend_movies_for_user(user_id=1, top_n=5)
