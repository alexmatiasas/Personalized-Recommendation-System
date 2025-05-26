import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class ContentBasedRecommender:
    def __init__(self, dataframe: pd.DataFrame, overview_column: str = "overview"):
        self.df = dataframe.copy()
        self.overview_column = overview_column
        self.tfidf_matrix = None
        self.similarity_matrix = None
        self.indices = None
        self.vectorizer = TfidfVectorizer(stop_words="english")

    def preprocess(self):
        self.df[self.overview_column] = self.df[self.overview_column].fillna("")

    def vectorize(self):
        self.tfidf_matrix = self.vectorizer.fit_transform(self.df[self.overview_column])

    def compute_similarity(self):
        self.similarity_matrix = cosine_similarity(self.tfidf_matrix, self.tfidf_matrix)
        self.indices = pd.Series(
            self.df.index, index=self.df["title"]
        ).drop_duplicates()

    def fit(self):
        self.preprocess()
        self.vectorize()
        self.compute_similarity()

    def get_recommendations(self, title: str, top_n: int = 5):
        if self.similarity_matrix is None or self.indices is None:
            raise ValueError(
                "Model has not been fitted. Call fit() before getting recommendations."
            )

        if title not in self.indices:
            raise ValueError(f"Title '{title}' not found in the dataset.")

        idx = self.indices[title]
        sim_scores = list(enumerate(self.similarity_matrix[idx]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        sim_scores = sim_scores[1 : top_n + 1]
        movie_indices = [i[0] for i in sim_scores]
        return self.df["title"].iloc[movie_indices].tolist()
