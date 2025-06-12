"""
config.py

Configuration module for environment variables and project settings.

- Loads values from a `.env` file using `python-dotenv`.
- Exposes variables like DATA_MODE and DB_PATH to other backend components.
"""

import os

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Application mode: 'demo' or 'full'
DATA_MODE = os.getenv("DATA_MODE", "full").lower()

# Base data directory depending on mode
DATA_DIR = "data/demo" if DATA_MODE == "demo" else "data/ml-1m"

# Path to SQLite database
DB_PATH = f"{DATA_DIR}/recommendations.db"

# You can add other constants like model paths, API keys, etc.
