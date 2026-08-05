"""Match scoring router."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from backend.database.database import get_db
from backend.database.models import User
from backend.routers.profile import serialize_full_profile, get_user_with_profile
from backend.services.scorer_service import calculate_match_score
from backend.services.parser_service import parse_job_description

router = APIRouter(prefix="/api/scoring", tags=["scoring"])


class MatchRequest(BaseModel):
    user_id: int
    parsed_job: dict


class QuickScoreRequest(BaseModel):
    user_id: int
    job_description: str = Field(min_length=1, max_length=50000)


@router.post("/match")
def score_match(data: MatchRequest, db: Session = Depends(get_db)):
    """Calculate match score between a user's profile and a parsed job description."""
    user = get_user_with_profile(db, data.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    profile = serialize_full_profile(user)
    result = calculate_match_score(profile, data.parsed_job)
    return result


@router.post("/quick")
def quick_score(data: QuickScoreRequest, db: Session = Depends(get_db)):
    """Parse a job description and calculate match score in one call."""
    user = get_user_with_profile(db, data.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    profile = serialize_full_profile(user)
    parsed_job = parse_job_description(data.job_description)
    score_result = calculate_match_score(profile, parsed_job)

    return {
        "parsed_job": parsed_job,
        "overall_score": score_result.get("overall_score"),
        "verdict": score_result.get("verdict"),
        "breakdown": score_result.get("breakdown"),
    }
