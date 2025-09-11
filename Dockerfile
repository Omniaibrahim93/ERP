FROM python:3.13-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir --timeout=1000 --retries=5 -r requirements.txt

COPY . .

EXPOSE 8000
EXPOSE 8501

CMD ["/bin/bash", "-c", "uvicorn backend.main:app --host 0.0.0.0 --port 8000 & streamlit run frontend.py --server.port 8501 --server.enableCORS false --server.enableXsrfProtection false"]
