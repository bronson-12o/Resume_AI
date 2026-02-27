"""Tests for the cover letter router."""
import pytest
from unittest.mock import patch


@patch("backend.routers.cover_letter.generate_cover_letter")
@patch("backend.routers.cover_letter.parse_job_description")
def test_generate_cover_letter(mock_parse, mock_gen, client, sample_user_with_profile):
    mock_parse.return_value = {
        "job_title": "Developer",
        "company_name": "Acme",
        "required_skills": ["Python"],
        "preferred_skills": [],
        "key_responsibilities": ["Build APIs"],
        "ats_keywords": [],
    }
    mock_gen.return_value = "Dear Hiring Manager,\n\nI am excited to apply..."

    response = client.post("/api/cover-letter/generate", json={
        "user_id": sample_user_with_profile["id"],
        "job_description": "Looking for a Python developer...",
        "tone": "formal",
    })
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["content"] == "Dear Hiring Manager,\n\nI am excited to apply..."
    assert data["tone"] == "formal"


def test_generate_cover_letter_invalid_user(client):
    response = client.post("/api/cover-letter/generate", json={
        "user_id": 99999,
        "job_description": "Test JD for a developer role with various requirements...",
        "tone": "formal",
    })
    assert response.status_code == 404


def test_generate_cover_letter_invalid_tone(client, sample_user):
    response = client.post("/api/cover-letter/generate", json={
        "user_id": sample_user["id"],
        "job_description": "Test JD",
        "tone": "aggressive",
    })
    assert response.status_code == 422


@patch("backend.routers.cover_letter.generate_cover_letter")
@patch("backend.routers.cover_letter.parse_job_description")
def test_get_cover_letter(mock_parse, mock_gen, client, sample_user_with_profile):
    mock_parse.return_value = {
        "job_title": "Dev", "company_name": "Co",
        "required_skills": [], "preferred_skills": [],
        "key_responsibilities": [], "ats_keywords": [],
    }
    mock_gen.return_value = "Test content"

    create = client.post("/api/cover-letter/generate", json={
        "user_id": sample_user_with_profile["id"],
        "job_description": "Test JD for a developer role with various requirements...",
        "tone": "formal",
    })
    cl_id = create.json()["id"]

    response = client.get(f"/api/cover-letter/{cl_id}")
    assert response.status_code == 200
    assert response.json()["content"] == "Test content"


def test_get_nonexistent_cover_letter(client):
    response = client.get("/api/cover-letter/99999")
    assert response.status_code == 404


@patch("backend.routers.cover_letter.generate_cover_letter")
@patch("backend.routers.cover_letter.parse_job_description")
def test_update_cover_letter(mock_parse, mock_gen, client, sample_user_with_profile):
    mock_parse.return_value = {
        "job_title": "Dev", "company_name": "Co",
        "required_skills": [], "preferred_skills": [],
        "key_responsibilities": [], "ats_keywords": [],
    }
    mock_gen.return_value = "Original"

    create = client.post("/api/cover-letter/generate", json={
        "user_id": sample_user_with_profile["id"],
        "job_description": "Test JD for a developer role with various requirements...",
        "tone": "formal",
    })
    cl_id = create.json()["id"]

    response = client.put(f"/api/cover-letter/{cl_id}", json={"content": "Updated content"})
    assert response.status_code == 200
    assert response.json()["content"] == "Updated content"


@patch("backend.routers.cover_letter.generate_cover_letter")
@patch("backend.routers.cover_letter.parse_job_description")
def test_download_cover_letter(mock_parse, mock_gen, client, sample_user_with_profile):
    mock_parse.return_value = {
        "job_title": "Dev", "company_name": "Co",
        "required_skills": [], "preferred_skills": [],
        "key_responsibilities": [], "ats_keywords": [],
    }
    mock_gen.return_value = "Cover letter content for download."

    create = client.post("/api/cover-letter/generate", json={
        "user_id": sample_user_with_profile["id"],
        "job_description": "Test JD for a developer role with various requirements...",
        "tone": "formal",
    })
    cl_id = create.json()["id"]

    response = client.get(f"/api/cover-letter/{cl_id}/download")
    assert response.status_code == 200
    assert "application/vnd" in response.headers["content-type"]


@patch("backend.routers.cover_letter.generate_cover_letter")
@patch("backend.routers.cover_letter.parse_job_description")
def test_cover_letter_history(mock_parse, mock_gen, client, sample_user_with_profile):
    mock_parse.return_value = {
        "job_title": "Dev", "company_name": "Co",
        "required_skills": [], "preferred_skills": [],
        "key_responsibilities": [], "ats_keywords": [],
    }
    mock_gen.return_value = "Content"

    user_id = sample_user_with_profile["id"]

    client.post("/api/cover-letter/generate", json={
        "user_id": user_id,
        "job_description": "Test JD for a developer role with various requirements...",
        "tone": "formal",
    })
    client.post("/api/cover-letter/generate", json={
        "user_id": user_id,
        "job_description": "Another JD for a developer role with various requirements...",
        "tone": "conversational",
    })

    response = client.get(f"/api/cover-letter/history/{user_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert len(data["items"]) == 2
