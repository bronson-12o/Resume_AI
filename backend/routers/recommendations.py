"""Recommendations router - skill gaps and sector suggestions."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from backend.database.database import get_db
from backend.database.models import User
from backend.routers.profile import serialize_full_profile
from backend.services.recommender import get_skill_recommendations, get_sector_suggestions

router = APIRouter(prefix="/api/recommendations", tags=["recommendations"])


class SkillRecommendationRequest(BaseModel):
    match_result: dict
    user_id: int


class SectorRequest(BaseModel):
    user_id: int


@router.post("/skills")
def recommend_skills(data: SkillRecommendationRequest, db: Session = Depends(get_db)):
    """Get skill gap recommendations based on match scoring result."""
    user = db.query(User).filter(User.id == data.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    profile = serialize_full_profile(user)
    result = get_skill_recommendations(data.match_result, profile)
    return result


@router.post("/sectors")
def explore_sectors(data: SectorRequest, db: Session = Depends(get_db)):
    """Suggest alternative job titles and industries for the user."""
    user = db.query(User).filter(User.id == data.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    profile = serialize_full_profile(user)
    result = get_sector_suggestions(profile)
    return result
