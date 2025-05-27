import pandas as pd
from scipy.sparse import csr_matrix
from sklearn.metrics.pairwise import cosine_similarity


class CollaborativeFilteringRecommender:
    def __init__(self, ratings_path):
        self.ratings_path = ratings_path
        self.ratings_df = None
        self.user_item_matrix = None
        self.similarity_matrix = None
        self.user_ids = None
        self.item_ids = None

    def load_data(self):
        self.ratings_df = pd.read_csv(self.ratings_path)
        print(f"✅ Loaded {len(self.ratings_df)} ratings")

    def build_user_item_matrix(self):
        pivot = self.ratings_df.pivot(
            index="userId", columns="movieId", values="rating"
        ).fillna(0)
        self.user_item_matrix = csr_matrix(pivot.values)
        self.user_ids = pivot.index.tolist()
        self.item_ids = pivot.columns.tolist()
        print(f"✅ Built user-item matrix with shape {pivot.shape}")

    def compute_user_similarity(self):
        self.similarity_matrix = cosine_similarity(self.user_item_matrix)
        print("✅ Computed user-user similarity matrix")

    def get_user_recommendations(self, user_id, top_n=5):
        if self.similarity_matrix is None:
            raise ValueError(
                "⚠️ Similarity matrix not computed. Run compute_user_similarity()."
            )

        if user_id not in self.user_ids:
            raise ValueError(f"❌ User ID {user_id} not found in dataset.")

        user_idx = self.user_ids.index(user_id)
        sim_scores = list(enumerate(self.similarity_matrix[user_idx]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)[
            1:
        ]  # exclude self

        similar_users = [self.user_ids[i] for i, _ in sim_scores[:top_n]]
        print(f"🔍 Top {top_n} similar users to user {user_id}: {similar_users}")
        return similar_users


if __name__ == "__main__":
    recommender = CollaborativeFilteringRecommender("data/ml-1m/ratings.csv")
    recommender.load_data()
    recommender.build_user_item_matrix()
    recommender.compute_user_similarity()
    recommender.get_user_recommendations(user_id=1, top_n=5)
