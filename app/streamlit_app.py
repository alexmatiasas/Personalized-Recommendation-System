import os
import sys

# Add src/ to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from src.collaborative_filtering import CollaborativeFilteringRecommender
from src.content_based import ContentBasedRecommender
from src.ui.components import generate_genre_html, generate_rating_html
from src.ui.helpers import load_similarity, normalize_title, save_similarity
from src.ui.tmdb import get_movie_trailer_url

load_dotenv()
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
base_url = "https://image.tmdb.org/t/p/w500/"


@st.cache_resource
def load_similarity_cached(path: str = "models/user_similarity.joblib"):
    return load_similarity(path)


st.title("🎬 Movie Recommender System")

# Sidebar options
option = st.sidebar.selectbox(
    "Choose Recommender:", ("Content-Based", "Collaborative Filtering")
)

if option == "Content-Based":
    # Load content-based recommender
    movies_df = pd.read_csv("data/processed/enriched_movies_clean.csv")

    @st.cache_resource
    def fit_recommender():
        recommender = ContentBasedRecommender(movies_df)
        recommender.fit()
        return recommender

    st.markdown("---")

    movie_options = movies_df["title"].apply(normalize_title)
    movie_labels = movie_options.apply(lambda x: x[0])
    movie_title = st.selectbox("Choose a Movie Title", sorted(movie_labels.unique()))

    if not movie_title:
        st.warning("⚠️ Please select a movie first.")
        st.stop()

    # Find the true movie row based on the normalized title
    # (since dropdown is normalized, match accordingly)
    selected_movie = movies_df[
        movies_df["title"].apply(lambda t: normalize_title(t)[0] == movie_title)
    ].iloc[0]
    st.markdown("### 🎞️ Selected Movie")
    with st.container():
        # Try to extract year for display if present
        year = ""
        if "(" in selected_movie["title"] and ")" in selected_movie["title"]:
            try:
                year = selected_movie["title"].split("(")[1].replace(")", "")
            except Exception:
                year = ""
        try:
            genres = (
                eval(selected_movie["genres"])
                if isinstance(selected_movie["genres"], str)
                else selected_movie["genres"]
            )
        except Exception:
            genres = []
        genre_html = generate_genre_html(genres)
        score = selected_movie["vote_average"]
        score_html = generate_rating_html(score)
        st.markdown(
            """
            <div style='background-color:#1a1a40; padding:20px; border-radius:12px; margin-bottom:25px; display: flex; align-items: flex-start; box-shadow: 0 6px 12px rgba(0,0,0,0.3);'>
                <img src="{}" style="width:140px; height:auto; border-radius:5px; margin-right:25px;" />
                <div style="flex:1;">
                    <h3 style='margin-bottom:5px; color:#efb810;'>🎬 {}</h3>
                    <p style='margin-top:0; color:#bbb; font-size:14px;'>📅 {}</p>
                    <div style='margin:5px 0;'>
                        <strong style='color:#e0e0e0;'>Genres:</strong>
                        {}
                    </div>
                    <p style='margin:5px 0; color:#e0e0e0;'>{}</p>
                    <div style='margin:5px 0;'>
                        <strong style='color:#e0e0e0;'>Rating:</strong> {}
                    </div>
                    {}
                    <p style='margin-top:10px;'>
                      <a href="https://www.themoviedb.org/search?query={}" target="_blank" style="color:#00ffff;">More Info ↗</a>
                    </p>
                </div>
            </div>
            """.format(
                base_url + selected_movie["poster_path"],
                normalize_title(selected_movie["title"])[0],
                year,
                genre_html,
                selected_movie["overview"],
                score_html,
                (
                    "<p style='font-size:12px; color:gray; margin:0;'>Based on TMDB user ratings</p>"
                    if score_html != 0
                    else ""
                ),
                normalize_title(selected_movie["title"])[0].replace(" ", "%20"),
            ),
            unsafe_allow_html=True,
        )
    trailer_url = get_movie_trailer_url(normalize_title(selected_movie["title"])[0])
    if trailer_url:
        st.markdown("### 🎬 Watch Trailer")
        st.video(trailer_url)

    top_n = st.slider("How many recommendations?", min_value=1, max_value=10, value=5)
    if st.button("Get Recommendations", key="cb_button"):
        recommender = fit_recommender()
        recs = recommender.get_recommendations(selected_movie["title"], top_n=top_n)
        st.subheader("🎯 Recommended Movies")
        # Include poster_path for image display
        recommended_df = movies_df[movies_df["title"].isin(recs)][
            ["title", "genres", "overview", "poster_path", "vote_average", "popularity"]
        ]

        for _, row in recommended_df.iterrows():
            title_normalized = normalize_title(row["title"])[0].replace(" ", "%20")
            with st.container():
                title, year = normalize_title(row["title"])
                try:
                    genres = (
                        eval(row["genres"])
                        if isinstance(row["genres"], str)
                        else row["genres"]
                    )
                except Exception:
                    genres = []
                genre_html = generate_genre_html(genres)
                score = row["vote_average"]
                score_html = generate_rating_html(score)
                # Compose the card HTML, with More Info link inside the card div
                card_html = """
                    <div style='background-color:#111111; padding:15px; border-radius:10px; margin-bottom:20px; display: flex; align-items: flex-start; box-shadow: 0 4px 8px rgba(0,0,0,0.25); transition: transform 0.2s;'>
                        <img src="{}" style="width:120px; height:auto; border-radius:5px; margin-right:15px;" />
                        <div style="flex:1;">
                            <h4 style='margin-bottom:0px; color:#efb810;'>🎬 {}</h4>
                            <p style='margin-top:2px; color:#bbb; font-size:14px;'>📅 {}</p>
                            <div style='margin:5px 0;'>
                                <strong style='color:#ccc;'>Genres:</strong>
                                {}
                            </div>
                            <p style='margin:5px 0; color:#ccc;'>{}...</p>
                            <div style='margin:5px 0;'>
                                <strong style='color:#ccc;'>Rating:</strong> {}
                            </div>
                            {}
                            <p style='margin-top:10px;'>
                              <a href="https://www.themoviedb.org/search?query={}" target="_blank" style="color:#00ffff;">More Info ↗</a>
                            </p>
                        </div>
                    </div>
                """.format(
                    base_url + row["poster_path"],
                    title,
                    year,
                    genre_html,
                    row["overview"][:300],
                    score_html,
                    (
                        "<p style='font-size:12px; color:gray; margin:0;'>Based on TMDB user ratings</p>"
                        if score_html != 0
                        else ""
                    ),
                    title.replace(" ", "%20"),
                )
                st.markdown(card_html, unsafe_allow_html=True)
                trailer_url = get_movie_trailer_url(title)
                if trailer_url:
                    st.video(trailer_url)

else:
    max_user_id = 10000  # default fallback
    try:
        ratings_df = pd.read_csv("data/ml-1m/ratings.csv")
        max_user_id = ratings_df["userId"].max()
    except Exception:
        st.warning(
            "⚠️ Could not load user data to determine max user ID. Default max=10000 used."
        )

    user_id = st.number_input(
        "Enter User ID", min_value=1, max_value=int(max_user_id), step=1
    )

    if st.button("Get Recommendations", key="cf_button"):
        if not os.path.exists("data/ml-1m/ratings.csv"):
            st.error(
                "⚠️ Ratings data file not found. Please ensure 'data/ml-1m/ratings.csv' exists."
            )
            st.stop()
        recommender = CollaborativeFilteringRecommender(
            ratings_path="data/ml-1m/ratings.csv",
            enriched_movies_path="data/processed/enriched_movies_clean.csv",
        )
        recommender.load_data()

        # Ensure models/ directory exists
        os.makedirs("models", exist_ok=True)

        similarity_matrix = load_similarity_cached()
        if similarity_matrix is None:
            st.warning("⚠️ Precomputed matrix not found, computing similarity...")
            recommender.compute_user_similarity()
            save_similarity(recommender.similarity_matrix)
            st.success("✅ Similarity matrix computed and saved")
        else:
            recommender.similarity_matrix = similarity_matrix
            st.info("🔁 Loaded precomputed similarity matrix from disk")

        if user_id not in recommender.ratings_df["userId"].unique():
            st.warning(f"User ID {user_id} not found in dataset.")
            st.stop()
        recs = recommender.recommend_movies_for_user(user_id)
        movies_df = pd.read_csv("data/processed/enriched_movies_clean.csv")
        recommended_df = movies_df[movies_df["movieId"].isin(recs)][
            ["title", "genres", "overview", "poster_path", "vote_average", "popularity"]
        ]

        st.subheader("🎯 Recommended Movies")
        for _, row in recommended_df.iterrows():
            title, year = normalize_title(row["title"])
            try:
                genres = (
                    eval(row["genres"])
                    if isinstance(row["genres"], str)
                    else row["genres"]
                )
            except Exception:
                genres = []
            genre_html = generate_genre_html(genres)
            score = row["vote_average"]
            score_html = generate_rating_html(score)
            title_normalized = title.replace(" ", "%20")
            card_html = """
                <div style='background-color:#111111; padding:15px; border-radius:10px; margin-bottom:20px; display: flex; align-items: flex-start; box-shadow: 0 4px 8px rgba(0,0,0,0.25); transition: transform 0.2s;'>
                    <img src="{}" style="width:120px; height:auto; border-radius:5px; margin-right:15px;" />
                    <div style="flex:1;">
                        <h4 style='margin-bottom:0px; color:#efb810;'>🎬 {}</h4>
                        <p style='margin-top:2px; color:#bbb; font-size:14px;'>📅 {}</p>
                        <div style='margin:5px 0;'>
                            <strong style='color:#ccc;'>Genres:</strong>
                            {}
                        </div>
                        <p style='margin:5px 0; color:#ccc;'>{}...</p>
                        <div style='margin:5px 0;'>
                            <strong style='color:#ccc;'>Rating:</strong> {}
                        </div>
                        {}
                        <p style='margin-top:10px;'>
                          <a href="https://www.themoviedb.org/search?query={}" target="_blank" style="color:#00ffff;">More Info ↗</a>
                        </p>
                    </div>
                </div>
            """.format(
                base_url + row["poster_path"],
                title,
                year,
                genre_html,
                row["overview"][:300],
                score_html,
                (
                    "<p style='font-size:12px; color:gray; margin:0;'>Based on TMDB user ratings</p>"
                    if score_html != 0
                    else ""
                ),
                title_normalized,
            )
            st.markdown(card_html, unsafe_allow_html=True)
            trailer_url = get_movie_trailer_url(title)
            if trailer_url:
                st.video(trailer_url)
