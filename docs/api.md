# API Reference Documentation

This document describes all API endpoints exposed by the **BIT Mesra AI Assistant** backend server.

---

## Endpoint Base URL
```text
http://localhost:8001
```

---

## 1. Authentication Module

### Login Admin User
* **Method:** `POST`
* **Route:** `/api/admin/login`
* **Purpose:** Authenticates admin dashboard users and returns a JWT access token.
* **Authentication Required:** No
* **Request Body (JSON):**
  ```json
  {
    "username": "admin",
    "password": "your_password"
  }
  ```
* **Response (JSON):**
  ```json
  {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "username": "admin"
  }
  ```
* **Status Codes:**
  * `200 OK`: Successful authentication.
  * `401 Unauthorized`: Incorrect username or password.

### Logout Admin User
* **Method:** `POST`
* **Route:** `/api/admin/logout`
* **Purpose:** Logs out the currently authenticated admin and records the event log.
* **Authentication Required:** Yes (JWT Bearer Token)
* **Response (JSON):**
  ```json
  {
    "status": "success",
    "message": "Logged out successfully"
  }
  ```
* **Status Codes:**
  * `200 OK`: Success.
  * `401 Unauthorized`: Missing or invalid admin token.

---

## 2. Chat & Assistant Module

### Send Chat Query
* **Method:** `POST`
* **Route:** `/chat`
* **Purpose:** Processes user queries using hybrid RAG, intent routing, and Gemini 2.5 Flash.
* **Authentication Required:** No
* **Request Body (JSON):**
  ```json
  {
    "message": "Where is the computer science department located?",
    "sessionId": "session-1234-abcd"
  }
  ```
* **Response (JSON):**
  ```json
  {
    "type": "success",
    "answer": "The Department of Computer Science & Engineering is located in the Main Building on the ground floor, near the central library.",
    "citations": [
      {
        "source": "BIT Mesra Map Info",
        "text": "The Computer Science Department is situated on the Ground Floor of the Main Building.",
        "score": 0.89
      }
    ]
  }
  ```
* **Status Codes:**
  * `200 OK`: Success.

### Get Chat Conversation History
* **Method:** `GET`
* **Route:** `/chat/history/{sessionId}`
* **Purpose:** Fetches message logs for a specific conversation session identifier.
* **Authentication Required:** No
* **Path Parameters:**
  * `sessionId` (string, required)
* **Response (JSON):**
  ```json
  {
    "sessionId": "session-1234-abcd",
    "messages": [
      {
        "role": "user",
        "content": "Hi, where is the CSE department?"
      },
      {
        "role": "assistant",
        "content": "The Computer Science & Engineering department is located in the main building..."
      }
    ]
  }
  ```
* **Status Codes:**
  * `200 OK`: History retrieved successfully.
  * `500 Internal Server Error`: Database query failed.

### Delete Chat Conversation History
* **Method:** `DELETE`
* **Route:** `/chat/history/{sessionId}`
* **Purpose:** Clears session history entries from MongoDB.
* **Authentication Required:** No
* **Path Parameters:**
  * `sessionId` (string, required)
* **Response (JSON):**
  ```json
  {
    "status": "success",
    "message": "Chat history cleared successfully"
  }
  ```

---

## 3. PDF Ingestion & Document Management

### List PDF Documents
* **Method:** `GET`
* **Route:** `/api/admin/documents`
* **Purpose:** Returns a list of all indexed PDF documents.
* **Authentication Required:** Yes (JWT Bearer Token)
* **Response (JSON):**
  ```json
  {
    "documents": [
      {
        "id": "doc-9876",
        "title": "admission_brochure.pdf",
        "chunk_count": 48,
        "word_count": 12400,
        "indexed_at": "2026-06-27T12:00:00Z"
      }
    ],
    "total": 1
  }
  ```

### Upload PDF Document
* **Method:** `POST`
* **Route:** `/api/admin/documents/upload`
* **Purpose:** Uploads a PDF file, extracts text, chunks it, and indexes it. Progress states are streamed back to the client.
* **Authentication Required:** Yes (JWT Bearer Token)
* **Request Body:** `multipart/form-data`
  * `file` (Binary PDF file, required)
  * `overwrite` (boolean, optional query parameter, defaults to `false`)
* **Response:** Streaming Response (`application/x-ndjson`)
* **Example Stream Elements:**
  ```json
  {"status": "Extracting text...", "progress": 10}
  {"status": "Chunking pages...", "progress": 40}
  {"status": "Generating embeddings...", "progress": 70}
  {"status": "Completed", "progress": 100, "title": "brochure.pdf", "chunk_count": 12}
  ```
* **Status Codes:**
  * `200 OK`: Ingestion stream initiated.
  * `400 Bad Request`: Non-PDF file provided.
  * `429 Too Many Requests`: Triggered if upload rate limits are exceeded.

### Re-index PDF Document
* **Method:** `POST`
* **Route:** `/api/admin/documents/{doc_id}/reindex`
* **Purpose:** Reloads text and vectors for an already stored PDF document. Streams progress states back to the client.
* **Authentication Required:** Yes (JWT Bearer Token)
* **Path Parameters:**
  * `doc_id` (string, required)
* **Response:** Streaming Response (`application/x-ndjson`)

### Delete PDF Document
* **Method:** `DELETE`
* **Route:** `/api/admin/documents/{doc_id}`
* **Purpose:** Purges the document record from MongoDB and deletes its vectors from ChromaDB.
* **Authentication Required:** Yes (JWT Bearer Token)
* **Path Parameters:**
  * `doc_id` (string, required)
* **Response (JSON):**
  ```json
  {
    "status": "success",
    "message": "Document and associated vectors deleted successfully."
  }
  ```
* **Status Codes:**
  * `200 OK`: Document deleted.
  * `404 Not Found`: Document not found.

---

## 4. Website Ingestion Module

### Index New Website Page
* **Method:** `POST`
* **Route:** `/api/admin/websites`
* **Purpose:** Crawls a URL, extracts text, normalizes content, generates embeddings, and indexes chunks.
* **Authentication Required:** Yes (JWT Bearer Token)
* **Request Body (JSON):**
  ```json
  {
    "url": "https://bitmesra.ac.in/edudepartment/1/70"
  }
  ```
* **Response (JSON):**
  ```json
  {
    "status": "Completed",
    "message": "Successfully indexed: Department of Computer Science",
    "website_id": "site_70",
    "url": "https://bitmesra.ac.in/edudepartment/1/70",
    "title": "Department of Computer Science",
    "domain": "bitmesra.ac.in",
    "word_count": 680,
    "chunk_count": 4
  }
  ```
* **Status Codes:**
  * `200 OK`: Page indexed.
  * `400 Bad Request`: Invalid URL format.

### List Indexed Websites
* **Method:** `GET`
* **Route:** `/api/admin/websites`
* **Purpose:** Returns all indexed websites with crawling and hashing details.
* **Authentication Required:** Yes (JWT Bearer Token)
* **Response (JSON):**
  ```json
  {
    "websites": [
      {
        "id": "site_70",
        "url": "https://bitmesra.ac.in/edudepartment/1/70",
        "domain": "bitmesra.ac.in",
        "title": "Department of Computer Science",
        "word_count": 680,
        "chunk_count": 4,
        "content_hash": "65f886f788...",
        "normalized_content_hash": "3be7234fe8...",
        "status": "Indexed",
        "sync_enabled": true,
        "sync_status": "Healthy",
        "last_checked": "2026-06-27T17:00:00Z",
        "last_changed": "2026-06-27T15:00:00Z"
      }
    ],
    "total": 1
  }
  ```

### Get Website Details
* **Method:** `GET`
* **Route:** `/api/admin/websites/{id}`
* **Purpose:** Retrieves detailed metadata for a specific website page.
* **Authentication Required:** Yes (JWT Bearer Token)
* **Path Parameters:**
  * `id` (string, required)

### Delete Website Page Index
* **Method:** `DELETE`
* **Route:** `/api/admin/websites/{id}`
* **Purpose:** Removes website metadata from MongoDB and purges vector chunks from ChromaDB.
* **Authentication Required:** Yes (JWT Bearer Token)
* **Path Parameters:**
  * `id` (string, required)

### Reindex Website Page
* **Method:** `POST`
* **Route:** `/api/admin/websites/{id}/reindex`
* **Purpose:** Re-scrapes the HTML content and regenerates embeddings for the selected page.
* **Authentication Required:** Yes (JWT Bearer Token)
* **Path Parameters:**
  * `id` (string, required)

---

## 5. Website Synchronization Module

### Trigger Manual Sync Update Check
* **Method:** `POST`
* **Route:** `/api/admin/websites/{id}/sync`
* **Purpose:** Triggers a crawl check immediately to verify content updates.
* **Authentication Required:** Yes (JWT Bearer Token)
* **Path Parameters:**
  * `id` (string, required)
* **Response (No meaningful change):**
  * Status: `200 OK` (PlainTextResponse: `"No changes detected."`)
* **Response (Updated):**
  ```json
  {
    "status": "Updated",
    "message": "Website updated.",
    "chunks": 5
  }
  ```

### Trigger Bulk Sync Check
* **Method:** `POST`
* **Route:** `/api/admin/websites/sync-all`
* **Purpose:** Initiates update checks for all active websites concurrently.
* **Authentication Required:** Yes (JWT Bearer Token)
* **Response (JSON):**
  ```json
  {
    "checked": 12,
    "updated": 2,
    "unchanged": 9,
    "failed": 1,
    "duration": "14.5s"
  }
  ```

### Toggle Auto-Sync Switch
* **Method:** `POST`
* **Route:** `/api/admin/websites/{id}/toggle-sync`
* **Purpose:** Enables or disables automated background synchronization checks.
* **Authentication Required:** Yes (JWT Bearer Token)
* **Path Parameters:**
  * `id` (string, required)
* **Request Body (JSON):**
  ```json
  {
    "sync_enabled": false
  }
  ```
* **Response (JSON):**
  ```json
  {
    "status": "success",
    "sync_enabled": false
  }
  ```

### Get Sync Summary Statistics
* **Method:** `GET`
* **Route:** `/api/admin/websites/stats`
* **Purpose:** Returns synchronization counters for the dashboard panels.
* **Authentication Required:** Yes (JWT Bearer Token)
* **Response (JSON):**
  ```json
  {
    "indexed_websites": 12,
    "healthy_websites": 10,
    "pending_updates": 1,
    "failed_websites": 1,
    "today_crawls": 48,
    "today_updates": 3,
    "avg_crawl_time_ms": 1240,
    "avg_chunk_count": 6
  }
  ```

### Get Detailed System Scheduler Status
* **Method:** `GET`
* **Route:** `/api/admin/websites/status`
* **Purpose:** Fetches running status configs of the background scheduler loop.
* **Authentication Required:** Yes (JWT Bearer Token)
* **Response (JSON):**
  ```json
  {
    "scheduler_running": true,
    "interval_minutes": 60,
    "active_syncs_count": 0,
    "websites_status": [
      {
        "id": "site_70",
        "url": "https://bitmesra.ac.in/edudepartment/1/70",
        "title": "Department of Computer Science",
        "domain": "bitmesra.ac.in",
        "word_count": 680,
        "chunk_count": 4,
        "indexed_at": "2026-06-27T12:00:00Z",
        "sync_status": "Healthy",
        "sync_enabled": true,
        "last_checked": "2026-06-27T17:00:00Z",
        "last_changed": "2026-06-27T15:00:00Z",
        "last_error": null,
        "check_count": 4,
        "successful_checks": 4,
        "failed_checks": 0,
        "normalized_content_hash": "3be7234fe8..."
      }
    ]
  }
  ```

---

## 6. Audit & History Module

### Get Crawl History Log
* **Method:** `GET`
* **Route:** `/api/admin/websites/history`
* **Purpose:** Fetches audit history records for all crawler events.
* **Authentication Required:** Yes (JWT Bearer Token)
* **Response (JSON):**
  ```json
  {
    "history": [
      {
        "id": "log-uuid-1122",
        "website_id": "site_70",
        "url": "https://bitmesra.ac.in/edudepartment/1/70",
        "started_at": "2026-06-27T17:00:00Z",
        "completed_at": "2026-06-27T17:00:01Z",
        "duration_ms": 1150,
        "status": "success",
        "content_changed": false,
        "old_hash": "65f886f788...",
        "new_hash": "b2c9a928e1...",
        "old_chunks": 4,
        "new_chunks": 4,
        "message": "Only volatile content changed.",
        "raw_hash_changed": true,
        "normalized_hash_changed": false,
        "reindex_triggered": false,
        "reason": "Only volatile content changed."
      }
    ],
    "total": 1
  }
  ```

### Get Specific Page Crawl History
* **Method:** `GET`
* **Route:** `/api/admin/websites/history/{website_id}`
* **Purpose:** Fetches logs filter restricted to the selected website page document.
* **Authentication Required:** Yes (JWT Bearer Token)
* **Path Parameters:**
  * `website_id` (string, required)

---

## 7. Dashboard & System Metrics

### Get General Dashboard Statistics
* **Method:** `GET`
* **Route:** `/api/admin/dashboard` (also matches `/api/admin/statistics`)
* **Purpose:** Fetches general counters (total vector chunks, documents count, website pages count, failed logs rate).
* **Authentication Required:** Yes (JWT Bearer Token)

### Get System Health Status
* **Method:** `GET`
* **Route:** `/api/admin/system-status`
* **Purpose:** Performs health check tests on MongoDB client connection and local persistent ChromaDB client file write paths.
* **Authentication Required:** Yes (JWT Bearer Token)

### Get Admin Activity Logs
* **Method:** `GET`
* **Route:** `/api/admin/activity`
* **Purpose:** Fetches login, upload, and deletion event audits for security verification.
* **Authentication Required:** Yes (JWT Bearer Token)

### Get Admin Settings Configurations
* **Method:** `GET`
* **Route:** `/api/admin/settings`
* **Purpose:** Fetches active directory sizes and config settings (token timeout, max files allowed).
* **Authentication Required:** Yes (JWT Bearer Token)

---

## 8. Navigation & Diagnostics Module

### Get All Navigation Graph Nodes
* **Method:** `GET`
* **Route:** `/api/navigation/nodes`
* **Purpose:** Retrieves all spatial nodes (buildings, facilities, landmarks, rooms) from the MongoDB graph collection.
* **Authentication Required:** No
* **Response (JSON):**
  ```json
  [
    {
      "id": "node_lib",
      "name": "Central Library",
      "node_type": "building",
      "latitude": 23.4150,
      "longitude": 85.4400,
      "metadata": {
        "building_code": "LIB",
        "description": "Central Library of BIT Mesra"
      }
    }
  ]
  ```

### Calculate Dijkstra Route
* **Method:** `POST`
* **Route:** `/api/navigation/route`
* **Purpose:** Generates path coordinate points, distances, ETA durations, and walking instructions between source and destination.
* **Authentication Required:** No
* **Request Body (JSON):**
  ```json
  {
    "source_id": "main_gate",
    "destination_id": "node_lib",
    "accessibility_mode": false
  }
  ```
* **Response (JSON):**
  ```json
  {
    "route_found": true,
    "distance_meters": 780.0,
    "eta_minutes": 10,
    "path": [[23.4082, 85.4452], [23.4110, 85.4430], [23.4150, 85.4400]],
    "instructions": ["Walk straight from Main Gate...", "Turn right past Central Lawn..."]
  }
  ```

### Compile Academic Context
* **Method:** `GET`
* **Route:** `/api/academics/context`
* **Purpose:** Compiles full student context (profile, today/tomorrow classes, attendance alerts, checklist tasks) for the prompt builder. Used for developer diagnostics.
* **Authentication Required:** Yes (JWT Bearer Token)

