# Security Architecture & Best Practices

This document describes the security controls, validation middlewares, encryption frameworks, and prompt injection mitigation strategies implemented in the **BIT Mesra AI Workspace**.

---

## 1. Authentication & Session Security

- **JWT bearer validation**: Session verification relies on JSON Web Tokens (JWT). The backend signs JWT keys using `HS256` symmetric encryption keys and enforces a session timeout limit (`ACCESS_TOKEN_EXPIRE_MINUTES`).
- **Secure Password Storage**: Student passwords are hashed before database entry using **bcrypt** with a work factor of 12 rounds. Plaintext passwords are never logged or stored.
- **Refresh Token Rotation**: Standard rotating token checks verify refresh requests before issuing new short-lived access credentials.

---

## 2. API Middleware Pipelines (OWASP Hardening)

FastAPI endpoints are protected by non-blocking Starlette middlewares:
- **`SecurityHeadersMiddleware`**: Adds HTTP response headers to harden the application:
  - `X-Frame-Options: DENY` (intercepts clickjacking attempts)
  - `X-Content-Type-Options: nosniff` (mitigates MIME sniffing)
  - `Strict-Transport-Security` (enforces TLS/HTTPS usage)
- **CORS Configuration**: Restricts API calls to approved origins (`settings.CORS_ORIGINS`). Wildcard origins are disabled in production.

---

## 3. Data Sanitization & Input Filters

- **Pydantic Validation**: Strong-typed Pydantic model schemas intercept HTTP payloads at the routing tier, rejecting malformed JSON parameters immediately.
- **SQL / NoSQL Injection Prevention**: Database CRUD queries compile using async Motor parameters, preventing query string injections.
- **File Upload Verification**: 
  - Restricts uploads strictly to matching file formats (`.pdf` or `.png`/`.jpg`).
  - Limits file size properties to prevent denial-of-service (DoS) memory exhaustion.
  - Sanitizes target file names using `secure_filename` to prevent path traversal attempts.

---

## 4. Prompt Injection Mitigation

User inputs are evaluated by `validate_chat_query` in `ai_guard.py` before prompt assembly:
- **Block-list Regex**: Intercepts phrases containing instruction overrides (e.g., `ignore previous instructions`, `reveal system prompt`, `system developer guidelines`, `you are now acting as`).
- **Structured Prompts**: Enforces strict demarcation between system rules, context data, and user input variables, preventing user messages from leaking into system execution blocks.
- **Grounding Restraints**: Gemini instructions forbid the model from answering queries using facts not documented in the compiled context prompt.
