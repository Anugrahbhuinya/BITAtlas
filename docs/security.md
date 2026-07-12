# Enterprise Security Documentation

This document describes the security policies, protections, rate limiting rules, input validations, and threat mitigation models deployed in the **BIT Mesra AI Operating System** under **Phase 12 Hardening**.

---

## 1. Authentication Hardening
The application enforces JWT (JSON Web Token) authentication on all administrative and private student endpoints.
- **Access Token Integrity**: Access tokens are digitally signed using `HMAC-SHA256` using a cryptographically random secret key (`JWT_SECRET`) loaded from environment variables.
- **Expired Token Rejection**: Tokens are verified against active expiration timestamps (`ACCESS_TOKEN_EXPIRE_MINUTES`). Expired tokens are rejected with a standard `401 Unauthorized` status.
- **Invalid Signatures & Malformed Claims**: Any JWT token with a modified payload or incorrect signature is immediately intercepted and rejected at the route level.
- **Protected Routes**:
  - Protected student endpoints (e.g. `/api/student/profile`) require a valid bearer JWT with role `student`.
  - Protected administrative endpoints (e.g. `/api/admin/dashboard`) require a valid bearer JWT with role `admin`.

---

## 2. Authorization (Role-Based Access Control)
The application validates that authenticated users have the correct authorization scopes.
- **Role Scoping**: Users are assigned roles (e.g. `student`, `admin`) encoded in their JWT payload claim boundaries.
- **Admin Isolation**: Admin routes explicitly verify that the token owner holds admin permissions using FastAPI dependencies:
  ```python
  async def get_current_admin(current_user: str = Depends(get_current_user)) -> str:
      # Verifies role and grants permissions
  ```
- **Diagnostics and Settings Protection**: All internal system statuses, website logs, PDF management, and database statistics routes are locked behind admin authorization.

---

## 3. Input Validation & Request Constraints
Every API endpoint utilizes strongly typed Pydantic models for request body deserialization.
- **Malformed Payloads**: Any request containing invalid JSON structure or data types is immediately rejected with a `400 Bad Request` before invoking application logic.
- **Missing Required Fields**: The application catches `RequestValidationError` and returns a clean error mapping listing the missing fields, preventing raw python stack traces from leaking.
- **Oversized Payloads**: Standard REST endpoints are protected against excessive resource consumption using size checks on request bodies.

---

## 4. AI Security & Guardrails
The system protects LLM generation pipelines against manipulation and attacks:
- **Prompt Injection Filter**: User inputs are sanitized to strip system-override phrases (e.g. *"Ignore previous instructions..."*).
- **Jailbreak Blocks**: Input strings are assessed against pre-defined adversarial patterns and system keywords.
- **Smart Context Engine Budgeting**: Prevents large inputs from bloating the token counts. A strict budget of 3,500 tokens is enforced via the `TokenBudgetManager`.
- **RAG Context Sanitization**: Retrieved content is sanitized before prompt composition to ensure malicious documents cannot trick the LLM.

---

## 5. Standardized API Hardening
All exceptions are mapped to clean JSON response formats at the middleware level:
- **No Stack Traces**: Production modes disable internal tracebacks in error responses. 
- **Standardized Response Formats**: 
  - **401 Unauthorized**: Correctly formatted WWW-Authenticate headers.
  - **429 Too Many Requests**: Returned when rate limits are exceeded.
  - **500 Internal Server Error**: A generic user-friendly message is shown while the error is recorded securely in structured logs.

---

## 6. Rate Limiting
Configurable rate limit boundaries are applied to expensive endpoints:
- **Chat Endpoint (`/chat`)**: Standard rate is 20 requests per 60-second window.
- **Admin Authentication (`/api/admin/login`)**: Limit is 10 login attempts per 60-second window.
- **File Uploads (`/api/admin/documents/upload`)**: Rate-limited to avoid denial-of-service vector.
