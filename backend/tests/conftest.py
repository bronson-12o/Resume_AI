"""Shared test fixtures for ResumeAI backend tests."""
import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.database.database import Base, engine


@pytest.fixture(autouse=True)
def setup_db():
    """Create tables before each test and drop after."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    """TestClient instance for making API requests."""
    return TestClient(app)


@pytest.fixture
def sample_user(client):
    """Create a sample user and return its data."""
    response = client.post("/api/profile", json={
        "name": "Test User",
        "email": "test@example.com",
        "phone": "555-1234",
        "location": "New York, NY",
        "professional_summary": "Experienced software engineer with 5 years of Python.",
    })
    return response.json()


@pytest.fixture
def sample_user_with_profile(client, sample_user):
    """Create a user with experience, skills, education, project, and cert."""
    user_id = sample_user["id"]

    client.post(f"/api/profile/{user_id}/experience", json={
        "job_title": "Software Engineer",
        "company_name": "TechCo",
        "start_date": "2020-01",
        "end_date": "2023-12",
        "bullet_points": ["Built REST APIs in Python", "Led team of 5 engineers"],
        "skills_used": ["Python", "FastAPI", "PostgreSQL"],
    })

    client.post(f"/api/profile/{user_id}/skills", json={
        "skill_name": "Python",
        "category": "programming",
        "proficiency_level": "advanced",
    })

    client.post(f"/api/profile/{user_id}/education", json={
        "degree": "B.S. Computer Science",
        "institution": "MIT",
        "graduation_date": "2020-05",
    })

    client.post(f"/api/profile/{user_id}/projects", json={
        "project_name": "ResumeAI",
        "description": "AI-powered resume builder",
        "technologies_used": ["Python", "React"],
    })

    client.post(f"/api/profile/{user_id}/certifications", json={
        "cert_name": "AWS Solutions Architect",
        "issuing_org": "Amazon",
        "date_obtained": "2023-01",
    })

    return sample_user
