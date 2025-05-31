import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class ContentBasedRecommender:
    """
    A content-based recommendation system that uses movie overviews to recommend similar movies.
    It vectorizes the movie overviews using TF-IDF and computes cosine similarity between them.
    """

    def __init__(self, dataframe: pd.DataFrame, overview_column: str = "overview"):
        """
        Initializes the recommender with a DataFrame and the name of the overview column.

        Parameters:
        - dataframe (pd.DataFrame): The dataset containing movie information.
        - overview_column (str): The column name containing textual overviews.
        """
        self.df = dataframe.copy()
        self.overview_column = overview_column
        # TF-IDF matrix of the overviews
        self.tfidf_matrix = None
        # Cosine similarity matrix between all movies
        self.similarity_matrix = None
        # Series mapping movie titles to their indices in the DataFrame
        self.indices = None
        # TF-IDF vectorizer initialized with English stop words
        self.vectorizer = TfidfVectorizer(stop_words="english")

    def preprocess(self):
        """
        Preprocesses the data by filling missing values in the overview column with empty strings.
        """
        # Replace null values in the overview column with empty strings
        self.df[self.overview_column] = self.df[self.overview_column].fillna("")

    def vectorize(self):
        """
        Converts the text overviews into TF-IDF feature vectors.
        """
        # Transform the overview texts into TF-IDF vectors
        self.tfidf_matrix = self.vectorizer.fit_transform(self.df[self.overview_column])

    def compute_similarity(self):
        """
        Computes the cosine similarity matrix between TF-IDF vectors and creates an index of titles.
        """
        # Calculate cosine similarity between all TF-IDF vectors
        self.similarity_matrix = cosine_similarity(self.tfidf_matrix, self.tfidf_matrix)
        # Create a Series mapping movie titles to DataFrame indices, dropping duplicates
        self.indices = pd.Series(
            self.df.index, index=self.df["title"]
        ).drop_duplicates()

    def fit(self):
        """
        Runs the full pipeline: preprocesses data, vectorizes text, and computes similarity matrix.
        """
        self.preprocess()
        self.vectorize()
        self.compute_similarity()

    def get_recommendations(self, title: str, top_n: int = 5):
        """
        Returns a list of recommended movie titles similar to the given title.

        Parameters:
        - title (str): The title of the movie for which recommendations are sought.
        - top_n (int): The number of recommendations to return.

        Returns:
        - List[str]: A list of recommended movie titles.
        """
        # Check if the model has been fitted
        if self.similarity_matrix is None or self.indices is None:
            raise ValueError(
                "Model has not been fitted. Call fit() before getting recommendations."
            )

        # Check if the requested title exists in the dataset
        if title not in self.indices:
            raise ValueError(f"Title '{title}' not found in the dataset.")

        # Get the index of the movie that matches the title
        idx = self.indices[title]

        # Get the pairwise similarity scores of all movies with that movie
        sim_scores = list(enumerate(self.similarity_matrix[idx]))

        # Sort the movies based on the similarity scores in descending order
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

        # Get the scores of the top_n most similar movies excluding the first one (itself)
        sim_scores = sim_scores[1 : top_n + 1]

        # Get the indices of the recommended movies
        movie_indices = [i[0] for i in sim_scores]

        # Return the titles of the recommended movies
        return self.df["title"].iloc[movie_indices].tolist()
