#!/usr/bin/env python3
"""
Script to initialize Ollama with the required model.
This script waits for Ollama to be ready and then pulls the llama3 model.
"""

import requests
import time
import subprocess
import sys

def wait_for_ollama(max_retries=30, delay=5):
    """Wait for Ollama service to be ready."""
    print("Waiting for Ollama to be ready...")
    
    for i in range(max_retries):
        try:
            response = requests.get("http://ollama:11434/api/tags", timeout=5)
            if response.status_code == 200:
                print("Ollama is ready!")
                return True
        except requests.exceptions.RequestException:
            pass
        
        print(f"Attempt {i+1}/{max_retries}: Ollama not ready yet, waiting {delay}s...")
        time.sleep(delay)
    
    print("Failed to connect to Ollama after maximum retries")
    return False

def pull_model(model_name="llama3"):
    """Pull the specified model using the Ollama API."""
    print(f"Pulling model: {model_name}")
    
    try:
        # Use Ollama API to pull the model
        response = requests.post(
            f"http://ollama:11434/api/pull",
            json={"name": model_name},
            stream=True,
            timeout=600  # 10 minutes timeout
        )
        
        if response.status_code == 200:
            print(f"Successfully pulled model: {model_name}")
            # Read the stream to completion
            for line in response.iter_lines():
                if line:
                    try:
                        data = line.decode('utf-8')
                        if data.strip():
                            # Parse the JSON response for progress updates
                            import json
                            try:
                                progress = json.loads(data)
                                if 'status' in progress:
                                    print(f"Status: {progress['status']}")
                            except:
                                pass
                    except:
                        pass
            return True
        else:
            print(f"Failed to pull model: HTTP {response.status_code}")
            return False
            
    except requests.exceptions.Timeout:
        print("Model pull timed out")
        return False
    except Exception as e:
        print(f"Error pulling model: {e}")
        return False

def main():
    """Main initialization function."""
    if not wait_for_ollama():
        sys.exit(1)
    
    if not pull_model():
        sys.exit(1)
    
    print("Ollama initialization completed successfully!")

if __name__ == "__main__":
    main()
