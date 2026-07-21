# Testing & QA Reference Documentation

This document describes the testing frameworks, automated verification commands, manual QA checklists, and performance latency stress testing setups for the **BITAtlas Workspace**.

---

## 1. Test Architecture Hierarchy

```text
       [ Quality Dashboard Metrics ]
                     │
     ┌───────────────┼───────────────┐
     ▼               ▼               ▼
[ Unit Tests ] [ Integration ] [ Performance ]
 (pytest-async)   (mock DBs)   (semaphore-stress)
```

- **Unit Testing**: Tests logical boundaries of individual modules (e.g. JWT token signatures, timetable imports, and BeautifulSoup HTML crawl parsers).
- **Integration Testing**: Validates end-to-end API exchanges, verifying coordinate mappings and schedule integrations against mock database adapters.
- **Performance Benchmarks**: Stresses the asynchronous context pipeline to measure average throughput (req/s) and P95 response times.
- **Quality Dashboard Compiler**: Aggregates coverage ratios, test execution outputs, and static analysis outputs into a unified report.

---

## 2. Running Automated Tests

### 2.1 Run Backend Pytest Suite
From the `backend/` directory:
```bash
python -m pytest
```

### 2.2 Run Full Validation Suite (Orchestrated)
Executes all unit, integration, and workflow runs:
```bash
python tests/test_runner.py --all
```

### 2.3 Run Performance Stress Benchmarks
Measures execution latencies and concurrency throughput limits:
```bash
python tests/performance_runner.py
```

### 2.4 Compile Quality Dashboard
Generates a quality index report containing coverage and static analysis logs:
```bash
python tests/quality_dashboard.py
```

---

## 3. Manual Release Candidate (RC) QA Checklist

Perform this verification checklist before production release:

### 3.1 Authentication & Workspace Setup
- [ ] **Registration**: Verify registering a student with valid `bitmesra.ac.in` domain details succeeds; invalid emails fail.
- [ ] **Login**: Validate login yields valid JWT tokens; incorrect credentials raise an HTTP 401 error.
- [ ] **Remember Session**: Check that reloading the dashboard after logging in with "Remember session" active keeps the student logged in.
- [ ] **Workspace Setup**: Confirm a new student is redirected to select their semester, department, and section.

### 3.2 AI Assistant & History
- [ ] **Welcoming Hero**: Confirm that when first opening the chat assistant page, the welcome section and capability cards are displayed.
- [ ] **Hero Fade**: Verify that sending a message fades the hero section away, replacing it with the message bubble stream.
- [ ] **History deduplication**: Refresh the page during a conversation and confirm that chat bubble lines load correctly with no duplicate messages.
- [ ] **Diagnostics Collapse**: Verify the diagnostics observability console is collapsed by default under `▼ Diagnostics`.

### 3.3 Dynamic Ingestion (Admin)
- [ ] **PDF Upload**: Upload a campus PDF brochure. Check that extraction progress states stream in real-time.
- [ ] **Crawling / Sync**: Crawler sync detects dynamic changes. Sync stats must update correctly on the admin dashboard.

---

## 4. Performance Latency Baselines

Target response limits in production environments:
- **API Router overhead**: < `10ms` (middleware execution).
- **Dijkstra Navigation path calculation**: < `15ms`.
- **Hybrid RAG vector lookup (Stage 1)**: < `80ms`.
- **Cross-Encoder Re-ranking (Stage 2)**: < `180ms` (pre-loaded model).
- **Gemini response generation stream**: < `250ms` (time-to-first-token).
- **Concurrent Context Gathering pipeline**: < `250ms` (concurrency execution).
