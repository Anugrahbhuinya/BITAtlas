# Changelog

All notable changes to the **BIT Mesra AI Assistant** project will be documented in this file.

The project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [2.1.0] - 2026-07-07
### Added
- **Smart Context Engine Pipeline (Phase 10B):** A modular pipeline that gathers, sanitizes, and budgets prompt context.
- **Provider Selector:** Selects context providers (`system`, `profile`, `conversation`, `workspace`, `navigation`, `rag`) depending on intent routing and authorization status.
- **Concurrent Context Gathering:** Concurrently executes active providers using `asyncio.gather` for optimal performance.
- **Priority-based Scoring:** Scores context items based on source importance, classification confidence, and time-decay factors.
- **Fuzzy Deduplication:** Filters duplicate and near-duplicate documents (Jaccard similarity > 0.85) to save tokens and prevent LLM confusion.
- **Dynamic Context Compressor:** Trims RAG document lists and reduces conversation history turns depending on context severity levels (LOW, MEDIUM, HIGH, AUTO).
- **Token Budget Manager:** Guarantees final prompts stay under the 3,500 token limit using priority-based section trimming.
- **Diagnostics Tracing:** Exposes provider execution latencies, token counts, and deduplication stats in developer diagnostics payload.
- **Unit and Integration Tests:** Added a test suite of 22 tests verifying models, selector, prioritizer, deduplicator, merger, compressor, budget manager, and full route API integrations.

## [2.0.0] - 2026-06-27
### Added
- **Automatic Website Synchronization (Phase 6B):** Background cron scheduler executing check cycles to keep indexed webpages fresh.
- **Intelligent Change Detection:** Added a pre-normalizer service ([content_normalizer.py](file:///c:/Users/ASUS/bit-mesra-ai-agent/backend/app/services/websites/content_normalizer.py)) using regex rules to ignore volatile date timestamps, copyright years, hit counters, session variables, and whitespaces when computing content hashes.
- **Concurrency Locks:** Limits concurrent background crawler sync runs to 3 using an asynchronous Semaphore queue.
- **Crawl Audit Trail:** Added a MongoDB collection `website_crawl_history` storing detailed logs about crawl checks, raw change flags, normalized change flags, duration speeds, and decision reasons.
- **Admin Crawl History Screen:** Added a dedicated page in the admin portal to browse, search, and filter crawl event histories.
- **Dashboard Synchronization Metrics:** Responsive metrics display at the top of the webpage details dashboard (total pages, failure rates, healthy sources, today's crawl logs, average chunks sizes, and duration speeds).
- **Manual Actions:** Inline buttons to trigger immediate sync checks ("Sync Now") or run bulk synchronizations ("Sync All Pages").

### Changed
- **FastAPI Lifespan Hooks:** Migrated legacy startup events to modern `lifespan` context manager managers to initialize scheduler threads.

### Fixed
- **React Rendering Error:** Resolved uncaught JSX rendering error ("Objects are not valid as a React child") caused by passing raw Lucide Icon components.

---

## [1.5.0] - 2026-06-15
### Added
- **Website Ingestion Pipeline (Phase 6A):** Administrative capability to index and query public webpages directly.
- **Advanced HTML Extraction:** Developed parser modules leveraging BeautifulSoup to strip boilerplate (script, style, noscript, svg, iframe) while prioritizing semantic elements (main, article, section, div, tables).
- **Table Cell Formatting:** Improved crawler to aggregate table grids using cell delimiters (`|`) rather than split lines.
- **URL Normalizer:** Normalizes URL path structures to avoid duplicate index storage.

---

## [1.4.0] - 2026-05-20
### Added
- **PDF Knowledge base ingestion (Phase 5):** Added support for indexing dynamic PDF manuals.
- **Recursive Splitting:** Chunks text using recursive boundary checks (paragraphs, lines, words) to preserve context.
- **Source Citations:** Attaches page numbers, document titles, and scores to citations.

---

## [1.3.0] - 2026-04-10
### Added
- **Enterprise Admin Portal (Phase 4):** Dashboard UI allowing administrators to check system performance and manage files.
- **JWT Admin Authentication:** Secures backend API configurations and document management.
- **Activity logs:** Audit log database recording admin logins, uploads, and deletions.

---

## [1.2.0] - 2026-03-01
### Added
- **Hybrid RAG Core:** Integrates ChromaDB vector store matching with LangChain retrieval helpers.
- **Semantic Embeddings:** Generates vector representations using HuggingFace's `BAAI/bge-small-en-v1.5` embedder.

---

## [1.1.0] - 2026-01-15
### Added
- **Chat Memory:** Extended conversational context using MongoDB storage collections.

---

## [1.0.0] - 2025-12-01
### Added
- **Initial Release:** Universal Search matching system mapping campus building coordinates, hostel names, department directories, and FAQs.
