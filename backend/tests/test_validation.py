"""Tests for input validation improvements."""
import pytest
from unittest.mock import patch


def test_empty_name_rejected(client):
    response = client.post("/api/profile", json={
        "name": "",
        "email": "test@example.com",
    })
    assert response.status_code == 422


def test_invalid_job_status_rejected(client, sample_user):
    create = client.post("/api/tracker", json={
        "user_id": sample_user["id"],
        "job_title": "Test",
    })
    job_id = create.json()["id"]

    response = client.put(f"/api/tracker/{job_id}", json={
        "status": "pending",  # Not a valid status
    })
    assert response.status_code == 422


def test_invalid_cover_letter_tone_rejected(client, sample_user):
    response = client.post("/api/cover-letter/generate", json={
        "user_id": sample_user["id"],
        "job_description": "Test JD",
        "tone": "aggressive",
    })
    assert response.status_code == 422


def test_short_job_description_rejected(client, sample_user):
    response = client.post("/api/resume/generate", json={
        "user_id": sample_user["id"],
        "job_description": "Too short",
    })
    assert response.status_code == 422


def test_empty_job_parse_rejected(client):
    response = client.post("/api/jobs/parse", json={
        "job_description": "",
    })
    assert response.status_code == 422


def test_blank_tracker_title_rejected(client, sample_user):
    response = client.post("/api/tracker", json={
        "user_id": sample_user["id"],
        "job_title": "   ",
    })
    assert response.status_code == 422


def test_invalid_skill_category_rejected(client, sample_user):
    response = client.post(f"/api/profile/{sample_user['id']}/skills", json={
        "skill_name": "Python",
        "category": "miscellaneous",
        "proficiency_level": "advanced",
    })
    assert response.status_code == 422


def test_profile_update_rejects_duplicate_email(client, sample_user):
    second = client.post("/api/profile", json={
        "name": "Second User",
        "email": "second@example.com",
    }).json()
    response = client.put(f"/api/profile/{second['id']}", json={
        "email": sample_user["email"],
    })
    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"


def test_security_headers_are_added(client):
    response = client.get("/api/health")
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["x-frame-options"] == "DENY"
    assert response.headers["referrer-policy"] == "strict-origin-when-cross-origin"


@patch("backend.routers.resume.generate_tailored_resume")
@patch("backend.routers.resume.calculate_match_score")
@patch("backend.routers.resume.get_skill_recommendations")
def test_resume_rejects_job_from_another_profile(
    mock_recommendations, mock_score, mock_generate, client, sample_user_with_profile
):
    second = client.post("/api/profile", json={
        "name": "Second User",
        "email": "second@example.com",
    }).json()
    foreign_job = client.post("/api/tracker", json={
        "user_id": second["id"],
        "job_title": "Foreign Job",
    }).json()

    response = client.post("/api/resume/generate", json={
        "user_id": sample_user_with_profile["id"],
        "job_description": "A detailed Python engineering job description with enough content for validation.",
        "parsed_job": {"required_skills": [], "preferred_skills": [], "ats_keywords": []},
        "saved_job_id": foreign_job["id"],
    })

    assert response.status_code == 400
    assert response.json()["detail"] == "Saved job does not belong to this profile"
    mock_generate.assert_not_called()
    mock_score.assert_not_called()
    mock_recommendations.assert_not_called()
