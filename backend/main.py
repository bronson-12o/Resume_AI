"""FastAPI application entry point for ResumeAI."""
import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

load_dotenv()

from backend.database.database import init_db
from backend.routers import profile, jobs, scoring, resume, recommendations, jobs_tracker, cover_letter


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="ResumeAI",
    description="AI-powered resume tailoring tool that optimizes resumes for specific job postings",
    version="2.0.0",
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS configuration
frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontend_url, "http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(profile.router)
app.include_router(jobs.router)
app.include_router(scoring.router)
app.include_router(resume.router)
app.include_router(recommendations.router)
app.include_router(jobs_tracker.router)
app.include_router(cover_letter.router)


@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "service": "ResumeAI",
        "version": "1.0.0",
    }


@app.get("/")
def root():
    return {
        "message": "Welcome to ResumeAI API",
        "docs": "/docs",
        "health": "/api/health",
    }
