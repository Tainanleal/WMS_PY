#!/bin/bash
# Activate the virtual environment
source .venv/bin/activate

# Run the FastAPI server with Uvicorn
# It listens on all available network interfaces (0.0.0.0)
# The port is determined by the $PORT environment variable, defaulting to 8000
echo "Starting server on port ${PORT:-8000}..."
uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --reload
