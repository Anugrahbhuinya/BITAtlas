# Troubleshooting & Operational Recovery Guide

This document describes solutions for database connection timeouts, API startup conflicts, Gemini authentication errors, website sync crawler issues, and vector index recovery.

---

## 1. Database Connection Failures

### 1.1 MongoDB Timeout Issues
- **Symptoms**: Logs show `ServerSelectionTimeoutError` or chat history loading hangs.
- **Resolution**:
  1. Verify the MongoDB daemon is active on the host machine:
     ```bash
     docker ps | grep mongo
     # Or for local service:
     systemctl status mongod
     ```
  2. Confirm the `MONGODB_URI` string matches the correct host name and credentials.
  3. Verify port access permissions: MongoDB must be reachable on port `27017`.

### 1.2 ChromaDB Database Lock Errors
- **Symptoms**: Server logs show database read/write locks or index files write access errors.
- **Resolution**:
  1. ChromaDB runs as a persistent file client. Ensure only a single FastAPI backend instance is running and has write access to the directory defined in `CHROMA_DB_PATH`.
  2. If a database lock persists, stop the container, verify no stray python processes are running, and restart the backend.

---

## 2. API Startup & Port Conflicts

- **Symptoms**: Backend terminates immediately on start with port binding errors.
- **Resolution**:
  - The backend includes a port conflict utility checker. By default, the API binds to port `8001` and checks if port `5180` (or the configured `PORT`) is occupied.
  - Find and terminate any processes occupying port `8001`:
    ```powershell
    # On Windows:
    Get-NetTCPConnection -LocalPort 8001 | Select-Object -ExpandProperty OwningProcess | ForEach-Object { Stop-Process -Id $_ -Force }
    ```
    ```bash
    # On Linux:
    fuser -k 8001/tcp
    ```

---

## 3. Google Gemini API Failures

- **Symptoms**: Chat requests fail with `401 Unauthorized` or `403 Forbidden` API status codes.
- **Resolution**:
  1. Confirm your `GEMINI_API_KEY` is loaded correctly into the environment.
  2. Verify your API key has not expired and has sufficient quota.
  3. Validate model naming configurations. Ensure the `GEMINI_MODEL` environment variable matches `gemini-2.5-flash`.

---

## 4. Crawl Sync Scheduler Failures

- **Symptoms**: Crawl log history records show sync status "Failed" with traceback details.
- **Resolution**:
  1. Verify outbound internet access on the backend container.
  2. Check target website structures. If website formats change, BeautifulSoup selectors might fail. Use the admin workspace details screen to trigger manual check runs and review the crawl log reports.
  3. Check `robots.txt` compliance settings if the scraper is configured to restrict crawls based on robots policies.
