"""Job description parsing router."""
from fastapi import APIRouter
from pydantic import BaseModel

from backend.services.parser_service import parse_job_description

router = APIRouter(prefix="/api/jobs", tags=["jobs"])


class JobDescriptionInput(BaseModel):
    job_description: str


@router.post("/parse")
def parse_job(data: JobDescriptionInput):
    """Parse a raw job description into structured data."""
    if not data.job_description.strip():
        return {"error": "Job description cannot be empty"}
    result = parse_job_description(data.job_description)
    return result
