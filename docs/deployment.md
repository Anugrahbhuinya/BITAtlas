# Production Deployment Guide

This document describes environment configurations, Docker Compose orchestration models, reverse proxy configurations, and TLS/HTTPS setups to deploy the **BIT Mesra AI Workspace** to production.

---

## 1. Prerequisites

Before deploying the workspace, ensure the target virtual machine (VM) contains:
- **Docker Engine** (v24.0.0+)
- **Docker Compose** (v2.20.0+)
- An active domain name resolving to your server's public IP address.
- A valid **Google Gemini API Key**.

---

## 2. Production Environment Configurations

Create a production environment file (`.env`) in the project root:

```env
# Application Settings
ENV=production
DEBUG=False
PORT=8001

# Security Settings
SECRET_KEY="generate-a-64-character-cryptographic-hash-here"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Databases
MONGODB_URI="mongodb://production-mongo-ip-or-container:27017"
MONGODB_DB_NAME="bit_mesra_ai_agent_prod"
CHROMA_DB_PATH="/data/chroma_db"

# LLM Keys
GEMINI_API_KEY="AIzaSyYourProductionGeminiApiKeyHere"
GEMINI_MODEL="gemini-2.5-flash"
```

---

## 3. Docker Compose Configuration

Use the following `docker-compose.yml` to orchestrate backend, database, and client services:

```yaml
version: '3.8'

services:
  database:
    image: mongo:6.0
    container_name: bit-mesra-db
    restart: always
    volumes:
      - mongo-data:/data/db
    ports:
      - "27017:27017"
    networks:
      - bit-mesra-network

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: bit-mesra-api
    restart: always
    environment:
      - ENV=production
      - MONGODB_URI=mongodb://database:27017
      - MONGODB_DB_NAME=bit_mesra_ai_agent_prod
      - CHROMA_DB_PATH=/data/chroma_db
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - GEMINI_MODEL=gemini-2.5-flash
    volumes:
      - chroma-data:/data/chroma_db
      - uploads-data:/app/uploads
    ports:
      - "8001:8001"
    depends_on:
      - database
    networks:
      - bit-mesra-network

  frontend:
    image: nginx:alpine
    container_name: bit-mesra-client
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./frontend/dist:/usr/share/nginx/html
      - ./docker/nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - /etc/letsencrypt:/etc/letsencrypt:ro
    depends_on:
      - backend
    networks:
      - bit-mesra-network

networks:
  bit-mesra-network:
    driver: bridge

volumes:
  mongo-data:
  chroma-data:
  uploads-data:
```

---

## 4. Reverse Proxy & Nginx Configurations

Create Nginx server blocks to map client routes and forward API endpoints safely to the backend container:

```nginx
events { worker_connections 1024; }

http {
    include       mime.types;
    default_type  application/octet-stream;

    server {
        listen 80;
        server_name bit-mesra-ai.yourdomain.com;
        return 301 https://$host$request_uri;
    }

    server {
        listen 443 ssl;
        server_name bit-mesra-ai.yourdomain.com;

        ssl_certificate     /etc/letsencrypt/live/bit-mesra-ai.yourdomain.com/fullchain.pem;
        ssl_certificate_key /etc/letsencrypt/live/bit-mesra-ai.yourdomain.com/privkey.pem;
        
        ssl_protocols       TLSv1.2 TLSv1.3;
        ssl_ciphers         HIGH:!aNULL:!MD5;

        # Frontend Client SPA
        location / {
            root /usr/share/nginx/html;
            try_files $uri $uri/ /index.html;
            add_header X-Frame-Options "DENY";
            add_header X-Content-Type-Options "nosniff";
        }

        # Backend FastAPI Gateway
        location /api/ {
            proxy_pass http://backend:8001/;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection 'upgrade';
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Static uploads folder (Profile pictures)
        location /uploads/ {
            alias /app/uploads/;
            expires 7d;
        }
    }
}
```

---

## 5. Deployment Commands

1. **Build Static Assets**:
   ```bash
   cd frontend
   npm run build
   ```
2. **Build and Start Container Pool**:
   ```bash
   docker-compose up -d --build
   ```
3. **Verify running containers**:
   ```bash
   docker ps
   ```
4. **View Backend Logs**:
   ```bash
   docker logs -f bit-mesra-api
   ```
