# System Architecture & Lifecycle Diagrams

This document details the request lifecycles, sequence interaction parameters, and flow pathways within the **BIT Mesra AI Workspace**.

---

## 1. Overall System Dataflow

The platform processes student actions through dedicated routing pipelines, loading credentials and compiling relevant contexts before invoking target engines.

```mermaid
graph TD
    Client[Student Browser / Client]
    Router[FastAPI Route Handler]
    ContextEngine[Smart Context Engine]
    RAG[Hybrid RAG Engine]
    LLM[Gemini 2.5 API]
    Mongo[(MongoDB Database)]
    Chroma[(ChromaDB Vector Store)]

    Client -->|"1. Chat Request (JWT Claim)"| Router
    Router -->|"2. Assemble Context"| ContextEngine
    ContextEngine -->|"3. Retrieve Profile, Schedule, Checklist"| Mongo
    ContextEngine -->|"4. Retrieve Semantic Chunks"| RAG
    RAG -->|"5. Embed & Retrieve"| Chroma
    
    ContextEngine -->|"6. Deduplicate & Merge Context"| ContextEngine
    ContextEngine -->|"7. Send Structured Prompt"| LLM
    LLM -->|"8. Return Grounded Answer"| ContextEngine
    ContextEngine -->|"9. Save Thread History"| Mongo
    Router -->|"10. Return Response Stream"| Client
```

---

## 2. Request Lifecycle Flows

### 2.1 Chat Request Flow (Smart Context Pipeline)
When a query is dispatched to the `/chat` route:
1. **Request Received**: The router gateway intercepts the HTTP POST request.
2. **Session Verification**: The system decodes the JWT signature to resolve the active student's session profile.
3. **Intent Detection**: The keyword classifier matches the query terms to determine if the query represents an academic question, navigation check, or general FAQ lookup.
4. **Parallel Gathering**: `ContextOrchestrator` calls active providers concurrently using `asyncio.gather`:
   - `ProfileProvider` queries MongoDB for registration credentials.
   - `TimetableProvider` fetches course times.
   - `RAGProvider` embeds the query and fetches semantic chunks from ChromaDB.
5. **Deduplication**: `FuzzyDeduplicator` matches text segments (Jaccard > 0.85) to purge redundant pages.
6. **Token Compression & Budgeting**: If token limits are exceeded (max `3,500`), the budget manager trims lower-priority chunks.
7. **Synthesis**: The prompt builder packages the structured prompt and sends it to Gemini 2.5 Flash.
8. **Logging & Return**: The generated response is saved to the MongoDB thread history, and returned to the frontend.

---

## 3. Sequence Interaction Diagrams

### 3.1 End-to-End Chat Query Sequence

```mermaid
sequenceDiagram
    autonumber
    actor Client as Student React Client
    participant Router as FastAPI Router Gateway
    participant Auth as Auth Token Validator
    participant Context as Smart Context Engine
    participant DB as MongoDB
    participant Chroma as ChromaDB Index
    participant Gemini as Gemini LLM Engine

    Client->>Router: POST /chat (message, sessionId, Authorization Header)
    Router->>Auth: decode_access_token()
    Auth-->>Router: return Student Payload
    
    Router->>Context: gather_context(message, student_id)
    activate Context
    
    par Query Database records
        Context->>DB: Get Student Profile, Schedules, & Attendance Logs
        DB-->>Context: return Academic Records
    and Query Vector indexes
        Context->>Chroma: Retrieve Vector document chunks (Cos-Sim)
        Chroma-->>Context: return Vector Chunks & Meta
    end
    
    Context->>Context: Fuzzy Deduplication & Token Budget Validation
    Context->>Gemini: generate_response(ContextPrompt)
    Gemini-->>Context: return Synthesized Answer
    
    Context->>DB: add_message_to_history(sessionId, role="assistant", content)
    DB-->>Context: return Success
    
    Context-->>Router: return Formatted Response Payload
    deactivate Context
    
    Router-->>Client: return JSON Response (with Citations & Telemetry)
```

### 3.2 Website crawling & Automatic Synchronization Sequence

```mermaid
sequenceDiagram
    autonumber
    participant Scheduler as Background Cron Scheduler
    participant Sync as Website Sync Manager
    participant Crawler as Web Scraper Service
    participant Mongo as MongoDB Collections
    participant Chroma as ChromaDB Vector Store

    Scheduler->>Sync: trigger_sync_cycle()
    Sync->>Mongo: Find all active websites (sync_enabled=true)
    Mongo-->>Sync: Return website records
    
    loop For each website
        Sync->>Crawler: crawl_url(url)
        Crawler->>Crawler: Extract HTML & BeautifulSoup parse
        Crawler->>Crawler: Normalize content (strip Date, Session, Dynamic properties)
        Crawler->>Crawler: Generate content SHA-256 hash
        
        Sync->>Mongo: Compare newly generated hash with stored database hash
        
        alt Content Hash matches (No Changes)
            Sync->>Mongo: Update last_checked timestamp & Log Sync status "Unchanged"
        else Content Hash differs (Updates Detected)
            Sync->>Chroma: Purge old vector chunks by source ID
            Sync->>Crawler: Segment text into chunks & generate HuggingFace embeddings
            Crawler-->>Chroma: Insert new vector chunks
            Sync->>Mongo: Update stored hash, last_checked, & Log Sync audit trail "Updated"
        end
    end
```
