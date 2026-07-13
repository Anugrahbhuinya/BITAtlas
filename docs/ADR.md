# Architecture Decision Records (ADR)

This document contains Architecture Decision Records (ADRs) explaining key engineering choices, framework selections, and design decisions for the **BIT Mesra AI Workspace**.

---

## ADR 1: FastAPI for Backend REST Services

### Context
We needed a backend REST API framework to process asynchronous student requests, handle static uploads, parse PDF documents, and orchestrate RAG pipelines.

### Decision
FastAPI was selected for the backend framework.
- **Rationale**:
  - Out-of-the-box support for async context loops (`asyncio`) allows non-blocking database queries and crawler loops.
  - Native integration with Pydantic v2 enforces automatic payload serialization and validation.
  - Generates comprehensive OpenAPI/Swagger documentation automatically.

---

## ADR 2: React and Vite for Frontend SPA Client

### Context
The user interface required a responsive, client-side digital command center with real-time streaming transitions, navigation canvas rendering, and reactive dashboards.

### Decision
React, paired with Vite as the build tool, was selected for the frontend.
- **Rationale**:
  - Vite offers extremely fast Hot Module Replacement (HMR) and optimized build bundles.
  - React's component model fits the feature-driven layout design, separating features (chat, academics, map) into self-contained directories.
  - Lightweight state management (Zustand) avoids Redux boilerplate.

---

## ADR 3: MongoDB for Transactional and Metadata Persistence

### Context
The database needed to store student profiles, schedules, checklists, and crawler audit logs.

### Decision
MongoDB was selected as the main database.
- **Rationale**:
  - NoSQL document structure simplifies storing and updating highly structured data models (such as custom timetable schedules or planner checklists).
  - High write throughput for logging crawler sync activities and chat sessions.
  - Async access driver (`motor`) integrates cleanly with FastAPI's event loop.

---

## ADR 4: ChromaDB for Semantic Document Vector Indexing

### Context
Retrieval-Augmented Generation (RAG) required indexing text segments from campus PDF manuals and website pages to support semantic search.

### Decision
ChromaDB was selected as the vector store database.
- **Rationale**:
  - Lightweight database that can run locally as a persistent embedded instance.
  - Easy integration with HuggingFace embedding client wrappers.
  - Metadata filtering allows the retriever to narrow queries down to specific documents or categories.

---

## ADR 5: Two-Stage Hybrid Retrieval Pipeline

### Context
Simple vector lookups often return irrelevant text segments or miss relevant details due to keyword mismatch, which degrades LLM generation.

### Decision
Implemented a Two-Stage Hybrid Retrieval Pipeline.
- **Rationale**:
  - **Stage 1 (ChromaDB Vector Retrieval)**: Cosmo-similarity fetches the top 10 relevant document segments using BAAI embeddings.
  - **Stage 2 (Cross-Encoder Re-ranking)**: Passes the user question and the retrieved chunks through the `ms-marco-MiniLM-L-6-v2` model to evaluate semantic matches, filtering out low-quality inputs.
  - This design reduces context token counts, improves prompt relevance, and prevents hallucinated responses.

---

## ADR 6: Google Gemini 2.5 Flash for Response Synthesis

### Context
The LLM engine must process long prompts containing student profiles, timetables, and retrieved documents, and synthesize grounded answers quickly.

### Decision
Google Gemini 2.5 Flash was selected as the core LLM engine.
- **Rationale**:
  - Highly optimized inference speeds (fast time-to-first-token).
  - Large context window to support dense prompts.
  - High accuracy in structured tool use and JSON parsing.
