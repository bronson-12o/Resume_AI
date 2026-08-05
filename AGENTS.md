# ResumeAI Agent Guide

## Product

ResumeAI is a local-first job-search workspace. It stores a truthful master career profile, compares that profile with job descriptions, generates editable resumes and cover letters, and tracks applications. Do not add experience, claims, or qualifications that the user did not provide.

## Structure

- `backend/main.py`: FastAPI entry point and middleware.
- `backend/routers/`: HTTP contracts for profiles, parsing, scoring, resumes, cover letters, recommendations, and tracking.
- `backend/services/`: deterministic and provider-backed product logic.
- `backend/database/`: SQLAlchemy models, connection setup, and lightweight migrations.
- `backend/tests/`: API and service behavior tests.
- `frontend/src/pages/`: route-level React experiences.
- `frontend/src/components/`: shared interface components.
- `frontend/src/api/client.js`: browser API client.
- `docker-compose.yml`: local production-style deployment.

## Setup and development

Use Python 3.10+ and Node.js 18+.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r backend/requirements.txt
npm --prefix frontend install
cp backend/.env.example backend/.env
uvicorn backend.main:app --reload --port 8000
npm --prefix frontend run dev
```

An AI provider key is optional for deterministic features and tests. Provider-backed generation requires the corresponding key.

## Validation

Run the commands represented by the repository's package scripts and documentation. At minimum:

```bash
python -m pytest backend/tests -q
python -m compileall -q backend
npm --prefix frontend run build
```

When lint or test scripts are present in `frontend/package.json`, run them as well. Validate Docker configuration when Docker is available.

## Architecture and security constraints

- Preserve the provider-neutral AI service boundary.
- Keep deterministic parsing and scoring usable without external credentials.
- Treat uploaded resumes and career details as sensitive personal data. Never log document contents, API keys, or full profile payloads.
- Validate uploaded file type and size, job-description length, enumerated statuses, URLs, and user-owned resource relationships.
- Do not silently fabricate AI output or present fallback content as provider-generated.
- Preserve SQLite compatibility unless a documented migration strategy accompanies a database change.
- Avoid destructive migrations and never commit `.env`, database, generated resume, or personal profile files.

## Definition of done

A change is done when its primary workflow works, relevant backend tests and frontend quality gates pass, the production build succeeds, responsive and keyboard behavior are checked for UI changes, errors are understandable, and documentation matches reality. Update `.agent/EXEC_PLAN.md` and `PRODUCTIZATION_STATUS.md` after meaningful milestones.

