"""Tests for the quick score endpoint."""
import pytest
from unittest.mock import patch


@patch("backend.routers.scoring.parse_job_description")
@patch("backend.routers.scoring.calculate_match_score")
def test_quick_score(mock_score, mock_parse, client, sample_user_with_profile):
    mock_parse.return_value = {
        "job_title": "Software Engineer",
        "required_skills": ["Python", "FastAPI"],
        "preferred_skills": ["React"],
        "ats_keywords": ["api", "backend"],
    }
    mock_score.return_value = {
        "overall_score": 78.5,
        "verdict": "Strong match",
        "breakdown": {
            "hard_skills": {"score": 85, "matched": ["Python"], "missing": ["FastAPI"]},
        },
    }

    response = client.post("/api/scoring/quick", json={
        "user_id": sample_user_with_profile["id"],
        "job_description": "Looking for a Python backend engineer...",
    })
    assert response.status_code == 200
    data = response.json()
    assert data["overall_score"] == 78.5
    assert data["verdict"] == "Strong match"
    assert "parsed_job" in data
    assert "breakdown" in data


def test_quick_score_invalid_user(client):
    response = client.post("/api/scoring/quick", json={
        "user_id": 99999,
        "job_description": "Some job description text...",
    })
    assert response.status_code == 404
