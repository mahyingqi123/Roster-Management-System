#!/bin/bash

# --- Backend Setup and Run Script ---

# 1. Navigate to the backend directory
echo "Navigating to the backend directory..."
cd backend || { echo "Error: 'backend' directory not found."; exit 1; }

# 2. Create and activate virtual environment
ENV_DIR=".venv"
echo "Checking for virtual environment in $ENV_DIR..."

if [ ! -d "$ENV_DIR" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$ENV_DIR"
fi

echo "Activating virtual environment..."
source "$ENV_DIR/bin/activate" 
# Note: For strict Windows compatibility, you'd need to check the OS here.

# 3. Install dependencies
echo "Installing/updating dependencies from requirements.txt..."
pip install -r requirements.txt || { echo "Error: Dependency installation failed."; exit 1; }

# 4. Run the API using uvicorn
echo "Starting FastAPI application on port 8000..."
# Using exec ensures that signals (like Ctrl+C) are correctly passed to uvicorn
exec uvicorn app.main:app --reload --port 8000