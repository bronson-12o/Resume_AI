"""FastAPI application entry point for ResumeAI."""
import logging
import os
import time
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

load_dotenv()

from backend.database.database import init_db
from backend.routers import profile, jobs, scoring, resume, recommendations, jobs_tracker, cover_letter


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting ResumeAI API v2.1.0")
    init_db()
    yield
    logger.info("Shutting down ResumeAI API")


limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="ResumeAI",
    description="AI-powered resume tailoring tool that optimizes resumes for specific job postings",
    version="2.1.0",
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
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = time.time() - start
    logger.info(f"{request.method} {request.url.path} -> {response.status_code} ({duration:.3f}s)")
    return response


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
        "version": "2.1.0",
    }


@app.get("/")
def root():
    return {
        "message": "Welcome to ResumeAI API",
        "docs": "/docs",
        "health": "/api/health",
    }
