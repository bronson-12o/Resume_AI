# ResumeAI

ResumeAI is a local-first job-search workspace that turns one complete, truthful career profile into job-specific resumes and cover letters. It also explains profile-to-role fit and keeps applications organized in a lightweight tracker.

The product is designed for an individual job seeker. It is not a hosted multi-user service: there is currently no authentication or account isolation, so do not expose it directly to the public internet.

## What it does

- Maintains a master profile with experience, education, skills, projects, and certifications.
- Imports text-based PDF and DOCX resumes into a review step before saving.
- Parses job descriptions and provides match scores. These features have deterministic fallbacks when no AI key is configured.
- Generates editable, job-specific resumes from saved experience without authorizing fabricated qualifications.
- Preserves detailed score breakdowns with each resume and exports ATS-oriented DOCX files in three templates.
- Generates and exports editable cover letters.
- Tracks saved, applied, interviewing, offered, and rejected jobs.
- Supports responsive light and dark interfaces.

## Product workflow

1. Create a profile manually or review an imported resume.
2. Paste a complete job description.
3. Review the parsed requirements and match score.
4. Optionally save the role to the tracker.
5. Generate, edit, preview, and export a tailored resume.
6. Create a cover letter and update the application status.

Job parsing and match scoring fall back to deterministic local logic when the selected AI provider is unavailable. Resume generation, section regeneration, resume import parsing, sector suggestions, and cover-letter generation require the selected provider key.

## Architecture

| Layer | Technology | Responsibility |
| --- | --- | --- |
| Web client | React 18, Vite 8, Tailwind CSS | Profile, tailoring, editing, scoring, export, and tracking workflows |
| API | Python 3.12, FastAPI, Pydantic | HTTP contracts, validation, security headers, and orchestration |
| Persistence | SQLAlchemy, SQLite | Local profiles, generated materials, and tracked jobs |
| AI boundary | OpenAI or Anthropic | Provider-backed parsing and generation behind one service interface |
| Documents | python-docx, PyPDF2 | DOCX export and text extraction |
| Runtime | Nginx, Docker Compose | Same-origin web/API deployment and persistent database volume |

The browser calls `/api` by default. In development, Vite proxies that path to FastAPI. In Docker, Nginx serves the client and proxies it to the backend container.

## Repository layout

```text
backend/
  database/       SQLAlchemy models, connection, and additive SQLite migrations
  routers/        Profile, job, scoring, resume, cover-letter, and tracker APIs
  services/       AI boundary, parsers, scoring, recommendations, and document builders
  tests/          API and service regression tests
frontend/
  public/         Static application assets
  src/api/        Browser API client
  src/components/ Shared interface components
  src/pages/      Route-level workflows
  src/router.jsx  Small client-only history router
.github/workflows/ci.yml
docker-compose.yml
```

## Local development

### Prerequisites

- Python 3.10 or newer; Python 3.12 matches the container and CI runtime.
- Node.js 20.19 or newer.
- An OpenAI or Anthropic key for provider-backed generation.

### Backend

From the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r backend/requirements.txt
cp backend/.env.example backend/.env
python -m uvicorn backend.main:app --reload --port 8000
```

The API is available at `http://localhost:8000`; interactive documentation is at `http://localhost:8000/docs`.

### Frontend

In another terminal:

```bash
npm --prefix frontend ci
cp frontend/.env.example frontend/.env
npm --prefix frontend run dev
```

Open `http://localhost:5173`.

### Optional sample profile

With the backend environment active:

```bash
python -m backend.database.seed
```

The seed uses fictional local data and does not contact an AI provider.

## Environment variables

Backend variables are documented in `backend/.env.example`.

| Variable | Default | Purpose |
| --- | --- | --- |
| `AI_PROVIDER` | `openai` | `openai` or `anthropic` |
| `OPENAI_API_KEY` | empty | Required when the OpenAI provider performs generation |
| `OPENAI_MODEL` | `gpt-4o-mini` | OpenAI model identifier |
| `ANTHROPIC_API_KEY` | empty | Required when the Anthropic provider performs generation |
| `ANTHROPIC_MODEL` | `claude-sonnet-4-20250514` | Anthropic model identifier |
| `DATABASE_URL` | `sqlite:///./resume_ai.db` | SQLAlchemy connection string |
| `FRONTEND_URL` | `http://localhost:5173` | Allowed browser origin |
| `ENVIRONMENT` | `development` | Enables production-only transport headers when set to `production` |

The frontend accepts `VITE_API_BASE_URL`. Keep `/api` for the normal same-origin setup; use a full backend URL ending in `/api` only for a deliberate split deployment.

Never commit `.env` files, provider keys, databases, uploaded resumes, or generated application materials.

## Validation

Run the same core checks used by CI:

```bash
source .venv/bin/activate
python -m compileall -q backend
python -m pytest backend/tests -q
npm --prefix frontend run check
npm --prefix frontend audit --audit-level=high
docker compose config --quiet
```

`npm run check` runs ESLint, Vitest, and the production Vite build.

## Docker Compose

```bash
# Optional: export the key for the selected provider.
export OPENAI_API_KEY="..."
docker compose up --build
```

Open `http://localhost`. The SQLite database is stored in the named `db-data` volume at `/app/data/resume_ai.db`, so container recreation does not discard the workspace. The frontend waits for the backend health check before starting.

To stop the services without deleting data:

```bash
docker compose down
```

Do not add `--volumes` unless you intentionally want to delete the local ResumeAI database.

## API surfaces

| Area | Representative endpoints |
| --- | --- |
| Health | `GET /api/health` |
| Profile | `POST /api/profile`, `GET /api/profile/{id}` |
| Import | `POST /api/profile/import`, `POST /api/profile/{id}/import/confirm` |
| Job analysis | `POST /api/jobs/parse`, `POST /api/scoring/quick` |
| Resumes | `POST /api/resume/generate`, `GET/PUT /api/resume/{id}`, `GET /api/resume/{id}/download` |
| Cover letters | `POST /api/cover-letter/generate`, `GET/PUT /api/cover-letter/{id}` |
| Tracker | `POST /api/tracker`, `GET /api/tracker/{user_id}`, `PUT/DELETE /api/tracker/{job_id}` |

See `/docs` for request and response schemas.

## Privacy and security model

- Profiles, job descriptions, generated materials, and tracking notes are sensitive personal data stored in SQLite.
- Uploaded PDF/DOCX bytes are processed in memory and are not retained as source files. Confirmed structured profile data is persisted.
- When an AI provider is configured, relevant profile and job-description text is sent to that provider for the requested analysis or generation. Provider retention and training policies are outside this repository.
- Upload type, signature, and size are validated; API inputs have bounded lengths and enumerated states.
- The API and Nginx add baseline browser security headers. The production container persists its database outside the image.
- Resource IDs are not authorization boundaries. Authentication must be added before any shared or public deployment.

## Known limitations

- One installation assumes one trusted user and selects the first saved profile in the client.
- There is no authentication, authorization, password reset, or encrypted-at-rest storage.
- Scanned/image-only PDFs require OCR before import.
- AI availability, latency, cost, and output quality depend on the configured provider.
- SQLite migrations are intentionally small and additive; a production-scale service needs a versioned migration tool and a managed database.
- Generated resumes and cover letters remain user-reviewable drafts. The user is responsible for checking accuracy before applying.

## Recommended next work

1. Add authentication and server-side ownership enforcement before shared deployment.
2. Add browser-level end-to-end coverage for import, tailoring, editing, export, and tracker transitions.
3. Add versioned database migrations and encrypted backups.
4. Add OCR as an explicit, privacy-reviewed import option.
