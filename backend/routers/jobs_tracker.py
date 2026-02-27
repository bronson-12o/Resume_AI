"""Job tracker router - save jobs, track application status."""
import logging

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel
from typing import Literal, Optional

logger = logging.getLogger(__name__)

from sqlalchemy.orm import joinedload

from backend.database.database import get_db
from backend.database.models import User, SavedJob
from backend.routers.profile import serialize_full_profile, get_user_with_profile
from backend.services.parser_service import parse_job_description
from backend.services.scorer_service import calculate_match_score

router = APIRouter(prefix="/api/tracker", tags=["tracker"])


class SaveJobRequest(BaseModel):
    user_id: int
    job_title: str
    company_name: Optional[str] = None
    job_url: Optional[str] = None
    job_description_text: Optional[str] = None
    notes: Optional[str] = None


class UpdateJobRequest(BaseModel):
    status: Optional[Literal["saved", "applied", "interviewing", "offered", "rejected"]] = None
    notes: Optional[str] = None
    job_title: Optional[str] = None
    company_name: Optional[str] = None
    job_url: Optional[str] = None
    applied_date: Optional[str] = None


def _serialize_job(job: SavedJob) -> dict:
    return {
        "id": job.id,
        "user_id": job.user_id,
        "job_title": job.job_title,
        "company_name": job.company_name,
        "job_url": job.job_url,
        "job_description_text": job.job_description_text,
        "parsed_job_data": job.parsed_job_data,
        "quick_score": job.quick_score,
        "status": job.status,
        "applied_date": job.applied_date,
        "notes": job.notes,
        "created_at": str(job.created_at) if job.created_at else None,
        "updated_at": str(job.updated_at) if job.updated_at else None,
        "tailored_resume_ids": [r.id for r in job.tailored_resumes] if job.tailored_resumes else [],
        "cover_letter_ids": [cl.id for cl in job.cover_letters] if job.cover_letters else [],
    }


@router.post("")
def save_job(data: SaveJobRequest, db: Session = Depends(get_db)):
    """Save a job to the tracker. Auto-parses JD and calculates quick score if JD provided."""
    user = get_user_with_profile(db, data.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    parsed_job = None
    quick_score = None

    if data.job_description_text:
        try:
            parsed_job = parse_job_description(data.job_description_text)
            profile = serialize_full_profile(user)
            score_result = calculate_match_score(profile, parsed_job)
            quick_score = score_result.get("overall_score")
        except Exception:
            pass

    job = SavedJob(
        user_id=data.user_id,
        job_title=data.job_title,
        company_name=data.company_name or (parsed_job.get("company_name") if parsed_job else None),
        job_url=data.job_url,
        job_description_text=data.job_description_text,
        parsed_job_data=parsed_job,
        quick_score=quick_score,
        status="saved",
        notes=data.notes,
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return _serialize_job(job)


@router.get("/{user_id}")
def list_saved_jobs(
    user_id: int,
    status: Optional[str] = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """List all saved jobs for a user, optionally filtered by status."""
    base = db.query(SavedJob).filter(SavedJob.user_id == user_id)
    if status:
        base = base.filter(SavedJob.status == status)
    total = base.count()
    jobs = (
        base.options(
            joinedload(SavedJob.tailored_resumes),
            joinedload(SavedJob.cover_letters),
        )
        .order_by(SavedJob.updated_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return {"items": [_serialize_job(j) for j in jobs], "total": total, "skip": skip, "limit": limit}


@router.get("/{user_id}/{job_id}")
def get_saved_job(user_id: int, job_id: int, db: Session = Depends(get_db)):
    """Get a single saved job with full details."""
    job = db.query(SavedJob).filter(
        SavedJob.id == job_id, SavedJob.user_id == user_id
    ).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return _serialize_job(job)


@router.put("/{job_id}")
def update_saved_job(job_id: int, data: UpdateJobRequest, db: Session = Depends(get_db)):
    """Update a saved job's status, notes, etc."""
    job = db.query(SavedJob).filter(SavedJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(job, key, value)

    db.commit()
    db.refresh(job)
    return _serialize_job(job)


@router.delete("/{job_id}")
def delete_saved_job(job_id: int, db: Session = Depends(get_db)):
    """Remove a saved job."""
    job = db.query(SavedJob).filter(SavedJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    db.delete(job)
    db.commit()
    return {"message": "Job deleted"}


@router.get("/{user_id}/stats/funnel")
def get_job_stats(user_id: int, db: Session = Depends(get_db)):
    """Get application funnel stats for dashboard."""
    counts = (
        db.query(SavedJob.status, func.count(SavedJob.id))
        .filter(SavedJob.user_id == user_id)
        .group_by(SavedJob.status)
        .all()
    )
    stats = {status: count for status, count in counts}
    return {
        "saved": stats.get("saved", 0),
        "applied": stats.get("applied", 0),
        "interviewing": stats.get("interviewing", 0),
        "offered": stats.get("offered", 0),
        "rejected": stats.get("rejected", 0),
        "total": sum(stats.values()),
    }
