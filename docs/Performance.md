# Performance Benchmarks & Latency Guidelines

This document details the latency targets, concurrency models, model preloading strategies, and context trimming optimizations implemented in the **BITATLAS Workspace**.

---

## 1. Concurrency Model (`asyncio.gather`)

To minimize request overhead, the backend orchestrates context providers concurrently:
- **Sequential Execution**: Querying database records (profile, schedules, attendance, planners) and ChromaDB vectors sequentially would result in a cumulative latency of `400ms` to `650ms`.
- **Concurrent Execution**: Utilizing asynchronous execution pools (`asyncio.gather`) reduces this overhead to the speed of the slowest single I/O bound query (typically vector lookup, which completes in `< 80ms`).

---

## 2. Latency Baselines & P95 Targets

The following P95 limits are enforced across backend stages under a concurrent load of 50 requests/sec:

| Pipeline Stage | Metric Checked | P95 Target | Optimization Mechanism |
| :--- | :--- | :--- | :--- |
| **API Middleware Gateway** | JWT claims validation and timing | `< 5ms` | In-memory token checks and stateless middleware filters. |
| **Dijkstra Navigation Route** | Map routing solver | `< 15ms` | Adjacency list graph representations and cached node coordinates. |
| **ChromaDB Vector Retrieve** | Stage 1 semantic search | `< 80ms` | HNSW indices and preloaded local dense embedding models. |
| **Cross-Encoder Rerank** | Stage 2 relevance re-ranking | `< 150ms` | Preloaded `ms-marco-MiniLM-L-6-v2` transformer model. |
| **Smart Context Gathering** | Concurrent DB & vector collection | `< 120ms` | `asyncio.gather` non-blocking pools and MongoDB indexing. |
| **Gemini LLM Stream** | Time-to-first-token | `< 250ms` | Native Google streaming endpoint integrations. |

---

## 3. Memory & Model Preloading Optimization

To prevent first-request lazy loading latency penalties (which can exceed `4.5s` on cold starts):
- **Lifespan Loader**: The FastAPI startup context manager loads the HuggingFace Embeddings pipeline and Cross-Encoder re-ranker weights directly into system memory.
- **Pre-warmed GPU/CPU Pipelines**: Pre-warm processes are executed on container startup, making the system immediately ready to handle queries at production speed.

---

## 4. Context Budget Compressor

To keep token overhead low and avoid model context degradation:
- **Fuzzy Deduplicator**: Compares chunk similarities using Jaccard checks. Eliminating duplicates exceeding `0.85` similarity coefficient reduces context payloads by up to 40%.
- **Budget Trimming**: Trims history logs and vector snippets dynamically to stay strictly under the 3,500 token limit.
