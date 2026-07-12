# Operational, Logging & Monitoring Guide

This guide details the logging, monitoring, health checks, and operational resilience parameters designed for the **BIT Mesra AI Assistant** platform under **Phase 12 Hardening**.

---

## 1. Structured Logging
The application replaces standard print statements and raw text logs with structured JSON formatting optimized for log collectors (such as Elasticsearch, Logstash, Fluentd, or Datadog).

### Configured Attributes
Every API request writes a single log record capturing:
- `Request ID`: Unique correlation UUID injected via `RequestIDMiddleware` to trace execution steps.
- `Client IP`: Remote address of the caller.
- `Endpoint`: Requested path (e.g. `/chat`).
- `Execution Time`: Precise API duration in seconds measured by `RequestTimingMiddleware`.
- `Status Code`: Return HTTP status.
- `User ID`: Extracted student email/identifier if the request is authenticated.

### Security Sanitization
Under **no circumstances** does the logging utility log sensitive credentials. Filter rules prevent:
- Plaintext passwords (e.g., from login payloads)
- Session tokens / JWT Bearer keys
- Personal student identity data (PII)

---

## 2. Health Monitoring
Health indicators are exposed via the `/health` and `/ready` endpoints to assist orchestrators (such as Kubernetes or Docker Swarm) in evaluating container statuses.

### Endpoints
* **`/health`**: Determines if the FastAPI server is running.
  - **Response (200 OK)**: `{"status": "healthy", "timestamp": "..."}`
* **`/ready`**: Verifies connectivity to required upstream systems.
  - Checks if **MongoDB** is connected and responsive.
  - Checks if **ChromaDB** is loaded and queryable.
  - Validates **Gemini API** configuration state.
  - **Response (200 OK)**:
    ```json
    {
      "status": "ready",
      "services": {
        "mongodb": "healthy",
        "chromadb": "healthy",
        "gemini": "healthy"
      }
    }
    ```
    *(If any required service is down, a `503 Service Unavailable` is returned containing the failures breakdown).*

---

## 3. Middleware Architecture
Operations logging, correlation tracing, and security policies are processed using dedicated Starlette middlewares in `backend/app/main.py`:

1. **`RequestIDMiddleware`**: Generates or forwards a `X-Request-ID` header.
2. **`RequestTimingMiddleware`**: Measures backend execution latency.
3. **`SecurityHeadersMiddleware`**: Mounts OWASP headers (`X-Frame-Options`, `X-Content-Type-Options`, `Content-Security-Policy`, `Strict-Transport-Security`).
4. **`StructuredLoggingMiddleware`**: Combines correlation details, timing results, and status codes to emit a structured log record.

---

## 4. Error Recovery & Resilience
To prevent single-point failures from causing complete system crashes, the following circuit protections are integrated:

- **Subsystem Isolation**: A database error or scraping crawler failure runs in isolated event loop threads (`asyncio.to_thread`) without blocking main API router queues.
- **Circuit Breaker**: Detects repeated failures when connecting to third-party APIs (like Google Gemini). When the threshold is crossed, the circuit trips to `OPEN` and fast-fails requests using fallback strategies to save processing cycles.
- **Fast Fallback**: If the Gemini LLM is unreachable or rate-limited, the system falls back to direct RAG retrieval answers or displays a graceful message without crashing the user interface.
- **Retry Policy**: Upstream requests to Gemini utilize an exponential backoff retry configuration to handle temporary network fluctuations gracefully.
