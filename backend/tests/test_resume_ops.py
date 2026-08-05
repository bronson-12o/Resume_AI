"""Tests for resume operations (update, regenerate, download, history)."""
import pytest
from unittest.mock import patch


def _create_resume(client, user_id, saved_job_id=None):
    """Helper: generate a resume and return its ID."""
    with patch("backend.routers.resume.parse_job_description") as mock_parse, \
         patch("backend.routers.resume.generate_tailored_resume") as mock_gen, \
         patch("backend.routers.resume.calculate_match_score") as mock_score, \
         patch("backend.routers.resume.get_skill_recommendations") as mock_recs:

        mock_parse.return_value = {
            "job_title": "Developer",
            "company_name": "Acme",
            "required_skills": ["Python"],
            "preferred_skills": [],
            "ats_keywords": ["python"],
        }
        mock_gen.return_value = {
            "professional_summary": "Test summary",
            "work_experience": [{"title": "Dev", "company": "Co", "dates": "2020-2023", "bullets": ["Built APIs"]}],
            "education": [{"degree": "BS CS", "institution": "MIT", "graduation_date": "2020"}],
            "skills": {"Programming": ["Python", "JavaScript"]},
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

        # The job description must be at least 50 chars due to validation
        jd = "Looking for a Python developer with experience in building REST APIs and web applications at our company"
        payload = {
            "user_id": user_id,
            "job_description": jd,
        }
        if saved_job_id is not None:
            payload["saved_job_id"] = saved_job_id
        response = client.post("/api/resume/generate", json=payload)
        assert response.status_code == 200
        return response.json()["resume_id"]


def test_update_resume(client, sample_user_with_profile):
    resume_id = _create_resume(client, sample_user_with_profile["id"])

    response = client.put(f"/api/resume/{resume_id}", json={
        "generated_resume_content": {
            "professional_summary": "Updated summary",
            "work_experience": [],
            "education": [],
            "skills": {},
            "projects": [],
            "certifications": [],
        }
    })
    assert response.status_code == 200
    assert response.json()["resume_content"]["professional_summary"] == "Updated summary"
    assert "html_preview" in response.json()


@patch("backend.routers.resume.regenerate_section")
def test_regenerate_section(mock_regen, client, sample_user_with_profile):
    resume_id = _create_resume(client, sample_user_with_profile["id"])

    mock_regen.return_value = {"professional_summary": "Brand new AI-generated summary"}

    response = client.post(f"/api/resume/{resume_id}/regenerate-section", json={
        "section_name": "professional_summary",
    })
    assert response.status_code == 200
    data = response.json()
    assert data["regenerated_section"] == "professional_summary"
    assert data["resume_content"]["professional_summary"] == "Brand new AI-generated summary"


def test_get_resume(client, sample_user_with_profile):
    resume_id = _create_resume(client, sample_user_with_profile["id"])

    response = client.get(f"/api/resume/{resume_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == resume_id
    assert "html_preview" in data
    assert "resume_content" in data
    assert data["job_description_text"].startswith("Looking for a Python developer")
    assert data["match_score"]["overall_score"] == 75
    assert data["match_score"]["breakdown"]["hard_skills"]["matched"] == ["Python"]


def test_download_resume(client, sample_user_with_profile):
    resume_id = _create_resume(client, sample_user_with_profile["id"])

    response = client.get(f"/api/resume/{resume_id}/download")
    assert response.status_code == 200
    assert "application/vnd" in response.headers["content-type"]


def test_download_resume_with_template(client, sample_user_with_profile):
    resume_id = _create_resume(client, sample_user_with_profile["id"])

    for template in ["ats_classic", "modern", "compact"]:
        response = client.get(f"/api/resume/{resume_id}/download?template={template}")
        assert response.status_code == 200, f"Template {template} failed"


def test_resume_history(client, sample_user_with_profile):
    user_id = sample_user_with_profile["id"]
    _create_resume(client, user_id)
    _create_resume(client, user_id)

    response = client.get(f"/api/resume/history/{user_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert len(data["items"]) == 2


def test_resume_is_preserved_when_linked_job_is_deleted(client, sample_user_with_profile):
    user_id = sample_user_with_profile["id"]
    job = client.post("/api/tracker", json={
        "user_id": user_id,
        "job_title": "Developer",
    }).json()
    resume_id = _create_resume(client, user_id, saved_job_id=job["id"])

    delete_response = client.delete(f"/api/tracker/{job['id']}")
    resume_response = client.get(f"/api/resume/{resume_id}")

    assert delete_response.status_code == 200
    assert resume_response.status_code == 200
