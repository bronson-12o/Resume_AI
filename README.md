# ResumeAI

AI-powered resume tailoring tool that helps job seekers optimize their resumes for specific job postings. Built with a "master profile" approach — store everything you've done, then generate targeted, ATS-optimized resumes for each application without fabricating experience.

## Features

- **Master Profile** — Store all your experience, skills, projects, education, and certifications in one place
- **Job Description Parser** — Paste any JD and get structured extraction of requirements, skills, and ATS keywords
- **Match Scoring** — See exactly how well your profile matches a job (hard skills, experience, education, keywords)
- **AI Resume Generator** — Get a tailored, ATS-optimized resume using only your real experience
- **DOCX Export** — Download clean, ATS-friendly Word documents
- **Skill Gap Recommendations** — Actionable suggestions with curated learning resources
- **Sector Explorer** — Discover alternative job titles and industries where your skills transfer
- **Dark Mode** — Full dark mode support

## Tech Stack

| Layer | Technology | Why |
|-------|-----------|-----|
| Backend | Python + FastAPI | High performance async API framework |
| Frontend | React (Vite) + Tailwind CSS | Fast dev experience, clean utility-first styling |
| AI | OpenAI / Anthropic (swappable) | Provider-agnostic abstraction layer |
| Database | SQLite + SQLAlchemy | Zero-config, easy deployment |
| Resume Export | python-docx | ATS-friendly .docx generation |
| Deployment | Docker + docker-compose | Single-command deployment |

## Project Structure

```
resume-ai/
├── backend/
│   ├── main.py                  # FastAPI app entry point
│   ├── requirements.txt
│   ├── .env.example
│   ├── Dockerfile
│   ├── database/
│   │   ├── models.py            # SQLAlchemy models
│   │   ├── database.py          # DB connection and session
│   │   └── seed.py              # Sample data seeder
│   ├── routers/
│   │   ├── profile.py           # CRUD for master profile
│   │   ├── jobs.py              # Job description parsing
│   │   ├── resume.py            # Resume generation + download
│   │   ├── scoring.py           # Match scoring
│   │   └── recommendations.py   # Skill gaps + sector suggestions
│   ├── services/
│   │   ├── ai_service.py        # AI provider abstraction layer
│   │   ├── parser_service.py    # Job description NLP parsing
│   │   ├── scorer_service.py    # Match scoring logic
│   │   ├── resume_builder.py    # Resume assembly + DOCX/HTML
│   │   └── recommender.py       # Skill gap + sector logic
│   ├── utils/
│   │   ├── ats_keywords.py      # ATS keyword lists + resources
│   │   └── templates.py         # Resume templates + AI prompts
│   └── tests/
│       └── test_api.py          # API tests with mocks
├── frontend/
│   ├── src/
│   │   ├── App.jsx              # Root with routing + dark mode
│   │   ├── pages/
│   │   │   ├── Dashboard.jsx    # Overview + history
│   │   │   ├── Profile.jsx      # Master profile management
│   │   │   ├── Tailor.jsx       # Paste JD + generate resume
│   │   │   └── Results.jsx      # Score, preview, download
│   │   ├── components/
│   │   │   ├── ProfileForm.jsx  # Reusable form field
│   │   │   ├── SkillTag.jsx     # Removable skill chip
│   │   │   ├── ScoreGauge.jsx   # Circular score display
│   │   │   ├── ResumePreview.jsx # HTML resume preview
│   │   │   └── GapCard.jsx      # Skill gap recommendation card
│   │   └── api/
│   │       └── client.js        # API helper functions
│   ├── package.json
│   ├── vite.config.js
│   ├── Dockerfile
│   └── nginx.conf
├── docker-compose.yml
└── README.md
```

## Setup — Local Development

### Prerequisites

- Python 3.10+
- Node.js 18+
- An OpenAI or Anthropic API key

### Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your API key

# Run the server
cd ..
uvicorn backend.main:app --reload --port 8000

# (Optional) Seed sample data
python -m backend.database.seed
```

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start dev server (proxies API to localhost:8000)
npm run dev
```

Visit `http://localhost:5173` in your browser.

### Running Tests

```bash
# From project root
python -m pytest backend/tests/ -v
```

## Deployment

### Docker (Single Server)

```bash
# Set your API key
export OPENAI_API_KEY=sk-...

# Build and run
docker-compose up --build -d
```

The app will be available at `http://localhost` (port 80).

### Separate Deployment

**Backend** (Railway / Render / Fly.io):
- Deploy the `backend/` directory
- Set environment variables (API keys, DATABASE_URL)
- Start command: `uvicorn backend.main:app --host 0.0.0.0 --port 8000`

**Frontend** (Vercel / Netlify):
- Deploy the `frontend/` directory
- Build command: `npm run build`
- Output directory: `dist`
- Set API proxy to your backend URL

## API Documentation

Once the backend is running, visit `http://localhost:8000/docs` for the interactive Swagger UI.

### Key Endpoints

| Method | Endpoint | Description |
|--------|---------|-------------|
| GET | `/api/health` | Health check |
| POST | `/api/profile` | Create user profile |
| GET | `/api/profile/{id}` | Get full profile |
| POST | `/api/jobs/parse` | Parse job description |
| POST | `/api/scoring/match` | Calculate match score |
| POST | `/api/resume/generate` | Generate tailored resume |
| GET | `/api/resume/{id}/download` | Download .docx |
| POST | `/api/recommendations/skills` | Get skill gap recs |
| POST | `/api/recommendations/sectors` | Explore sectors |

## AI Provider Configuration

The AI service is provider-agnostic. Set `AI_PROVIDER` in your `.env`:

- `openai` (default) — Uses GPT-4o-mini
- `anthropic` — Uses Claude Sonnet

Switching providers is a one-variable change. The abstraction layer in `backend/services/ai_service.py` handles the rest.

## Environment Variables

```
OPENAI_API_KEY=sk-...          # Required if using OpenAI
ANTHROPIC_API_KEY=sk-ant-...   # Required if using Anthropic
DATABASE_URL=sqlite:///./resume_ai.db
FRONTEND_URL=http://localhost:5173
AI_PROVIDER=openai             # openai or anthropic
ENVIRONMENT=development
```

## Future Roadmap

- Cover letter generator using profile + JD
- LinkedIn profile optimizer
- Job tracking board (applications, statuses, follow-ups)
- Bulk tailoring (multiple JDs at once)
- Interview prep question generator
- Browser extension for auto-pulling JDs
- Multi-user authentication
