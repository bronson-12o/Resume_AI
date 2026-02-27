"""Tests for the job tracker router."""
import pytest
from unittest.mock import patch


def test_save_job(client, sample_user):
    response = client.post("/api/tracker", json={
        "user_id": sample_user["id"],
        "job_title": "Software Engineer",
        "company_name": "Google",
    })
    assert response.status_code == 200
    data = response.json()
    assert data["job_title"] == "Software Engineer"
    assert data["company_name"] == "Google"
    assert data["status"] == "saved"
    assert "id" in data


@patch("backend.routers.jobs_tracker.parse_job_description")
@patch("backend.routers.jobs_tracker.calculate_match_score")
def test_save_job_with_jd(mock_score, mock_parse, client, sample_user_with_profile):
    mock_parse.return_value = {
        "job_title": "Software Engineer",
        "company_name": "Google",
        "required_skills": ["Python"],
        "preferred_skills": [],
        "ats_keywords": [],
    }
    mock_score.return_value = {"overall_score": 82.5, "verdict": "Strong match"}

    response = client.post("/api/tracker", json={
        "user_id": sample_user_with_profile["id"],
        "job_title": "Software Engineer",
        "job_description_text": "Looking for a Python developer with FastAPI experience...",
    })
    assert response.status_code == 200
    data = response.json()
    assert data["quick_score"] == 82.5
    assert data["parsed_job_data"] is not None


def test_list_saved_jobs(client, sample_user):
    # Create two jobs
    client.post("/api/tracker", json={
        "user_id": sample_user["id"],
        "job_title": "Job A",
    })
    client.post("/api/tracker", json={
        "user_id": sample_user["id"],
        "job_title": "Job B",
    })

    response = client.get(f"/api/tracker/{sample_user['id']}")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert len(data["items"]) == 2


def test_list_saved_jobs_filter_status(client, sample_user):
    # Create a job, then update its status
    create = client.post("/api/tracker", json={
        "user_id": sample_user["id"],
        "job_title": "Applied Job",
    })
    job_id = create.json()["id"]
    client.put(f"/api/tracker/{job_id}", json={"status": "applied"})

    client.post("/api/tracker", json={
        "user_id": sample_user["id"],
        "job_title": "Saved Job",
    })

    # Filter by applied
    response = client.get(f"/api/tracker/{sample_user['id']}?status=applied")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["job_title"] == "Applied Job"


def test_get_saved_job(client, sample_user):
    create = client.post("/api/tracker", json={
        "user_id": sample_user["id"],
        "job_title": "My Job",
        "company_name": "Acme",
    })
    job_id = create.json()["id"]

    response = client.get(f"/api/tracker/{sample_user['id']}/{job_id}")
    assert response.status_code == 200
    assert response.json()["job_title"] == "My Job"


def test_get_nonexistent_job(client, sample_user):
    response = client.get(f"/api/tracker/{sample_user['id']}/99999")
    assert response.status_code == 404


def test_update_job_status(client, sample_user):
    create = client.post("/api/tracker", json={
        "user_id": sample_user["id"],
        "job_title": "Status Test",
    })
    job_id = create.json()["id"]

    response = client.put(f"/api/tracker/{job_id}", json={"status": "applied"})
    assert response.status_code == 200
    assert response.json()["status"] == "applied"


def test_update_job_invalid_status(client, sample_user):
    create = client.post("/api/tracker", json={
        "user_id": sample_user["id"],
        "job_title": "Invalid Status Test",
    })
    job_id = create.json()["id"]

    response = client.put(f"/api/tracker/{job_id}", json={"status": "invalid_status"})
    assert response.status_code == 422


def test_delete_job(client, sample_user):
    create = client.post("/api/tracker", json={
        "user_id": sample_user["id"],
        "job_title": "Delete Me",
    })
    job_id = create.json()["id"]

    response = client.delete(f"/api/tracker/{job_id}")
    assert response.status_code == 200

    # Verify deleted
    get_response = client.get(f"/api/tracker/{sample_user['id']}/{job_id}")
    assert get_response.status_code == 404


def test_job_funnel_stats(client, sample_user):
    # Create jobs with various statuses
    j1 = client.post("/api/tracker", json={"user_id": sample_user["id"], "job_title": "A"}).json()
    j2 = client.post("/api/tracker", json={"user_id": sample_user["id"], "job_title": "B"}).json()
    j3 = client.post("/api/tracker", json={"user_id": sample_user["id"], "job_title": "C"}).json()

    client.put(f"/api/tracker/{j2['id']}", json={"status": "applied"})
    client.put(f"/api/tracker/{j3['id']}", json={"status": "interviewing"})

    response = client.get(f"/api/tracker/{sample_user['id']}/stats/funnel")
    assert response.status_code == 200
    data = response.json()
    assert data["saved"] == 1
    assert data["applied"] == 1
    assert data["interviewing"] == 1
    assert data["total"] == 3
