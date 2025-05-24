from pymongo import MongoClient
from dotenv import load_dotenv
import os
import pandas as pd

# Load environment variables from .env file
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")

# Conection to MongoDB
client = MongoClient(MONGO_URI)
db = client["movies_db"]
collection = db["movies_enriched"]

# Movies with overview not null
query = {"overview": {"$exists": True, "$ne": None, "$ne": ""}}
enriched_movies = collection.find(query)

# Count enriched movies
count = collection.count_documents(query)
print(f"✅ Movies enriched with overview: {count}")

# Show some examples
print("\n🔍 Examples:")
for doc in enriched_movies.limit(5):
    print(f"🎬 {doc.get('title')} → {doc.get('overview')[:60]}...")

# Export to CSV
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