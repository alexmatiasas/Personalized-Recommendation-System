"""
Collaborative Filtering Recommender

This script implements a user-based collaborative filtering system using cosine similarity
on the MovieLens 1M ratings dataset. It includes functions to load data, build a sparse user-item
matrix, compute similarity between users, and generate movie recommendations.
"""

import pandas as pd
from scipy.sparse import csr_matrix
from sklearn.metrics.pairwise import cosine_similarity


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
        Sets up internal structures for later use.
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

        If ratings_df and/or enriched_df are provided, use them directly.
        Otherwise, load data from the provided file paths.

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
        # Convert the pivot table to a sparse matrix for efficiency
        self.user_item_matrix = csr_matrix(pivot.values)
        # Store the user and movie IDs for later reference
        self.user_ids = pivot.index.tolist()
        self.item_ids = pivot.columns.tolist()
        print(f"✅ Built user-item matrix with shape {pivot.shape}")

    def compute_user_similarity(self):
        """
        Compute cosine similarity between all users based on their ratings.

        The similarity matrix captures how similar each user is to every other user.
        """
        # Compute similarity between users based on their rating vectors
        self.similarity_matrix = cosine_similarity(self.user_item_matrix)
        print("✅ Computed user-user similarity matrix")

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


if __name__ == "__main__":
    # Instantiate the recommender with dataset paths
    recommender = CollaborativeFilteringRecommender(
        "data/ml-1m/ratings.csv", "data/processed/enriched_movies.csv"
    )

    # Run the full recommendation pipeline:
    # 1. Load and filter data
    recommender.load_data()
    # 2. Build the user-item matrix
    recommender.build_user_item_matrix()
    # 3. Compute user-user similarity
    recommender.compute_user_similarity()
    # 4. Get the top 5 most similar users to user 1
    recommender.get_user_recommendations(user_id=1, top_n=5)
    # 5. Get the top 5 recommended movies for user 1
    recommender.recommend_movies_for_user(user_id=1, top_n=5)
