#!/bin/bash

# Function to kill background processes on exit
cleanup() {
    echo "Stopping services..."
    kill $(jobs -p)
    exit
}

trap cleanup SIGINT SIGTERM

# Check if .venv exists
if [ -d ".venv" ]; then
    echo "Using virtual environment at .venv"
    PYTHON_CMD="./.venv/bin/python"
    UVICORN_CMD="./.venv/bin/uvicorn"
    STREAMLIT_CMD="./.venv/bin/streamlit"
else
    echo "Virtual environment not found at .venv. Assuming global path."
    PYTHON_CMD="python"
    UVICORN_CMD="uvicorn"
    STREAMLIT_CMD="streamlit"
fi

echo "Starting Backend..."
$UVICORN_CMD app.backend.main:app --reload --port 8000 &
BACKEND_PID=$!

echo "Waiting for Backend to start..."
sleep 5

echo "Starting Frontend..."
$STREAMLIT_CMD run app/frontend/ui.py &
FRONTEND_PID=$!

echo "Services running. Press Ctrl+C to stop."
wait $BACKEND_PID $FRONTEND_PID
