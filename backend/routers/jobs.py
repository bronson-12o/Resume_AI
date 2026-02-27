"""Job description parsing router."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.services.parser_service import parse_job_description

router = APIRouter(prefix="/api/jobs", tags=["jobs"])


class JobDescriptionInput(BaseModel):
    job_description: str = Field(min_length=1)


@router.post("/parse")
def parse_job(data: JobDescriptionInput):
    """Parse a raw job description into structured data."""
    if not data.job_description.strip():
        raise HTTPException(status_code=400, detail="Job description cannot be empty")
    result = parse_job_description(data.job_description)
    return result
