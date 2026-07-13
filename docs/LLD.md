# Low-Level Design (LLD)

This document provides a detailed low-level design overview of the modules, folder relationships, component trees, and class structures of the **BIT Mesra AI Workspace**.

---

## 1. Directory Structure Mappings

### 1.1 Backend Layout
```text
backend/
├── app/
│   ├── auth/                  # JWT signature verifiers & router handlers
│   ├── context/               # Academic context provider files
│   ├── core/                  # DB clients, exceptions handlers, and settings config
│   ├── models/                # Pydantic schema validation objects
│   ├── repositories/          # MongoDB Motor CRUD operations
│   ├── routes/                # FastAPI controller endpoints
│   ├── security/              # Security middlewares & rate limit configs
│   ├── services/              # Core domain services
│   │   ├── llm/               # Prompt assembly & Gemini API wrappers
│   │   ├── rag/               # ChromaDB vector store, embedders & rerankers
│   │   └── websites/          # BeautifulSoup crawlers & scheduler threads
│   └── main.py                # Main app startup
```

### 1.2 Frontend Layout
```text
frontend/
├── src/
│   ├── app/                   # Layout wrappers, global styles & providers
│   ├── features/              # Feature modules
│   │   ├── academics/         # Dashboard panels, timetables & attendance grids
│   │   ├── auth/              # Registration, login & context managers
│   │   ├── chat/              # Chat window & bubble widgets
│   │   └── map/               # Campus navigation map canvas
│   ├── shared/                # Common widgets (Sidebar, Navbar)
│   └── App.tsx                # Client route mapping definitions
```

---

## 2. Backend Design Layers

```text
  [ FastAPI Route Controllers ]
               │
               ▼  (Pydantic Type Validation)
       [ Service Layer ]
               │
      ┌────────┴────────┐
      ▼                 ▼
[ Repository Layer ]  [ RAG / AI Services ]
      │                 │
      ▼                 ▼
 [ MongoDB ]       [ ChromaDB / Gemini ]
```

### 2.1 API Route Layer
- Exposes REST endpoints to processes requests.
- Leverages Pydantic validation schemas to cast parameter shapes before dispatching.
- *Examples*: `app/routes/chat.py`, `app/routes/academics.py`, `app/routes/admin.py`.

### 2.2 Service Layer
- Encapsulates the transactional business logic.
- Resolves computations (e.g. safe leaves percentages) and integrates multiple resource dependencies.
- *Examples*: `app/services/academic_service.py`, `app/services/websites/crawler.py`.

### 2.3 Repository Layer
- Abstract interface containing MongoDB client execution pools.
- Uses the `motor` async driver to run CRUD tasks.
- *Examples*: `app/repositories/student_repository.py`, `app/repositories/attendance_repository.py`.

### 2.4 Database & Vector Layer
- Initializes connection instances for MongoDB and ChromaDB.
- Indexes required database collections on startup.
- *Examples*: `app/core/database.py`, `app/services/rag/vector_store.py`.

---

## 3. Core Module Technical Breakdown

### 3.1 Smart Context Engine (`app/context/`)
- **`ContextOrchestrator`**: Orchestrates providers based on user intent. Runs `gather_context` to concurrently retrieve:
  - `ProfileProvider`: Resolves name, roll number, and department metadata.
  - `TimetableProvider`: Resolves scheduled classes for today/tomorrow.
  - `AttendanceProvider`: Fetches attendance scores and Bunk safety margins.
  - `PlannerProvider`: Gathers active checklist deadlines.
  - `RAGProvider`: Conducts semantic searches across ChromaDB.
- **`FuzzyDeduplicator`**: Tokenizes incoming chunks and computes Jaccard overlaps. Purges duplicates exceeding a `0.85` similarity coefficient.
- **`TokenBudgetManager`**: Loops through prioritized context blocks. If the token count exceeds `3,500`, it cuts chunks from the bottom to prevent model overflows.

### 3.2 Hybrid RAG Engine (`app/services/rag/`)
- **`VectorStore`**: Integrates persistent ChromaDB client collections.
- **`EmbeddingManager`**: Resolves text chunks into 384-dimensional arrays using HuggingFace's `BAAI/bge-small-en-v1.5` transformer model.
- **`Reranker`**: Uses `sentence-transformers/ms-marco-MiniLM-L-6-v2` as a Cross-Encoder to compute relevance scores against user query terms.

### 3.3 Website Synchronization Scheduler (`app/services/websites/`)
- **`SyncScheduler`**: Utilizes an hourly async loop checking website states.
- **`ContentNormalizer`**: Applies regular expression cleansers to strip dynamic elements (e.g., date stamps, session IDs, tracking pixels, whitespaces) before computing SHA-256 content hashes.
- **`Crawler`**: Crawls targets respecting rate parameters and `robots.txt` specifications.

---

## 4. Frontend Component Tree

```text
App (Routes Configuration)
 └── MainLayout (Sidebar, Top App Bar)
      ├── DashboardPage (Bento Layout, Insights Panel, Timeline Summary)
      ├── ChatPage (Welcome Hero State / Conversation Scroll Container)
      │     ├── MessageBubble (Bot Avatar / Citations / Diagnostics Expandable)
      │     └── ChatInput (Textarea Input / Voice Mic & Send Controls)
      ├── AcademicsPage (Timetable grid / Attendance Registers / Planner list)
      └── CampusMapPage (Leaflet Map Render / Routing panel)
```

- **State Management**:
  - `AuthContext`: Tracks JWT token payload properties and active user profiles.
  - `PreferencesContext`: Persists desktop layout collapse configurations and dark mode preferences.
  - `useChat`: Stores current conversation messages and active speech synthesis status.

---

## 5. Security & Exception Middleware

- **`SecurityHeadersMiddleware`**: Mounts OWASP headers to intercept Cross-Site Scripting (XSS), framing (Clickjacking), and sniffing parameters.
- **`ai_guard.py`**: Intercepts chat queries using regex parameters to identify prompt injection attacks before context prompt assembly.
- **`GlobalExceptionHandler`**: Captures unhandled Python runtime errors or model validation failures and maps them to clean HTTP payloads without exposing trace logs.
