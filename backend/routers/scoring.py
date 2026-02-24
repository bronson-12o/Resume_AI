"""Match scoring router."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from backend.database.database import get_db
from backend.database.models import User
from backend.routers.profile import serialize_full_profile
from backend.services.scorer_service import calculate_match_score

router = APIRouter(prefix="/api/scoring", tags=["scoring"])


class MatchRequest(BaseModel):
    user_id: int
    parsed_job: dict


@router.post("/match")
def score_match(data: MatchRequest, db: Session = Depends(get_db)):
    """Calculate match score between a user's profile and a parsed job description."""
    user = db.query(User).filter(User.id == data.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    profile = serialize_full_profile(user)
    result = calculate_match_score(profile, data.parsed_job)
    return result
