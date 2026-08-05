"""Resume generation router."""
import re

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional

from backend.database.database import get_db
from backend.database.models import SavedJob, User, TailoredResume
from backend.routers.profile import serialize_full_profile, get_user_with_profile
from backend.services.parser_service import parse_job_description
from backend.services.scorer_service import calculate_match_score
from backend.services.resume_builder import (
    generate_tailored_resume,
    generate_resume_html,
    generate_resume_docx,
    generate_resume_docx_with_template,
    regenerate_section,
)
from backend.services.recommender import get_skill_recommendations
from backend.services.ai_service import AIServiceError

router = APIRouter(prefix="/api/resume", tags=["resume"])


class ResumeGenerateRequest(BaseModel):
    user_id: int
    job_description: str = Field(min_length=50, max_length=50000)
    parsed_job: Optional[dict] = None
    saved_job_id: Optional[int] = None


class ResumeUpdateRequest(BaseModel):
    generated_resume_content: dict


class SectionRegenerateRequest(BaseModel):
    section_name: str  # professional_summary, work_experience, skills, etc.


@router.post("/generate")
def generate_resume(data: ResumeGenerateRequest, db: Session = Depends(get_db)):
    """Generate a tailored resume from profile + job description."""
    user = get_user_with_profile(db, data.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    profile = serialize_full_profile(user)

    if data.saved_job_id is not None:
        saved_job = db.query(SavedJob).filter(
            SavedJob.id == data.saved_job_id,
            SavedJob.user_id == data.user_id,
        ).first()
        if not saved_job:
            raise HTTPException(status_code=400, detail="Saved job does not belong to this profile")

    # Parse job description if not provided
    parsed_job = data.parsed_job
    if not parsed_job:
        parsed_job = parse_job_description(data.job_description)

    # Generate tailored resume
    try:
        resume_content = generate_tailored_resume(profile, data.job_description, parsed_job)
    except AIServiceError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

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
        match_details=match_result,
        matched_keywords=match_result.get("breakdown", {}).get("hard_skills", {}).get("matched", []),
        missing_keywords=match_result.get("breakdown", {}).get("hard_skills", {}).get("missing", []),
        recommendations=recommendations,
        saved_job_id=data.saved_job_id,
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


@router.put("/{resume_id}")
def update_resume(resume_id: int, data: ResumeUpdateRequest, db: Session = Depends(get_db)):
    """Update the generated resume content (save inline edits)."""
    tailored = db.query(TailoredResume).filter(TailoredResume.id == resume_id).first()
    if not tailored:
        raise HTTPException(status_code=404, detail="Resume not found")

    tailored.generated_resume_content = data.generated_resume_content
    db.commit()
    db.refresh(tailored)

    user = db.query(User).filter(User.id == tailored.user_id).first()
    user_info = serialize_full_profile(user)["user"] if user else {}
    html_preview = generate_resume_html(tailored.generated_resume_content or {}, user_info)

    return {
        "id": tailored.id,
        "resume_content": tailored.generated_resume_content,
        "html_preview": html_preview,
    }


@router.post("/{resume_id}/regenerate-section")
def regenerate_resume_section(resume_id: int, data: SectionRegenerateRequest, db: Session = Depends(get_db)):
    """Regenerate a single section of the resume."""
    tailored = db.query(TailoredResume).filter(TailoredResume.id == resume_id).first()
    if not tailored:
        raise HTTPException(status_code=404, detail="Resume not found")

    user = db.query(User).filter(User.id == tailored.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    profile = serialize_full_profile(user)
    try:
        new_section = regenerate_section(
            section_name=data.section_name,
            current_content=tailored.generated_resume_content or {},
            job_description=tailored.job_description_text or "",
            profile_data=profile,
        )
    except AIServiceError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    # Merge the regenerated section into existing content
    current = tailored.generated_resume_content or {}
    for key, value in new_section.items():
        current[key] = value

    tailored.generated_resume_content = current
    db.commit()
    db.refresh(tailored)

    user_info = profile["user"]
    html_preview = generate_resume_html(current, user_info)

    return {
        "id": tailored.id,
        "resume_content": current,
        "html_preview": html_preview,
        "regenerated_section": data.section_name,
    }


@router.get("/{resume_id}/download")
def download_resume(
    resume_id: int,
    template: str = Query(default="ats_classic", pattern="^(ats_classic|modern|compact)$"),
    db: Session = Depends(get_db),
):
    """Download a generated resume as .docx with template selection."""
    tailored = db.query(TailoredResume).filter(TailoredResume.id == resume_id).first()
    if not tailored:
        raise HTTPException(status_code=404, detail="Resume not found")

    user = db.query(User).filter(User.id == tailored.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    profile = serialize_full_profile(user)
    user_info = profile["user"]

    docx_buffer = generate_resume_docx_with_template(
        tailored.generated_resume_content, user_info, template
    )

    raw_name = f"resume_{user.name}_{tailored.job_title_applied or 'tailored'}.docx"
    filename = re.sub(r"[^\w\s\-.]", "", raw_name).replace(" ", "_")

    return StreamingResponse(
        docx_buffer,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/{resume_id}")
def get_resume(resume_id: int, template: str = Query(default="ats_classic"), db: Session = Depends(get_db)):
    """Get a saved tailored resume by ID."""
    tailored = db.query(TailoredResume).filter(TailoredResume.id == resume_id).first()
    if not tailored:
        raise HTTPException(status_code=404, detail="Resume not found")

    user = db.query(User).filter(User.id == tailored.user_id).first()
    user_info = serialize_full_profile(user)["user"] if user else {}
    html_preview = generate_resume_html(tailored.generated_resume_content or {}, user_info, template)

    return {
        "id": tailored.id,
        "user_id": tailored.user_id,
        "job_title_applied": tailored.job_title_applied,
        "company_name": tailored.company_name,
        "match_score": tailored.match_details or tailored.match_score,
        "job_description_text": tailored.job_description_text,
        "resume_content": tailored.generated_resume_content,
        "html_preview": html_preview,
        "matched_keywords": tailored.matched_keywords,
        "missing_keywords": tailored.missing_keywords,
        "recommendations": tailored.recommendations,
        "created_at": str(tailored.created_at) if tailored.created_at else None,
    }


@router.get("/history/{user_id}")
def get_resume_history(
    user_id: int,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Get all tailored resumes for a user."""
    base = db.query(TailoredResume).filter(TailoredResume.user_id == user_id)
    total = base.count()
    resumes = base.order_by(TailoredResume.created_at.desc()).offset(skip).limit(limit).all()
    items = [
        {
            "id": r.id,
            "job_title_applied": r.job_title_applied,
            "company_name": r.company_name,
            "match_score": r.match_score,
            "created_at": str(r.created_at) if r.created_at else None,
        }
        for r in resumes
    ]
    return {"items": items, "total": total, "skip": skip, "limit": limit}
