# Deployment and Setup Guide

This document describes how to setup, run, configure, and deploy the **BIT Mesra AI Assistant** (Enterprise Knowledge Platform) in both development and production environments.

---

## 1. Prerequisites

Before running the application, make sure the following dependencies are installed on your environment:

* **OS:** Windows / Linux / macOS
* **Python:** Python 3.10 or 3.11
* **Node.js:** Node.js 18.x or higher (with npm package manager)
* **MongoDB:** MongoDB Community Server (v6.0 or higher) running locally or a MongoDB Atlas connection URI.
* **C++ Build Tools:** Required for compiling compilation dependencies of ChromaDB (e.g., visual studio build tools on Windows, `build-essential` on Linux).

---

## 2. Environment Variables

Create a `.env` file inside the `backend` folder to configure database and authentication properties:

```ini
# Core Server Configuration
PORT=8001
HOST=0.0.0.0

# MongoDB Configuration
MONGO_URI=mongodb://localhost:27017/bit_mesra_assistant

# ChromaDB Configuration
CHROMA_PERSIST_DIR=./data/chromadb

# AI & LLM Service Keys
GEMINI_API_KEY=your_gemini_api_key_here

# JWT Authentication Configs
JWT_SECRET=your_super_secret_jwt_signature_key_here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=120

# Website Synchronization Configs
WEBSITE_SYNC_ENABLED=True
WEBSITE_SYNC_INTERVAL_MINUTES=60
MAX_CONCURRENT_WEBSITE_SYNCS=3
RESPECT_ROBOTS_TXT=False

# Content Normalizer Configurations
ENABLE_NORMALIZED_HASH=True
IGNORE_DATES=True
IGNORE_TIMESTAMPS=True
IGNORE_COUNTERS=True
IGNORE_SESSION_IDS=True
IGNORE_EXTRA_WHITESPACE=True
```

---

## 3. Local Development Setup

### 3.1 Backend Server Setup (FastAPI)
1. Navigate to the backend folder:
   ```bash
   cd backend
   ```
2. Create and activate a python virtual environment:
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On Linux / macOS:
   source venv/bin/activate
   ```
3. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Start the FastAPI development server:
   ```bash
   uvicorn app.main:app --reload --port 8001
   ```
   *The server will boot, automatically seeding the default administrator account (`admin` / `admin123`) and triggering the background website synchronization thread.*

### 3.2 Frontend Web Setup (Vite + React)
1. Navigate to the frontend folder:
   ```bash
   cd frontend
   ```
2. Install npm dependencies:
   ```bash
   npm install
   ```
3. Start the React development server:
   ```bash
   npm run dev
   ```
4. Access the web interface at `http://localhost:5180`.
   - Admin Workspace: `/admin/login`

---

## 4. Production Deployment

### 4.1 Production Stack Recommendation
* **Web Server:** Nginx (acting as a reverse proxy SSL terminator).
* **API Runner:** Gunicorn with Uvicorn workers (`gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app`).
* **Database Hosting:** MongoDB Atlas (for managed replication and backups).
* **Vector Store Hosting:** ChromaDB deployed on a standalone container or running locally on local persistent folders (backed up periodically).
* **Hosting Platform:** AWS EC2, DigitalOcean Droplet, or Google Compute Engine.

### 4.2 Docker Configuration (Future-Ready Containerization)

To containerize the application, you can use the following layout:

#### Backend Dockerfile (`backend/Dockerfile`)
```dockerfile
FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8001

CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:8001", "app.main:app"]
```

#### Frontend Dockerfile (`frontend/Dockerfile`)
```dockerfile
# Build stage
FROM node:18-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# Production stage
FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

---

## 5. Common Troubleshooting

### ChromaDB C++ Build Errors
- **Symptom:** Python complains about failing to compile `hnswlib` or `chromadb` during `pip install`.
- **Solution:** Make sure compile build tools are installed. On Windows, install *Desktop development with C++* through Visual Studio Installer. On Linux, run `sudo apt-get install build-essential python3-dev`.

### "Event loop is closed" on MongoDB/Motor calls
- **Symptom:** Logs display warnings about Motor trying to perform collection database operations on a closed loop.
- **Solution:** This is caused by running database operations inside separate threads or nested async tasks. Avoid instantiating new loops during standard FastAPI lifespan executions. Ensure all operations share the main event loop context.

### Gemini API rate limit blocks
- **Symptom:** Ingestion or chats return `429 Too Many Requests` when using Gemini.
- **Solution:** Reduce chunk sizes or insert delays when batching multiple PDF document ingestions concurrently.

---

## 6. Hardened Production Deployment Checklist & Monitoring Verification

When preparing to launch the hardened application in production:
1. **Set Configuration Mode**: Define `APP_ENV=production` in the environment variables block. This disables debug traceback screens, enables OWASP-compliant security headers, and enforces standard rate limits.
2. **Setup Log Aggregation**: Structured JSON logs are written by the FastAPI server to stdout. Configure Fluentd or log agents to parse and route these payloads to your centralized SIEM.
3. **Configure Health Inquiries**:
   - Set up ping configurations to hit `/health` every 10 seconds.
   - Configure gateway ready checks to poll `/ready` to monitor MongoDB, ChromaDB, and Gemini API statuses.
4. **Enforce Rate Limits**: Apply firewall rate limits (e.g., in Nginx reverse-proxy settings) that match the internal FastAPI rate limits (`RATE_LIMIT_CHAT_LIMIT`, `RATE_LIMIT_ADMIN_LIMIT`).

