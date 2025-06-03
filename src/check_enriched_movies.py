"""
Script to check enriched movies in MongoDB and export them to a CSV file.

This script connects to the MongoDB instance defined by the MONGO_URI in the .env file,
retrieves documents from the 'movies_enriched' collection with a non-empty 'overview',
prints the count and a few examples, and optionally exports the results to a CSV file.
"""

import os

import pandas as pd
from dotenv import load_dotenv
from pymongo import MongoClient

# Load environment variables
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")

# Establish connection with MongoDB
client = MongoClient(MONGO_URI)
db = client["movies_db"]
collection = db["movies_enriched"]

# Define query to select movies with a non-empty overview
query = {"overview": {"$exists": True, "$ne": ""}}
enriched_movies = collection.find(query)

# Count enriched movies
count = collection.count_documents(query)
print(f"✅ Movies enriched with overview: {count}")

# Display examples of enriched movie documents
print("\n🔍 Examples:")
for doc in enriched_movies.limit(5):
    print(f"🎬 {doc.get('title')} → {doc.get('overview')[:60]}...")

# Optional: export the filtered enriched movies to CSV
export = True
if export:
    print("\n💾 Exporting to data/processed/enriched_movies.csv...")
    docs = list(collection.find(query))
    df = pd.DataFrame(docs)
    if "_id" in df.columns:
        df.drop(columns=["_id"], inplace=True)
    os.makedirs("data/processed", exist_ok=True)
    df.to_csv("data/processed/enriched_movies.csv", index=False)
    print("✅ Completed export.")
