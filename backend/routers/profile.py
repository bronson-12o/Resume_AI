"""Profile CRUD router - manages the master profile."""
import logging
import re

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.orm import Session, joinedload
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from typing import Literal, Optional

logger = logging.getLogger(__name__)

MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10 MB

from backend.database.database import get_db
from backend.database.models import (
    User, WorkExperience, Education, Skill, Project, Certification,
)

router = APIRouter(prefix="/api/profile", tags=["profile"])


# --- Pydantic Schemas ---

class ProfileModel(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)


class UserCreate(ProfileModel):
    name: str = Field(min_length=1, max_length=255)
    email: EmailStr
    phone: Optional[str] = Field(default=None, max_length=50)
    location: Optional[str] = Field(default=None, max_length=255)
    linkedin_url: Optional[str] = Field(default=None, max_length=500)
    portfolio_url: Optional[str] = Field(default=None, max_length=500)
    professional_summary: Optional[str] = Field(default=None, max_length=5000)

class UserUpdate(ProfileModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(default=None, max_length=50)
    location: Optional[str] = Field(default=None, max_length=255)
    linkedin_url: Optional[str] = Field(default=None, max_length=500)
    portfolio_url: Optional[str] = Field(default=None, max_length=500)
    professional_summary: Optional[str] = Field(default=None, max_length=5000)

class ExperienceCreate(ProfileModel):
    job_title: str = Field(min_length=1, max_length=255)
    company_name: str = Field(min_length=1, max_length=255)
    location: Optional[str] = Field(default=None, max_length=255)
    start_date: str = Field(min_length=1, max_length=20)
    end_date: Optional[str] = Field(default=None, max_length=20)
    bullet_points: list[str] = Field(default_factory=list, max_length=100)
    skills_used: list[str] = Field(default_factory=list, max_length=100)
    is_current: bool = False

class EducationCreate(ProfileModel):
    degree: str = Field(min_length=1, max_length=255)
    institution: str = Field(min_length=1, max_length=255)
    graduation_date: Optional[str] = Field(default=None, max_length=20)
    gpa: Optional[str] = Field(default=None, max_length=10)
    relevant_coursework: list[str] = Field(default_factory=list, max_length=100)

class SkillCreate(ProfileModel):
    skill_name: str = Field(min_length=1, max_length=255)
    category: Literal["programming", "data", "soft_skill", "tool", "framework"]
    proficiency_level: Literal["beginner", "intermediate", "advanced"] = "intermediate"

class ProjectCreate(ProfileModel):
    project_name: str = Field(min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=5000)
    technologies_used: list[str] = Field(default_factory=list, max_length=100)
    url: Optional[str] = Field(default=None, max_length=500)
    bullet_points: list[str] = Field(default_factory=list, max_length=100)

class CertificationCreate(ProfileModel):
    cert_name: str = Field(min_length=1, max_length=255)
    issuing_org: Optional[str] = Field(default=None, max_length=255)
    date_obtained: Optional[str] = Field(default=None, max_length=20)
    expiry_date: Optional[str] = Field(default=None, max_length=20)
    credential_url: Optional[str] = Field(default=None, max_length=500)


# --- Helper to serialize profile ---

def serialize_user(user: User) -> dict:
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "phone": user.phone,
        "location": user.location,
        "linkedin_url": user.linkedin_url,
        "portfolio_url": user.portfolio_url,
        "professional_summary": user.professional_summary,
        "created_at": str(user.created_at) if user.created_at else None,
        "updated_at": str(user.updated_at) if user.updated_at else None,
    }

def serialize_full_profile(user: User) -> dict:
    return {
        "user": serialize_user(user),
        "experiences": [
            {
                "id": e.id,
                "job_title": e.job_title,
                "company_name": e.company_name,
                "location": e.location,
                "start_date": e.start_date,
                "end_date": e.end_date,
                "bullet_points": e.bullet_points or [],
                "skills_used": e.skills_used or [],
                "is_current": e.is_current,
            }
            for e in user.experiences
        ],
        "education": [
            {
                "id": e.id,
                "degree": e.degree,
                "institution": e.institution,
                "graduation_date": e.graduation_date,
                "gpa": e.gpa,
                "relevant_coursework": e.relevant_coursework or [],
            }
            for e in user.education
        ],
        "skills": [
            {
                "id": s.id,
                "skill_name": s.skill_name,
                "category": s.category,
                "proficiency_level": s.proficiency_level,
            }
            for s in user.skills
        ],
        "projects": [
            {
                "id": p.id,
                "project_name": p.project_name,
                "description": p.description,
                "technologies_used": p.technologies_used or [],
                "url": p.url,
                "bullet_points": p.bullet_points or [],
            }
            for p in user.projects
        ],
        "certifications": [
            {
                "id": c.id,
                "cert_name": c.cert_name,
                "issuing_org": c.issuing_org,
                "date_obtained": c.date_obtained,
                "expiry_date": c.expiry_date,
                "credential_url": c.credential_url,
            }
            for c in user.certifications
        ],
    }


def get_user_with_profile(db: Session, user_id: int) -> User:
    """Fetch a user with all profile relationships eagerly loaded (prevents N+1 queries)."""
    user = (
        db.query(User)
        .options(
            joinedload(User.experiences),
            joinedload(User.education),
            joinedload(User.skills),
            joinedload(User.projects),
            joinedload(User.certifications),
        )
        .filter(User.id == user_id)
        .first()
    )
    return user


# --- User CRUD ---

@router.post("")
def create_profile(data: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(**data.model_dump())
    db.add(user)
    db.commit()
    db.refresh(user)
    return serialize_user(user)


@router.get("/{user_id}")
def get_profile(user_id: int, db: Session = Depends(get_db)):
    user = get_user_with_profile(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return serialize_full_profile(user)


@router.get("")
def list_profiles(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    db: Session = Depends(get_db),
):
    total = db.query(User).count()
    users = db.query(User).offset(skip).limit(limit).all()
    return {"items": [serialize_user(u) for u in users], "total": total, "skip": skip, "limit": limit}


@router.put("/{user_id}")
def update_profile(user_id: int, data: UserUpdate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    update_data = data.model_dump(exclude_unset=True)
    if "email" in update_data:
        existing = db.query(User).filter(
            User.email == update_data["email"],
            User.id != user_id,
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")
    for key, value in update_data.items():
        setattr(user, key, value)
    db.commit()
    db.refresh(user)
    return serialize_user(user)


@router.delete("/{user_id}")
def delete_profile(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"message": "Profile deleted"}


# --- Work Experience CRUD ---

@router.post("/{user_id}/experience")
def add_experience(user_id: int, data: ExperienceCreate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    exp = WorkExperience(user_id=user_id, **data.model_dump())
    db.add(exp)
    db.commit()
    db.refresh(exp)
    return {"id": exp.id, **data.model_dump()}


@router.put("/{user_id}/experience/{exp_id}")
def update_experience(user_id: int, exp_id: int, data: ExperienceCreate, db: Session = Depends(get_db)):
    exp = db.query(WorkExperience).filter(
        WorkExperience.id == exp_id, WorkExperience.user_id == user_id
    ).first()
    if not exp:
        raise HTTPException(status_code=404, detail="Experience not found")
    for key, value in data.model_dump().items():
        setattr(exp, key, value)
    db.commit()
    db.refresh(exp)
    return {"id": exp.id, **data.model_dump()}


@router.delete("/{user_id}/experience/{exp_id}")
def delete_experience(user_id: int, exp_id: int, db: Session = Depends(get_db)):
    exp = db.query(WorkExperience).filter(
        WorkExperience.id == exp_id, WorkExperience.user_id == user_id
    ).first()
    if not exp:
        raise HTTPException(status_code=404, detail="Experience not found")
    db.delete(exp)
    db.commit()
    return {"message": "Experience deleted"}


# --- Education CRUD ---

@router.post("/{user_id}/education")
def add_education(user_id: int, data: EducationCreate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    edu = Education(user_id=user_id, **data.model_dump())
    db.add(edu)
    db.commit()
    db.refresh(edu)
    return {"id": edu.id, **data.model_dump()}


@router.put("/{user_id}/education/{edu_id}")
def update_education(user_id: int, edu_id: int, data: EducationCreate, db: Session = Depends(get_db)):
    edu = db.query(Education).filter(
        Education.id == edu_id, Education.user_id == user_id
    ).first()
    if not edu:
        raise HTTPException(status_code=404, detail="Education not found")
    for key, value in data.model_dump().items():
        setattr(edu, key, value)
    db.commit()
    db.refresh(edu)
    return {"id": edu.id, **data.model_dump()}


@router.delete("/{user_id}/education/{edu_id}")
def delete_education(user_id: int, edu_id: int, db: Session = Depends(get_db)):
    edu = db.query(Education).filter(
        Education.id == edu_id, Education.user_id == user_id
    ).first()
    if not edu:
        raise HTTPException(status_code=404, detail="Education not found")
    db.delete(edu)
    db.commit()
    return {"message": "Education deleted"}


# --- Skills CRUD ---

@router.post("/{user_id}/skills")
def add_skill(user_id: int, data: SkillCreate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    skill = Skill(user_id=user_id, **data.model_dump())
    db.add(skill)
    db.commit()
    db.refresh(skill)
    return {"id": skill.id, **data.model_dump()}


@router.put("/{user_id}/skills/{skill_id}")
def update_skill(user_id: int, skill_id: int, data: SkillCreate, db: Session = Depends(get_db)):
    skill = db.query(Skill).filter(
        Skill.id == skill_id, Skill.user_id == user_id
    ).first()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    for key, value in data.model_dump().items():
        setattr(skill, key, value)
    db.commit()
    db.refresh(skill)
    return {"id": skill.id, **data.model_dump()}


@router.delete("/{user_id}/skills/{skill_id}")
def delete_skill(user_id: int, skill_id: int, db: Session = Depends(get_db)):
    skill = db.query(Skill).filter(
        Skill.id == skill_id, Skill.user_id == user_id
    ).first()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    db.delete(skill)
    db.commit()
    return {"message": "Skill deleted"}


# --- Projects CRUD ---

@router.post("/{user_id}/projects")
def add_project(user_id: int, data: ProjectCreate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    project = Project(user_id=user_id, **data.model_dump())
    db.add(project)
    db.commit()
    db.refresh(project)
    return {"id": project.id, **data.model_dump()}


@router.put("/{user_id}/projects/{project_id}")
def update_project(user_id: int, project_id: int, data: ProjectCreate, db: Session = Depends(get_db)):
    project = db.query(Project).filter(
        Project.id == project_id, Project.user_id == user_id
    ).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    for key, value in data.model_dump().items():
        setattr(project, key, value)
    db.commit()
    db.refresh(project)
    return {"id": project.id, **data.model_dump()}


@router.delete("/{user_id}/projects/{project_id}")
def delete_project(user_id: int, project_id: int, db: Session = Depends(get_db)):
    project = db.query(Project).filter(
        Project.id == project_id, Project.user_id == user_id
    ).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    db.delete(project)
    db.commit()
    return {"message": "Project deleted"}


# --- Certifications CRUD ---

@router.post("/{user_id}/certifications")
def add_certification(user_id: int, data: CertificationCreate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    cert = Certification(user_id=user_id, **data.model_dump())
    db.add(cert)
    db.commit()
    db.refresh(cert)
    return {"id": cert.id, **data.model_dump()}


@router.put("/{user_id}/certifications/{cert_id}")
def update_certification(user_id: int, cert_id: int, data: CertificationCreate, db: Session = Depends(get_db)):
    cert = db.query(Certification).filter(
        Certification.id == cert_id, Certification.user_id == user_id
    ).first()
    if not cert:
        raise HTTPException(status_code=404, detail="Certification not found")
    for key, value in data.model_dump().items():
        setattr(cert, key, value)
    db.commit()
    db.refresh(cert)
    return {"id": cert.id, **data.model_dump()}


@router.delete("/{user_id}/certifications/{cert_id}")
def delete_certification(user_id: int, cert_id: int, db: Session = Depends(get_db)):
    cert = db.query(Certification).filter(
        Certification.id == cert_id, Certification.user_id == user_id
    ).first()
    if not cert:
        raise HTTPException(status_code=404, detail="Certification not found")
    db.delete(cert)
    db.commit()
    return {"message": "Certification deleted"}


# --- Resume Import ---

class ImportConfirmData(ProfileModel):
    name: str = Field(min_length=1, max_length=255)
    email: EmailStr
    phone: Optional[str] = Field(default=None, max_length=50)
    location: Optional[str] = Field(default=None, max_length=255)
    linkedin_url: Optional[str] = Field(default=None, max_length=500)
    portfolio_url: Optional[str] = Field(default=None, max_length=500)
    professional_summary: Optional[str] = Field(default=None, max_length=5000)
    experiences: list[ExperienceCreate] = Field(default_factory=list, max_length=100)
    education: list[EducationCreate] = Field(default_factory=list, max_length=100)
    skills: list[SkillCreate] = Field(default_factory=list, max_length=500)
    projects: list[ProjectCreate] = Field(default_factory=list, max_length=100)
    certifications: list[CertificationCreate] = Field(default_factory=list, max_length=100)


@router.post("/import")
async def import_resume(file: UploadFile = File(...)):
    """Upload a resume (PDF/DOCX) and parse it into structured profile data for review."""
    from backend.services.resume_parser import (
        extract_text_from_docx, extract_text_from_pdf, parse_resume_to_profile,
    )

    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in ("pdf", "docx"):
        raise HTTPException(status_code=400, detail="Only PDF and DOCX files are supported")

    content = await file.read()

    if len(content) > MAX_UPLOAD_SIZE:
        raise HTTPException(status_code=413, detail=f"File too large. Maximum size is {MAX_UPLOAD_SIZE // (1024*1024)} MB.")

    # Validate file magic bytes
    if ext == "pdf" and not content[:5].startswith(b"%PDF"):
        raise HTTPException(status_code=400, detail="File does not appear to be a valid PDF")
    if ext == "docx" and not content[:2] == b"PK":
        raise HTTPException(status_code=400, detail="File does not appear to be a valid DOCX")

    try:
        if ext == "docx":
            text = extract_text_from_docx(content)
        else:
            text = extract_text_from_pdf(content)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if not text.strip():
        raise HTTPException(status_code=400, detail="Could not extract text from file")

    try:
        parsed = parse_resume_to_profile(text)
    except ValueError as e:
        raise HTTPException(status_code=502, detail=str(e))
    return parsed


@router.post("/{user_id}/import/confirm")
def confirm_import(user_id: int, data: ImportConfirmData, db: Session = Depends(get_db)):
    """Confirm and save imported resume data to an existing profile."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Update user fields
    for field in ["name", "email", "phone", "location", "linkedin_url", "portfolio_url", "professional_summary"]:
        value = getattr(data, field, None)
        if value is not None:
            setattr(user, field, value)

    # Add experiences
    for exp_data in data.experiences:
        exp = WorkExperience(user_id=user_id, **exp_data.model_dump())
        db.add(exp)

    # Add education
    for edu_data in data.education:
        edu = Education(user_id=user_id, **edu_data.model_dump())
        db.add(edu)

    # Add skills
    for skill_data in data.skills:
        skill = Skill(user_id=user_id, **skill_data.model_dump())
        db.add(skill)

    # Add projects
    for proj_data in data.projects:
        proj = Project(user_id=user_id, **proj_data.model_dump())
        db.add(proj)

    # Add certifications
    for cert_data in data.certifications:
        cert = Certification(user_id=user_id, **cert_data.model_dump())
        db.add(cert)

    db.commit()
    db.refresh(user)
    return serialize_full_profile(user)
