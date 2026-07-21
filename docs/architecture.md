# System Architecture & Request Flows

This document details the detailed system flow diagrams, request lifecycles, and sequence diagrams of the **BITAtlas Workspace**.

---

## 1. Overall System Dataflow

The platform processes student actions through dedicated routing pipelines, loading credentials and compiling relevant contexts before invoking target engines.

```mermaid
graph TD
    Client["Student Browser / Client"]
    Router["FastAPI Route Handler"]
    ContextEngine["Smart Context Engine"]
    RAG["Hybrid RAG Engine"]
    LLM["Gemini 2.5 API"]
    Mongo[("MongoDB Database")]
    Chroma[("ChromaDB Vector Store")]

    Client --> Router
    Router --> ContextEngine
    ContextEngine --> Mongo
    ContextEngine --> RAG
    RAG --> Chroma
    
    ContextEngine --> LLM
    LLM --> ContextEngine
    ContextEngine --> Mongo
    Router --> Client
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

    Client->>Router: POST /chat (sessionId)
    Router->>Auth: decode token
    Auth-->>Router: return Student Payload
    
    Router->>Context: gather context
    activate Context
    
    par Query Database records
        Context->>DB: Get Student records
        DB-->>Context: return Academic records
    and Query Vector indexes
        Context->>Chroma: Retrieve Vector chunks
        Chroma-->>Context: return Vector Chunks
    end
    
    Context->>Context: Deduplication & Token Budget checks
    Context->>Gemini: generate response
    Gemini-->>Context: return Synthesized Answer
    
    Context->>DB: add message to history
    DB-->>Context: return Success
    
    Context-->>Router: return Formatted Payload
    deactivate Context
    
    Router-->>Client: return JSON Response
```

### 3.2 Website Crawling & Automatic Synchronization Sequence

```mermaid
sequenceDiagram
    autonumber
    participant Scheduler as Background Cron Scheduler
    participant Sync as Website Sync Manager
    participant Crawler as Web Scraper Service
    participant Mongo as MongoDB Collections
    participant Chroma as ChromaDB Vector Store

    Scheduler->>Sync: trigger sync cycle
    Sync->>Mongo: Find active websites
    Mongo-->>Sync: Return website records
    
    loop For each website
        Sync->>Crawler: crawl url
        Crawler->>Crawler: Extract & BeautifulSoup parse
        Crawler->>Crawler: Normalize content hash
        
        Sync->>Mongo: Compare newly generated hash
        
        alt Content Hash matches
            Sync->>Mongo: Update last checked
        else Content Hash differs
            Sync->>Chroma: Purge old vector chunks
            Sync->>Crawler: Segment text & generate embeddings
            Crawler-->>Chroma: Insert new vector chunks
            Sync->>Mongo: Update stored hash & Log Sync success
        end
    end
```
