# Contributing to BITAtlas Workspace

We welcome contributions to the **BITAtlas Workspace**! Whether you are fixing bugs, improving the documentation, or adding new features, this guide will help you get started.

---

## Code of Conduct

Please help us maintain a friendly, welcoming, and professional community. Treat all contributors and users with respect.

---

## Coding Standards

### Python & FastAPI (Backend)
- **Formatting**: Adhere to PEP 8 standards. Use `black` or `yapf` for code formatting.
- **Type Hints**: All function signatures, routes, and services must include complete type annotations.
- **Linter**: Use `flake8` or `ruff` to identify style discrepancies before committing.
- **Middlewares**: Keep route middleware configurations non-blocking. Use async syntax where appropriate.
- **Exception Handling**: Use registered global handlers in `app/security/core/exceptions/handlers.py` to process validation or server errors cleanly.

### TypeScript & React (Frontend)
- **Framework**: Built with React 18, TypeScript, and TailwindCSS.
- **Linter & Compiler**: Code must compile cleanly under `npm run build` and pass ESLint audits via `npm run lint`.
- **Component Pattern**: Prefer Feature-Driven Development (FDD). Encapsulate component structures under `src/features/`.
- **Hooks**: Keep side effects isolated in custom hook files. Avoid synchronous setState calls inside effects.
- **Accessibility**: Support ARIA roles, labels, and full keyboard tab-indices on all interactive widgets.

---

## Git Workflow & Conventions

### Branch Naming Conventions
Follow semantic branch naming prefixes:
- `feature/amazing-feature` (for new features/enhancements)
- `bugfix/issue-description` (for bug fixes)
- `hotfix/quick-resolve` (for production release candidate hotfixes)
- `docs/update-guide` (for documentation updates)

### Commit Message Conventions
Use [Semantic Commits](https://www.conventionalcommits.org/):
- `feat: add AI assistant voice feedback`
- `fix: resolve duplicate message rendering on page refresh`
- `docs: update deployment environment parameters`
- `style: adjust chat window container max-width`
- `refactor: clean up unused imports in LoginPage`
- `test: add integration test suite for scheduler`

---

## Pull Request Process

1. **Fork the Repository**: Clone your fork locally and configure the upstream remote.
2. **Synchronize Branch**: Keep your branch up to date with the upstream `main` branch before making modifications.
3. **Local Tests & Linting**:
   - Run the backend test suite:
     ```bash
     cd backend
     python -m pytest
     ```
   - Run the frontend build and linter checks:
     ```bash
     cd frontend
     npm run lint
     npm run build
     ```
4. **Open a Pull Request**: Submit your pull request to the main repository.
5. **Review Cycle**: Address reviewer feedback promptly. Ensure all automated validation builds pass before merging.
