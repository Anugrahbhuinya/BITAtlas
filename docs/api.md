# REST API Reference Documentation

This document describes all REST API endpoints exposed by the **BITAtlas Assistant** backend server.

---

## Endpoint Base URL
```text
http://localhost:8001
```

---

## 1. Authentication Module

### Student Registration
* **Method:** `POST`
* **Route:** `/api/auth/register`
* **Purpose:** Registers a new student account.
* **Authentication Required:** No
* **Request Body (JSON):**
  ```json
  {
    "email": "student@bitmesra.ac.in",
    "password": "strongpassword123",
    "roll_number": "BE/10001/21",
    "name": "Jane Doe",
    "department": "Computer Science",
    "semester": 5,
    "section": "A"
  }
  ```
* **Response (JSON):**
  ```json
  {
    "message": "Student registered successfully",
    "student_id": "student_uuid_5566"
  }
  ```
* **Status Codes:**
  * `201 Created`: Registration successful.
  * `400 Bad Request`: Email or Roll Number already registered.

### Student Login
* **Method:** `POST`
* **Route:** `/api/auth/login`
* **Purpose:** Authenticates student credentials and returns access and refresh JWT tokens.
* **Authentication Required:** No
* **Request Body (JSON):**
  ```json
  {
    "email": "student@bitmesra.ac.in",
    "password": "strongpassword123"
  }
  ```
* **Response (JSON):**
  ```json
  {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "student": {
      "id": "student_uuid_5566",
      "name": "Jane Doe",
      "email": "student@bitmesra.ac.in"
    }
  }
  ```
* **Status Codes:**
  * `200 OK`: Login successful.
  * `401 Unauthorized`: Invalid credentials.

---

## 2. AI Assistant & Chat History

### Process Chat Query
* **Method:** `POST`
* **Route:** `/chat`
* **Purpose:** Processes user queries using hybrid RAG, intent routing, and Gemini 2.5 Flash.
* **Authentication Required:** No (Optional bearer token will resolve student profile context)
* **Headers:** `Authorization: Bearer <access_token>` (Optional)
* **Request Body (JSON):**
  ```json
  {
    "message": "What class do I have tomorrow at 10 AM?",
    "sessionId": "chat_session_8899"
  }
  ```
* **Response (JSON):**
  ```json
  {
    "type": "success",
    "answer": "According to your timetable, you have Machine Learning (L-302) with Prof. K. Sharma tomorrow at 10:00 AM.",
    "citations": [],
    "diagnostics": {
      "elapsed_ms": 120.5,
      "tokens_used": 450,
      "intent": "academic",
      "debug_rag": null
    }
  }
  ```

### Get Session Conversation History
* **Method:** `GET`
* **Route:** `/chat/history/{sessionId}`
* **Purpose:** Fetches message logs for a specific conversation session identifier.
* **Authentication Required:** No
* **Response (JSON):**
  ```json
  {
    "sessionId": "chat_session_8899",
    "messages": [
      {
        "sender": "user",
        "text": "Hi, what is my timetable today?",
        "timestamp": "2026-07-13T19:00:00Z"
      },
      {
        "sender": "bot",
        "text": "You have Machine Learning at 10 AM...",
        "timestamp": "2026-07-13T19:00:02Z"
      }
    ]
  }
  ```

### Delete Session Conversation History
* **Method:** `DELETE`
* **Route:** `/chat/history/{sessionId}`
* **Purpose:** Clears session history entries from MongoDB.
* **Authentication Required:** No
* **Response (JSON):**
  ```json
  {
    "status": "success",
    "message": "Chat history cleared successfully"
  }
  ```

---

## 3. Academics Workspace

### Get Academic Dashboard Data
* **Method:** `GET`
* **Route:** `/api/academics/dashboard`
* **Purpose:** Aggregates timetable classes, attendance summaries, pending tasks, calendar events, and rule-based warnings.
* **Authentication Required:** Yes (JWT access token)
* **Response (JSON):**
  ```json
  {
    "today_classes": [
      {
        "id": "class_ml_01",
        "subject": "Machine Learning",
        "instructor": "Prof. K. Sharma",
        "room": "L-302",
        "start_time": "10:00",
        "end_time": "10:50"
      }
    ],
    "attendance_summary": {
      "overall_percentage": 78.5,
      "risk_subjects_count": 0
    },
    "planner_summary": {
      "pending_tasks_count": 3
    },
    "insights": [
      "Your attendance in ML is 78.5%. You are safe to miss 1 more class."
    ]
  }
  ```

### Import Timetable PDF Scans
* **Method:** `POST`
* **Route:** `/api/academics/timetable/import/pdf`
* **Purpose:** Parses scanned sheets using Gemini Vision and writes class schedules to the student's timetable record.
* **Authentication Required:** Yes (JWT access token)
* **Request Body:** `multipart/form-data`
  - `file` (Binary PDF or image file, required)
* **Response (JSON):**
  ```json
  {
    "status": "success",
    "classes_imported_count": 12
  }
  ```

---

## 4. Administrative Document & Knowledge Management

### List Indexed Documents
* **Method:** `GET`
* **Route:** `/api/admin/documents`
* **Purpose:** Returns a list of all indexed PDF documents.
* **Authentication Required:** Yes (Admin JWT Token)
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
* **Authentication Required:** Yes (Admin JWT Token)
* **Request Body:** `multipart/form-data`
  * `file` (Binary PDF file, required)
* **Response:** Streaming Response (`application/x-ndjson`)

---

## 5. Website Crawler & Synchronization

### Index New Webpage URL
* **Method:** `POST`
* **Route:** `/api/admin/websites`
* **Purpose:** Crawls a URL, extracts text, normalizes content, generates embeddings, and indexes chunks.
* **Authentication Required:** Yes (Admin JWT Token)
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

### List Indexed Websites
* **Method:** `GET`
* **Route:** `/api/admin/websites`
* **Purpose:** Returns all indexed websites with crawling and hashing details.
* **Authentication Required:** Yes (Admin JWT Token)

### Trigger Manual Sync Update Check
* **Method:** `POST`
* **Route:** `/api/admin/websites/{id}/sync`
* **Purpose:** Triggers a crawl check immediately to verify content updates.
* **Authentication Required:** Yes (Admin JWT Token)
* **Response (JSON):**
  ```json
  {
    "status": "Updated",
    "message": "Website updated.",
    "chunks": 5
  }
  ```

---

## 6. System Health & Diagnostics

### Get System Health Status
* **Method:** `GET`
* **Route:** `/health`
* **Purpose:** Basic system diagnostics checking if backend services are up.
* **Authentication Required:** No
* **Response (JSON):**
  ```json
  {
    "status": "ok",
    "timestamp": "2026-07-13T19:30:00Z"
  }
  ```
* **Status Codes:**
  * `200 OK`: Healthy.
  * `503 Service Unavailable`: Internal dependency failure.
