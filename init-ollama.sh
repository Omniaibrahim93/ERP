#!/bin/bash

# Start Ollama in the background
ollama serve &

# Wait for Ollama to start
echo "Waiting for Ollama to start..."
while ! curl -s http://localhost:11434 > /dev/null; do
    sleep 1
done

# Pull a smaller model first
echo "Pulling smaller model for testing..."
ollama pull llama2  # or gemma:2b, mistral, etc.

# Optionally pull llama3 later
# ollama pull llama3 &

# Keep the container running
wait