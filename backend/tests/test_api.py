"""API tests for ResumeAI backend."""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from backend.main import app


client = TestClient(app)


# --- Health Check ---

def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "ResumeAI"


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "ResumeAI" in response.json()["message"]


# --- Profile CRUD ---

def test_create_profile():
    response = client.post("/api/profile", json={
        "name": "Test User",
        "email": "test@example.com",
        "phone": "555-1234",
        "location": "New York, NY",
        "professional_summary": "A test user profile",
    })
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test User"
    assert data["email"] == "test@example.com"
    assert "id" in data


def test_create_duplicate_email():
    client.post("/api/profile", json={
        "name": "User A",
        "email": "duplicate@example.com",
    })
    response = client.post("/api/profile", json={
        "name": "User B",
        "email": "duplicate@example.com",
    })
    assert response.status_code == 400


def test_get_profile():
    create = client.post("/api/profile", json={
        "name": "Full Profile User",
        "email": "full@example.com",
    })
    user_id = create.json()["id"]

    response = client.get(f"/api/profile/{user_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["user"]["name"] == "Full Profile User"
    assert "experiences" in data
    assert "skills" in data


def test_get_nonexistent_profile():
    response = client.get("/api/profile/99999")
    assert response.status_code == 404


def test_update_profile():
    create = client.post("/api/profile", json={
        "name": "Old Name",
        "email": "update@example.com",
    })
    user_id = create.json()["id"]

    response = client.put(f"/api/profile/{user_id}", json={
        "name": "New Name",
    })
    assert response.status_code == 200
    assert response.json()["name"] == "New Name"


def test_list_profiles():
    client.post("/api/profile", json={"name": "User 1", "email": "u1@example.com"})
    client.post("/api/profile", json={"name": "User 2", "email": "u2@example.com"})

    response = client.get("/api/profile")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 2
    assert len(data["items"]) >= 2


def test_delete_profile():
    create = client.post("/api/profile", json={
        "name": "Delete Me",
        "email": "delete@example.com",
    })
    user_id = create.json()["id"]

    response = client.delete(f"/api/profile/{user_id}")
    assert response.status_code == 200

    get_response = client.get(f"/api/profile/{user_id}")
    assert get_response.status_code == 404


# --- Work Experience ---

def test_add_experience():
    create = client.post("/api/profile", json={
        "name": "Exp User",
        "email": "exp@example.com",
    })
    user_id = create.json()["id"]

    response = client.post(f"/api/profile/{user_id}/experience", json={
        "job_title": "Software Engineer",
        "company_name": "TechCo",
        "start_date": "2022-01",
        "bullet_points": ["Built APIs", "Led team"],
        "skills_used": ["Python", "FastAPI"],
    })
    assert response.status_code == 200
    assert response.json()["job_title"] == "Software Engineer"


def test_delete_experience():
    create = client.post("/api/profile", json={
        "name": "Exp Del User",
        "email": "expdel@example.com",
    })
    user_id = create.json()["id"]

    exp = client.post(f"/api/profile/{user_id}/experience", json={
        "job_title": "Dev",
        "company_name": "Co",
        "start_date": "2020-01",
    })
    exp_id = exp.json()["id"]

    response = client.delete(f"/api/profile/{user_id}/experience/{exp_id}")
    assert response.status_code == 200


# --- Skills ---

def test_add_skill():
    create = client.post("/api/profile", json={
        "name": "Skill User",
        "email": "skill@example.com",
    })
    user_id = create.json()["id"]

    response = client.post(f"/api/profile/{user_id}/skills", json={
        "skill_name": "Python",
        "category": "programming",
        "proficiency_level": "advanced",
    })
    assert response.status_code == 200
    assert response.json()["skill_name"] == "Python"


# --- Education ---

def test_add_education():
    create = client.post("/api/profile", json={
        "name": "Edu User",
        "email": "edu@example.com",
    })
    user_id = create.json()["id"]

    response = client.post(f"/api/profile/{user_id}/education", json={
        "degree": "B.S. Computer Science",
        "institution": "MIT",
        "graduation_date": "2020-05",
    })
    assert response.status_code == 200
    assert response.json()["degree"] == "B.S. Computer Science"


# --- Projects ---

def test_add_project():
    create = client.post("/api/profile", json={
        "name": "Proj User",
        "email": "proj@example.com",
    })
    user_id = create.json()["id"]

    response = client.post(f"/api/profile/{user_id}/projects", json={
        "project_name": "MyApp",
        "description": "A cool app",
        "technologies_used": ["React", "Node.js"],
    })
    assert response.status_code == 200
    assert response.json()["project_name"] == "MyApp"


# --- Certifications ---

def test_add_certification():
    create = client.post("/api/profile", json={
        "name": "Cert User",
        "email": "cert@example.com",
    })
    user_id = create.json()["id"]

    response = client.post(f"/api/profile/{user_id}/certifications", json={
        "cert_name": "AWS Solutions Architect",
        "issuing_org": "Amazon",
        "date_obtained": "2023-01",
    })
    assert response.status_code == 200
    assert response.json()["cert_name"] == "AWS Solutions Architect"


# --- Job Parsing (with mock) ---

@patch("backend.routers.jobs.parse_job_description")
def test_parse_job(mock_parse):
    mock_parse.return_value = {
        "job_title": "Software Engineer",
        "company_name": "Google",
        "required_skills": ["Python", "Go"],
        "preferred_skills": ["Kubernetes"],
        "years_experience": "3+ years",
        "education_requirements": "BS in CS",
        "key_responsibilities": ["Build systems"],
        "ats_keywords": ["distributed", "scalable"],
        "seniority_level": "mid",
    }

    response = client.post("/api/jobs/parse", json={
        "job_description": "We're looking for a Software Engineer at Google...",
    })
    assert response.status_code == 200
    data = response.json()
    assert data["job_title"] == "Software Engineer"
    assert "Python" in data["required_skills"]


# --- Scoring (with mock) ---

@patch("backend.routers.scoring.calculate_match_score")
def test_score_match(mock_score):
    mock_score.return_value = {
        "overall_score": 72,
        "breakdown": {
            "hard_skills": {"score": 80, "matched": ["Python"], "missing": ["Go"]},
        },
        "verdict": "Strong match",
    }

    create = client.post("/api/profile", json={
        "name": "Score User",
        "email": "score@example.com",
    })
    user_id = create.json()["id"]

    response = client.post("/api/scoring/match", json={
        "user_id": user_id,
        "parsed_job": {
            "required_skills": ["Python", "Go"],
            "preferred_skills": [],
            "ats_keywords": [],
        },
    })
    assert response.status_code == 200
    assert response.json()["overall_score"] == 72


# --- Resume Generation (with mock) ---

@patch("backend.routers.resume.generate_tailored_resume")
@patch("backend.routers.resume.parse_job_description")
@patch("backend.routers.resume.calculate_match_score")
@patch("backend.routers.resume.get_skill_recommendations")
def test_generate_resume(mock_recs, mock_score, mock_parse, mock_gen):
    mock_parse.return_value = {
        "job_title": "Developer",
        "company_name": "Acme",
        "required_skills": ["Python"],
        "preferred_skills": [],
        "ats_keywords": ["python"],
    }
    mock_gen.return_value = {
        "professional_summary": "Test summary",
        "work_experience": [],
        "education": [],
        "skills": {},
        "projects": [],
        "certifications": [],
    }
    mock_score.return_value = {
        "overall_score": 75,
        "breakdown": {"hard_skills": {"matched": ["Python"], "missing": []}},
        "verdict": "Good match",
    }
    mock_recs.return_value = {
        "skill_recommendations": [],
        "keyword_suggestions": [],
        "general_advice": "Looks good",
    }

    create = client.post("/api/profile", json={
        "name": "Resume User",
        "email": "resume@example.com",
    })
    user_id = create.json()["id"]

    response = client.post("/api/resume/generate", json={
        "user_id": user_id,
        "job_description": "Looking for a Python developer with experience in building REST APIs and web applications at our company",
    })
    assert response.status_code == 200
    data = response.json()
    assert "resume_id" in data
    assert "html_preview" in data
    assert data["resume_content"]["professional_summary"] == "Test summary"
