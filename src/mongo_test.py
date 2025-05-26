import os

from dotenv import load_dotenv
from pymongo import MongoClient

# Load environment variables from .env file
load_dotenv()

# Obtain MongoDB URI from environment variables
MONGO_URI = os.getenv("MONGO_URI")

# Conect to MongoDB
client = MongoClient(MONGO_URI)

# Access the database and collection
db = client["movies_db"]
collection = db["movies_enriched"]

# Test document to insert
test_doc = {
    "movieId": 9999,
    "title": "Fake Movie (2099)",
    "genres": ["Sci-Fi", "Fantasy"],
    "overview": "This is a test document inserted to verify connection.",
}

# Insert the test document
collection.insert_one(test_doc)
print("✅ Document inserted successfully.")

# Verify the insertion
result = collection.find_one({"movieId": 9999})
print("🔍 Retrieved document:")
print(result)
