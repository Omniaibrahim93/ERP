#!/bin/bash

# Initialize Ollama with the required model
echo "Initializing Ollama..."
python3 init_ollama.py

if [ $? -ne 0 ]; then
    echo "Failed to initialize Ollama. Exiting..."
    exit 1
fi

echo "Starting the application..."

# Start the application
uvicorn backend.main:app --host 0.0.0.0 --port 8000 &
streamlit run frontend.py --server.port 8501 --server.enableCORS false --server.enableXsrfProtection false

wait
