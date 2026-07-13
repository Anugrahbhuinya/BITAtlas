# Database Reference Documentation

This document describes the schema designs, collection structures, vector schemas, index properties, and storage strategies for the **BIT Mesra AI Workspace**.

---

## 1. MongoDB Collections

MongoDB stores transactional student details, timetable configurations, attendance registers, checklist planner tasks, admin credentials, and crawl sync audit logs.

### 1.1 `students`
Stores credentials, registration profiles, and authentication keys.
- **Index**: `email` (Unique, ascending), `roll_number` (Unique, ascending).
- **Structure**:
  ```json
  {
    "_id": "ObjectId",
    "email": "student@bitmesra.ac.in",
    "password_hash": "$2b$12$...",
    "roll_number": "BE/10001/21",
    "name": "Jane Doe",
    "role": "student",
    "profile": {
      "department": "Computer Science",
      "semester": 5,
      "section": "A"
    },
    "created_at": "ISODate"
  }
  ```

### 1.2 `timetables`
Maintains daily class schedules.
- **Index**: `student_id` (Unique, ascending).
- **Structure**:
  ```json
  {
    "_id": "ObjectId",
    "student_id": "student_uuid_5566",
    "semester": 5,
    "classes": [
      {
        "id": "class_ml_01",
        "subject": "Machine Learning",
        "instructor": "Prof. K. Sharma",
        "room": "L-302",
        "day_of_week": "Monday",
        "start_time": "10:00",
        "end_time": "10:50"
      }
    ]
  }
  ```

### 1.3 `attendance_records`
Stores course attendance statistics.
- **Index**: `student_id` (Ascending).
- **Structure**:
  ```json
  {
    "_id": "ObjectId",
    "student_id": "student_uuid_5566",
    "subject_id": "sub_ml_101",
    "subject_name": "Machine Learning",
    "total_conducted": 12,
    "total_attended": 10,
    "percentage": 83.33
  }
  ```

### 1.4 `attendance_logs`
Audit history records log details for each class session.
- **Index**: `attendance_record_id` (Ascending).
- **Structure**:
  ```json
  {
    "_id": "ObjectId",
    "attendance_record_id": "attendance_uuid_9900",
    "class_date": "ISODate",
    "status": "Present",
    "remarks": "Regular Lecture"
  }
  ```

### 1.5 `planner_tasks`
Checklist tasks and personal reminders.
- **Index**: `student_id` (Ascending).
- **Structure**:
  ```json
  {
    "_id": "ObjectId",
    "student_id": "student_uuid_5566",
    "title": "Submit Lab Report",
    "description": "Prepare PDF of Experiment 4",
    "category": "assignments",
    "priority": "high",
    "due_date": "ISODate",
    "completed": false
  }
  ```

### 1.6 `sessions` (Chat History)
Maintains conversation logs for active AI sessions.
- **Index**: `sessionId` (Unique, ascending).
- **Structure**:
  ```json
  {
    "_id": "ObjectId",
    "sessionId": "chat_session_8899",
    "messages": [
      {
        "sender": "user",
        "text": "Where is the CSE department?",
        "timestamp": "ISODate"
      },
      {
        "sender": "bot",
        "text": "The computer science department is...",
        "timestamp": "ISODate"
      }
    ]
  }
  ```

### 1.7 `websites`
Stores crawled website configuration and hashing details.
- **Index**: `url` (Unique, ascending).
- **Structure**:
  ```json
  {
    "_id": "ObjectId",
    "url": "https://bitmesra.ac.in/edudepartment/1/70",
    "title": "Department of Computer Science",
    "domain": "bitmesra.ac.in",
    "content_hash": "65f886f788...",
    "normalized_content_hash": "3be7234fe8...",
    "sync_enabled": true,
    "sync_status": "Healthy",
    "last_checked": "ISODate",
    "last_changed": "ISODate"
  }
  ```

### 1.8 `website_crawl_history`
Maintains audit logs for crawler sync runs.
- **Index**: `website_id` (Ascending).
- **Structure**:
  ```json
  {
    "_id": "ObjectId",
    "website_id": "site_uuid_7788",
    "started_at": "ISODate",
    "completed_at": "ISODate",
    "status": "success",
    "content_changed": false,
    "old_hash": "65f886f788...",
    "new_hash": "65f886f788...",
    "message": "Only volatile content changed."
  }
  ```

---

## 2. ChromaDB Vector Collections

ChromaDB holds the 384-dimensional document chunk vector records.

### 2.1 `knowledge_base`
- **Embedding Dimensions**: `384`
- **Metric**: Cosine Similarity.
- **Metadata Fields**:
  - `doc_id` (maps to PDF document ID or Webpage ID)
  - `source` (file name or webpage URL)
  - `source_type` (`pdf` or `website`)
  - `text` (raw text segment)
  - `page` (PDF page index, if applicable)
  - `indexed_at` (Ingestion timestamp)
