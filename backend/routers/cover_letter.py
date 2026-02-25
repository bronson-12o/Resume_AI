"""Cover letter generation router."""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from backend.database.database import get_db
from backend.database.models import User, CoverLetter, TailoredResume
from backend.routers.profile import serialize_full_profile
from backend.services.parser_service import parse_job_description
from backend.services.cover_letter_builder import generate_cover_letter, generate_cover_letter_docx

router = APIRouter(prefix="/api/cover-letter", tags=["cover-letter"])


class CoverLetterGenerateRequest(BaseModel):
    user_id: int
    job_description: str
    parsed_job: Optional[dict] = None
    tailored_resume_id: Optional[int] = None
    saved_job_id: Optional[int] = None
    tone: str = "formal"  # formal, conversational, enthusiastic


class CoverLetterUpdateRequest(BaseModel):
    content: str


@router.post("/generate")
def generate(data: CoverLetterGenerateRequest, db: Session = Depends(get_db)):
    """Generate a tailored cover letter."""
    user = db.query(User).filter(User.id == data.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    profile = serialize_full_profile(user)

    parsed_job = data.parsed_job
    if not parsed_job:
        parsed_job = parse_job_description(data.job_description)

    content = generate_cover_letter(profile, data.job_description, parsed_job, data.tone)

    cl = CoverLetter(
        user_id=data.user_id,
        tailored_resume_id=data.tailored_resume_id,
        saved_job_id=data.saved_job_id,
        job_title=parsed_job.get("job_title"),
        company_name=parsed_job.get("company_name"),
        content=content,
        tone=data.tone,
    )
    db.add(cl)
    db.commit()
    db.refresh(cl)

    return {
        "id": cl.id,
        "content": cl.content,
        "tone": cl.tone,
        "job_title": cl.job_title,
        "company_name": cl.company_name,
        "created_at": str(cl.created_at) if cl.created_at else None,
    }


@router.get("/{cover_letter_id}")
def get_cover_letter(cover_letter_id: int, db: Session = Depends(get_db)):
    """Retrieve a cover letter."""
    cl = db.query(CoverLetter).filter(CoverLetter.id == cover_letter_id).first()
    if not cl:
        raise HTTPException(status_code=404, detail="Cover letter not found")
    return {
        "id": cl.id,
        "user_id": cl.user_id,
        "content": cl.content,
        "tone": cl.tone,
        "job_title": cl.job_title,
        "company_name": cl.company_name,
        "tailored_resume_id": cl.tailored_resume_id,
        "saved_job_id": cl.saved_job_id,
        "created_at": str(cl.created_at) if cl.created_at else None,
    }


@router.put("/{cover_letter_id}")
def update_cover_letter(cover_letter_id: int, data: CoverLetterUpdateRequest, db: Session = Depends(get_db)):
    """Save edits to a cover letter."""
    cl = db.query(CoverLetter).filter(CoverLetter.id == cover_letter_id).first()
    if not cl:
        raise HTTPException(status_code=404, detail="Cover letter not found")
    cl.content = data.content
    db.commit()
    db.refresh(cl)
    return {
        "id": cl.id,
        "content": cl.content,
        "tone": cl.tone,
    }


@router.get("/{cover_letter_id}/download")
def download_cover_letter(cover_letter_id: int, db: Session = Depends(get_db)):
    """Download cover letter as .docx."""
    cl = db.query(CoverLetter).filter(CoverLetter.id == cover_letter_id).first()
    if not cl:
        raise HTTPException(status_code=404, detail="Cover letter not found")

    user = db.query(User).filter(User.id == cl.user_id).first()
    user_info = serialize_full_profile(user)["user"] if user else {}

    docx_buffer = generate_cover_letter_docx(cl.content or "", user_info)

    filename = f"cover_letter_{cl.company_name or 'letter'}_{cl.job_title or ''}.docx".replace(" ", "_")

    return StreamingResponse(
        docx_buffer,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@router.get("/history/{user_id}")
def get_cover_letter_history(user_id: int, db: Session = Depends(get_db)):
    """List all cover letters for a user."""
    letters = (
        db.query(CoverLetter)
        .filter(CoverLetter.user_id == user_id)
        .order_by(CoverLetter.created_at.desc())
        .all()
    )
    return [
        {
            "id": cl.id,
            "job_title": cl.job_title,
            "company_name": cl.company_name,
            "tone": cl.tone,
            "tailored_resume_id": cl.tailored_resume_id,
            "created_at": str(cl.created_at) if cl.created_at else None,
        }
        for cl in letters
    ]
