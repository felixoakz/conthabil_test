#!/bin/bash
set -e

# Run database migrations/table creation
python -m src.conthabil.initialize_db

# Start the FastAPI application
uvicorn main:app --host 0.0.0.0 --port 8000
