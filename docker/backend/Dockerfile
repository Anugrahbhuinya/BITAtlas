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

# Copy RAG vector database and data files
COPY chroma_db /app/chroma_db
COPY data /app/data
COPY data /data

# Create required directories if needed
RUN mkdir -p /app/uploads

# Prevent HuggingFace tokenizer parallelism issues
ENV TOKENIZERS_PARALLELISM=false

# Expose default port
EXPOSE 8080

# Start FastAPI application with single worker for cloud memory constraints
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 1"]
