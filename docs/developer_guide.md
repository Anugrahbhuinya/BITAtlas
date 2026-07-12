# Developer & Code Quality Guide

This guide is for developers working on the **BIT Mesra AI Assistant** codebase. It defines setup steps, coding standards, directory conventions, and static analysis tools.

---

## 1. Local Development Setup

To initialize the development workspace locally:

### Backend Setup
1. Navigate to the `backend/` directory:
   ```bash
   cd backend
   ```
2. Create and activate a Python virtual environment:
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On Unix:
   source venv/bin/activate
   ```
3. Install standard requirements:
   ```bash
   pip install -r requirements.txt
   ```
4. Set up database configurations in `.env` based on `.env.example`.

### Frontend Setup
1. Navigate to the `frontend/` directory:
   ```bash
   cd frontend
   ```
2. Install npm packages:
   ```bash
   npm install
   ```

---

## 2. Coding Standards & Conventions

The codebase uses standard conventions for Python and React/TypeScript development:
- **Type Hints:** All new Python methods must declare argument and return type annotations.
- **Async Execution:** Asynchronous MongoDB Motor operations and RAG context fetches must use `async`/`await` paradigms to keep the gateway responsive.
- **Separation of Concerns:** Keep router controller functions lightweight. Place business logic inside dedicated classes under `backend/app/services/` and database interactions under repositories.

---

## 3. Static Analysis Checks

Before committing or pushing code, run static analysis tests to verify style adherence and type consistency:

### Running Static Checks
Run the static analysis orchestrator from the workspace root:
```bash
python tests/test_runner.py --static
```

This runs the following tools:
1. **Flake8:** Scans for syntax bugs and PEP 8 style issues.
2. **Pylint:** Flags complexity warnings and logical errors.
3. **Mypy:** Assesses type-safety parameters.
4. **Radon:** Calculates cyclomatic complexity to prevent overly complex methods.

Check the results and grading details inside `tests/reports/static_analysis_report.md`.

---

## 4. Hardening & Operational Readiness Policies

To maintain the production-ready state of the BIT Mesra AI OS:
- **No Hardcoded Secrets**: Always load secrets (database connections, JWT keys, Gemini credentials) using `settings` from `app.security.config.settings`.
- **Request ID Logging**: When initiating manual logs, include the current request ID from `state.request_id` to maintain trace correlation.
- **Pydantic Validation**: Ensure every new endpoint input strictly uses a Pydantic schema class.
- **Security-First Coding**: Never return raw exception strings or database query outlines in API JSON responses. Map all exceptions via `app.security.core.exceptions.handlers`.

