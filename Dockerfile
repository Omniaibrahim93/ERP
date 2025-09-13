FROM python:3.9-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir --timeout=1000 --retries=5 -r requirements.txt

# Copy the rest of the application code
COPY . .

# Initialize the database
RUN python3 database/init_db.py

# Expose the ports for FastAPI (backend) and Streamlit (frontend)
EXPOSE 8000
EXPOSE 8501

# The command to run the application
CMD ["./start.sh"]
