"""Tests for resume import endpoints."""
import io
import pytest
from unittest.mock import patch


@patch("backend.services.resume_parser.parse_resume_to_profile")
@patch("backend.services.resume_parser.extract_text_from_docx")
def test_import_docx(mock_extract, mock_parse, client):
    mock_extract.return_value = "John Doe\nSoftware Engineer\nPython, FastAPI"
    mock_parse.return_value = {
        "name": "John Doe",
        "email": "john@example.com",
        "experiences": [{"job_title": "Software Engineer", "company_name": "TechCo", "start_date": "2020"}],
        "skills": [{"skill_name": "Python", "category": "programming"}],
    }

    # Create a minimal valid DOCX (PK magic bytes)
    from docx import Document
    doc = Document()
    doc.add_paragraph("John Doe - Software Engineer")
    buf = io.BytesIO()
    doc.save(buf)
    buf.seek(0)

    response = client.post(
        "/api/profile/import",
        files={"file": ("resume.docx", buf, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "John Doe"


@patch("backend.services.resume_parser.parse_resume_to_profile")
@patch("backend.services.resume_parser.extract_text_from_pdf")
def test_import_pdf(mock_extract, mock_parse, client):
    mock_extract.return_value = "Jane Smith\nData Scientist\nPython, TensorFlow"
    mock_parse.return_value = {
        "name": "Jane Smith",
        "email": "jane@example.com",
        "skills": [{"skill_name": "Python", "category": "programming"}],
    }

    # Create a minimal valid PDF
    pdf_content = b"%PDF-1.4 minimal pdf content for testing"

    response = client.post(
        "/api/profile/import",
        files={"file": ("resume.pdf", io.BytesIO(pdf_content), "application/pdf")},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Jane Smith"


def test_import_invalid_file_type(client):
    response = client.post(
        "/api/profile/import",
        files={"file": ("resume.txt", io.BytesIO(b"plain text"), "text/plain")},
    )
    assert response.status_code == 400
    assert "Only PDF and DOCX" in response.json()["detail"]


def test_import_oversized_file(client):
    # Create a file > 10MB
    large_content = b"PK" + b"x" * (11 * 1024 * 1024)

    response = client.post(
        "/api/profile/import",
        files={"file": ("resume.docx", io.BytesIO(large_content), "application/vnd.openxmlformats-officedocument.wordprocessingml.document")},
    )
    assert response.status_code == 413


def test_confirm_import(client, sample_user):
    user_id = sample_user["id"]

    response = client.post(f"/api/profile/{user_id}/import/confirm", json={
        "name": "Updated Name",
        "email": "updated@example.com",
        "experiences": [
            {"job_title": "Dev", "company_name": "Co", "start_date": "2020-01"},
        ],
        "education": [
            {"degree": "BS CS", "institution": "MIT"},
        ],
        "skills": [
            {"skill_name": "Python", "category": "programming"},
        ],
        "projects": [],
        "certifications": [],
    })
    assert response.status_code == 200
    data = response.json()
    assert data["user"]["name"] == "Updated Name"
    assert len(data["experiences"]) >= 1
    assert len(data["skills"]) >= 1
