FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy backend dependencies
COPY backend/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend application
COPY backend/ .

# Copy RAG vector database
COPY chroma_db /app/chroma_db

# Copy knowledge/data files
COPY data /app/data

# Create required directories if needed
RUN mkdir -p /app/uploads

# Render assigns PORT dynamically
EXPOSE 8000

# Start FastAPI application
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port $PORT"]