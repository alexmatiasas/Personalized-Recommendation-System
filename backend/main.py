"""
main.py

Main entrypoint for the FastAPI application.

- Initializes the FastAPI app instance.
- Adds the project root to `sys.path` so modules in `src/` can be imported.
- Includes all API routes from the endpoints router.
"""

import os
import sys

# Add src/ to the path to allow absolute imports from the project
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi import FastAPI

from backend.api import endpoints

# Initialize the FastAPI app
app = FastAPI()

# Include API routes
app.include_router(endpoints.router)
