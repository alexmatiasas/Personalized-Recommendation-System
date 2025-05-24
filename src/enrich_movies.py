import pandas as pd
import requests
import time
import os
from pymongo import MongoClient
from dotenv import load_dotenv
# from urllib.parse import quote
import re

# Load environment variables from .env file
load_dotenv()

TMDB_API_KEY = os.getenv("TMDB_API_KEY")
MONGO_URI = os.getenv("MONGO_URI")

# Basic assertions
assert TMDB_API_KEY is not None, "❌ Missing the TMDB_API_KEY in .env"
assert MONGO_URI is not None, "❌ Missing MONGO_URI in .env"

# Conection to MongoDB
client = MongoClient(MONGO_URI)
db = client["movies_db"]
collection = db["movies_enriched"]

# Read movies dataset
movies_df = pd.read_csv("data/ml-1m/movies.csv")

# Function to clean the title
# Remove the year in parentheses at the end of the title
def clean_title(title):
    return re.sub(r"\s\(\d{4}\)$", "", title).strip()

# Function to search for a movie in TMDb
def search_movie(title):
    try:
        url = "https://api.themoviedb.org/3/search/movie"
        params = {
            "api_key": TMDB_API_KEY,
            "query": title,
            "language": "en-US",
            "include_adult": "false"
        }
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            if data["results"]:
                return data["results"][0]  # Takes the first result
        else:
            print(f"❌ TMDb error {response.status_code} for '{title}'")
    except Exception as e:
        print(f"⚠️ Excepción in search_movie('{title}'): {e}")
    return None

# Enrich and store movies in MongoDB
def enrich_and_store(movies, limit=100):
    for i, row in movies.head(limit).iterrows():
        title = row["title"]
        movie_id = int(row["movieId"])
        genres = row["genres"].split("|")

        if collection.find_one({"movieId": movie_id}):
            print(f"⏭️ It already exists in DB: {title}")
            continue

        query_title = clean_title(title)
        print(f"🔍 Searching: {query_title}")
        result = search_movie(query_title)

        if result:
            enriched = {
                "movieId": movie_id,
                "title": title,
                "genres": genres,
                "tmdb_id": result.get("id"),
                "overview": result.get("overview"),
                "poster_path": result.get("poster_path"),
                "release_date": result.get("release_date"),
                "popularity": result.get("popularity"),
                "vote_average": result.get("vote_average"),
            }
            collection.update_one({"movieId": movie_id}, {"$set": enriched}, upsert=True)
            print(f"✅ Saved: {title}")
        else:
            print(f"❌ Not found: {title}")

        time.sleep(0.25)  # avoid rate limit (40 req/10s)

# Execute the script (you can change the limit)
if __name__ == "__main__":
    print("🚀 Starting enrichment of movies dataset...")
    enrich_and_store(movies_df, limit=5000)
    print("✅ Finished process.")