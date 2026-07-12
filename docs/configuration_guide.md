# Configuration & Environment Setup Guide

This document describes the configuration profiles, feature flags, and environment configurations utilized by the **BIT Mesra AI Operating System**.

---

## 1. Centralized Settings Management
All configuration values are centralized under [settings.py](file:///c:/Users/ASUS/bit-mesra-ai-agent/backend/app/security/config/settings.py). 

Rather than scattering constants throughout the application code, modules import from this centralized configuration file.

---

## 2. Configuration Profiles (APP_ENV)
The application dynamically selects one of three configuration profiles at startup depending on the `APP_ENV` environment variable:

* **development**: Debug mode enabled. Security headers disabled for local client integrations. Configured to use the local development database (`bit_mesra_db`).
* **testing**: Configured to run tests in isolation. Utilizes an isolated database (`bit_mesra_test_db`). Rate limits are automatically bypassed (set to a very high threshold) to prevent test runner blocks.
* **production**: Strict production hardening. Debug mode is fully disabled (preventing stack trace leakage). Standard OWASP security headers are enforced.

---

## 3. Configurable Environment Variables
The following parameters can be customized in the `backend/.env` file:

### Core Server Settings
* `APP_ENV`: Deployment mode (`development`, `testing`, `production`). Default: `development`.
* `DEBUG`: Boolean flag (`True` / `False`).
* `ALLOWED_HOSTS`: Comma-separated list of allowed host headers. Default: `*`.
* `CORS_ORIGINS`: Comma-separated list of allowed origins. Default: `*`.

### Database Settings
* `MONGO_URI`: The connection string for the MongoDB instance.
* `MONGO_DB`: Name of the MongoDB database.

### Gemini LLM Settings
* `GEMINI_API_KEY`: API access key for Google Gemini.
* `GEMINI_MODEL`: The LLM version utilized (e.g. `gemini-3.5-flash`).
* `GEMINI_TIMEOUT`: Request timeout duration in seconds. Default: `10.0`.
* `GEMINI_MAX_RETRIES`: Number of retry attempts for failed requests. Default: `1`.
* `GEMINI_RETRY_DELAY`: Wait time in seconds between retries. Default: `1.0`.

### Reliability Settings
* `CIRCUIT_BREAKER_COOLDOWN`: Recovery duration in seconds for tripped circuit breakers. Default: `30.0`.
* `CACHE_TTL`: Time-to-Live in seconds for cached response payloads. Default: `300.0`.

### Rate Limiting Settings
* `RATE_LIMIT_CHAT_LIMIT`: Maximum number of requests allowed on the chat endpoint in the window. Default: `20`.
* `RATE_LIMIT_CHAT_WINDOW`: Duration of the rate limit window in seconds. Default: `60`.
* `RATE_LIMIT_ADMIN_LIMIT`: Maximum number of attempts allowed on admin endpoints. Default: `10`.
* `RATE_LIMIT_ADMIN_WINDOW`: Duration of the admin rate limit window in seconds. Default: `60`.

### Resource & Logging Limits
* `MAX_CONTENT_LENGTH`: Maximum allowable HTTP body payload size in bytes. Default: `5242880` (5MB).
* `MAX_PROMPT_SIZE`: Maximum character limit for assembled prompts. Default: `5000`.
* `LOG_LEVEL`: Severity level for logs (`DEBUG`, `INFO`, `WARNING`, `ERROR`). Default: `INFO`.
* `STRUCTURED_LOGGING`: Boolean flag to enable structured JSON logs. Default: `True`.
