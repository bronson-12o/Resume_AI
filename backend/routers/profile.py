"""Profile CRUD router - manages the master profile."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Optional

from backend.database.database import get_db
from backend.database.models import (
    User, WorkExperience, Education, Skill, Project, Certification,
)

router = APIRouter(prefix="/api/profile", tags=["profile"])


# --- Pydantic Schemas ---

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    location: Optional[str] = None
    linkedin_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    professional_summary: Optional[str] = None

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    linkedin_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    professional_summary: Optional[str] = None

class ExperienceCreate(BaseModel):
    job_title: str
    company_name: str
    location: Optional[str] = None
    start_date: str
    end_date: Optional[str] = None
    bullet_points: list[str] = []
    skills_used: list[str] = []
    is_current: bool = False

class EducationCreate(BaseModel):
    degree: str
    institution: str
    graduation_date: Optional[str] = None
    gpa: Optional[str] = None
    relevant_coursework: list[str] = []

class SkillCreate(BaseModel):
    skill_name: str
    category: str  # programming, data, soft_skill, tool, framework
    proficiency_level: str = "intermediate"  # beginner, intermediate, advanced

class ProjectCreate(BaseModel):
    project_name: str
    description: Optional[str] = None
    technologies_used: list[str] = []
    url: Optional[str] = None
    bullet_points: list[str] = []

class CertificationCreate(BaseModel):
    cert_name: str
    issuing_org: Optional[str] = None
    date_obtained: Optional[str] = None
    expiry_date: Optional[str] = None
    credential_url: Optional[str] = None


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
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return serialize_full_profile(user)


@router.get("")
def list_profiles(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return [serialize_user(u) for u in users]


@router.put("/{user_id}")
def update_profile(user_id: int, data: UserUpdate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    update_data = data.model_dump(exclude_unset=True)
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
