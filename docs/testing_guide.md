# Testing & Quality Assurance Guide

This document describes the testing architecture, test suites, and execution instructions for the **BIT Mesra AI Assistant** Quality Assurance (QA) Framework.

---

## 1. Testing Architecture Overview

The Phase 11 Enterprise QA Framework is structured to validate all layers of the BIT Mesra AI OS. The tests are located in the [tests/](file:///c:/Users/ASUS/bit-mesra-ai-agent/tests) directory:

```text
tests/
├── unit/             # Isolated testing of individual business services
├── integration/      # Validation of inter-service contracts
├── e2e/              # End-to-End student & admin workflow pipelines
├── security/         # JWT validations, traversal blocks, input sanitization
├── reports/          # Automatically generated markdown reports for all runs
├── mocks/            # Centralized database and vector store mocks
├── pytest.ini        # Pytest marker registration and configurations
├── coverage.ini      # Code coverage scoping directives
├── test_runner.py    # Universal test runner orchestrator
└── performance_runner.py # Concurrency load and latency benchmarking runner
```

---

## 2. Test Suites & Markers

The framework registers four distinct test categories in [pytest.ini](file:///c:/Users/ASUS/bit-mesra-ai-agent/tests/pytest.ini):

| Marker | Description | Key Modules Validated |
| :--- | :--- | :--- |
| `unit` | Isolated module validation | Intent Router, Prompt Builder, JWT Authentication, Website Content Normalizer |
| `integration` | Inter-service validation | Context Engine ↔ Prompt Builder, Navigation Resolver, RAG ↔ ChromaDB, Memory ↔ MongoDB |
| `e2e` | Request-response pipelines | Auth Registration/Login, Multi-turn conversations, Workspace dashboard profiles |
| `security` | Boundary validations | Route protection guards, Invalid signature rejections, Path traversal, Prompt injection block |

---

## 3. Running the Test Suites

All tests must be run using python in the workspace root directory. 

### A. Run all validation suites (Sequential Execution)
To run unit, integration, e2e, and security suites sequentially and generate markdown reports under `tests/reports/`:
```bash
python tests/test_runner.py --all
```

### B. Run a specific test suite
Use the specific marker flags to run individual suites:
- **Unit Tests:**
  ```bash
  python tests/test_runner.py --unit
  ```
- **Integration Tests:**
  ```bash
  python tests/test_runner.py --integration
  ```
- **E2e Tests:**
  ```bash
  python tests/test_runner.py --e2e
  ```
- **Security Tests:**
  ```bash
  python tests/test_runner.py --security
  ```

---

## 4. Code Coverage

Code coverage is automatically computed during the unit test execution using the configurations in `tests/coverage.ini`. The coverage report is outputted inside `tests/reports/unit_test_report.md`.

Target logic coverage is set at **90%+** for core backend packages (`backend/app/services/*`, `backend/app/routes/*`, etc.).

To manually run pytest with coverage flags:
```bash
pytest tests/ --cov=backend/app --cov-config=tests/coverage.ini --cov-report=term-missing
```

---

## 5. Performance Benchmarks & Load Testing

A dedicated performance and load benchmarking script is located at [tests/performance_runner.py](file:///c:/Users/ASUS/bit-mesra-ai-agent/tests/performance_runner.py). It tests pipeline component latencies and concurrency limits.

To execute the performance suite:
```bash
python tests/performance_runner.py
```
This generates a detailed benchmark breakdown at `tests/reports/performance_report.md`.

---

## 6. Unified Quality Dashboard

To compile all generated reports (static analysis, tests, performance, coverage) into a single executive dashboard:
```bash
python tests/quality_dashboard.py
```
This generates the dashboard at `tests/reports/quality_dashboard.md` with an overall health score out of 100.
