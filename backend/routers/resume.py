"""Resume generation router."""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from backend.database.database import get_db
from backend.database.models import User, TailoredResume
from backend.routers.profile import serialize_full_profile
from backend.services.parser_service import parse_job_description
from backend.services.scorer_service import calculate_match_score
from backend.services.resume_builder import (
    generate_tailored_resume,
    generate_resume_html,
    generate_resume_docx,
)
from backend.services.recommender import get_skill_recommendations

router = APIRouter(prefix="/api/resume", tags=["resume"])


class ResumeGenerateRequest(BaseModel):
    user_id: int
    job_description: str
    parsed_job: Optional[dict] = None


@router.post("/generate")
def generate_resume(data: ResumeGenerateRequest, db: Session = Depends(get_db)):
    """Generate a tailored resume from profile + job description."""
    user = db.query(User).filter(User.id == data.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    profile = serialize_full_profile(user)

    # Parse job description if not provided
    parsed_job = data.parsed_job
    if not parsed_job:
        parsed_job = parse_job_description(data.job_description)

    # Generate tailored resume
    resume_content = generate_tailored_resume(profile, data.job_description, parsed_job)

    # Generate HTML preview
    user_info = profile["user"]
    html_preview = generate_resume_html(resume_content, user_info)

    # Calculate match score
    match_result = calculate_match_score(profile, parsed_job)

    # Get recommendations
    recommendations = get_skill_recommendations(match_result, profile)

    # Save to history
    tailored = TailoredResume(
        user_id=data.user_id,
        job_title_applied=parsed_job.get("job_title"),
        company_name=parsed_job.get("company_name"),
        job_description_text=data.job_description,
        generated_resume_content=resume_content,
        match_score=match_result.get("overall_score"),
        matched_keywords=match_result.get("breakdown", {}).get("hard_skills", {}).get("matched", []),
        missing_keywords=match_result.get("breakdown", {}).get("hard_skills", {}).get("missing", []),
        recommendations=recommendations,
    )
    db.add(tailored)
    db.commit()
    db.refresh(tailored)

    return {
        "resume_id": tailored.id,
        "resume_content": resume_content,
        "html_preview": html_preview,
        "match_score": match_result,
        "recommendations": recommendations,
        "parsed_job": parsed_job,
    }


@router.get("/{resume_id}/download")
def download_resume(resume_id: int, db: Session = Depends(get_db)):
    """Download a generated resume as .docx."""
    tailored = db.query(TailoredResume).filter(TailoredResume.id == resume_id).first()
    if not tailored:
        raise HTTPException(status_code=404, detail="Resume not found")

    user = db.query(User).filter(User.id == tailored.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    profile = serialize_full_profile(user)
    user_info = profile["user"]

    docx_buffer = generate_resume_docx(tailored.generated_resume_content, user_info)

    filename = f"resume_{user.name.replace(' ', '_')}_{tailored.job_title_applied or 'tailored'}.docx"

    return StreamingResponse(
        docx_buffer,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@router.get("/{resume_id}")
def get_resume(resume_id: int, db: Session = Depends(get_db)):
    """Get a saved tailored resume by ID."""
    tailored = db.query(TailoredResume).filter(TailoredResume.id == resume_id).first()
    if not tailored:
        raise HTTPException(status_code=404, detail="Resume not found")

    user = db.query(User).filter(User.id == tailored.user_id).first()
    user_info = serialize_full_profile(user)["user"] if user else {}
    html_preview = generate_resume_html(tailored.generated_resume_content or {}, user_info)

    return {
        "id": tailored.id,
        "user_id": tailored.user_id,
        "job_title_applied": tailored.job_title_applied,
        "company_name": tailored.company_name,
        "match_score": tailored.match_score,
        "resume_content": tailored.generated_resume_content,
        "html_preview": html_preview,
        "matched_keywords": tailored.matched_keywords,
        "missing_keywords": tailored.missing_keywords,
        "recommendations": tailored.recommendations,
        "created_at": str(tailored.created_at) if tailored.created_at else None,
    }


@router.get("/history/{user_id}")
def get_resume_history(user_id: int, db: Session = Depends(get_db)):
    """Get all tailored resumes for a user."""
    resumes = (
        db.query(TailoredResume)
        .filter(TailoredResume.user_id == user_id)
        .order_by(TailoredResume.created_at.desc())
        .all()
    )
    return [
        {
            "id": r.id,
            "job_title_applied": r.job_title_applied,
            "company_name": r.company_name,
            "match_score": r.match_score,
            "created_at": str(r.created_at) if r.created_at else None,
        }
        for r in resumes
    ]
