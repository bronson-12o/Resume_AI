"""Tests for input validation improvements."""
import pytest


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
