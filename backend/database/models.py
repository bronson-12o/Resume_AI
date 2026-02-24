from sqlalchemy import (
    Column, Integer, String, Float, Boolean, Text, DateTime, ForeignKey, JSON,
)
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from backend.database.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    phone = Column(String(50), nullable=True)
    location = Column(String(255), nullable=True)
    linkedin_url = Column(String(500), nullable=True)
    portfolio_url = Column(String(500), nullable=True)
    professional_summary = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    experiences = relationship("WorkExperience", back_populates="user", cascade="all, delete-orphan")
    education = relationship("Education", back_populates="user", cascade="all, delete-orphan")
    skills = relationship("Skill", back_populates="user", cascade="all, delete-orphan")
    projects = relationship("Project", back_populates="user", cascade="all, delete-orphan")
    certifications = relationship("Certification", back_populates="user", cascade="all, delete-orphan")
    tailored_resumes = relationship("TailoredResume", back_populates="user", cascade="all, delete-orphan")


class WorkExperience(Base):
    __tablename__ = "work_experiences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    job_title = Column(String(255), nullable=False)
    company_name = Column(String(255), nullable=False)
    location = Column(String(255), nullable=True)
    start_date = Column(String(20), nullable=False)
    end_date = Column(String(20), nullable=True)
    bullet_points = Column(JSON, default=list)
    skills_used = Column(JSON, default=list)
    is_current = Column(Boolean, default=False)

    user = relationship("User", back_populates="experiences")


class Education(Base):
    __tablename__ = "education"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    degree = Column(String(255), nullable=False)
    institution = Column(String(255), nullable=False)
    graduation_date = Column(String(20), nullable=True)
    gpa = Column(String(10), nullable=True)
    relevant_coursework = Column(JSON, default=list)

    user = relationship("User", back_populates="education")


class Skill(Base):
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    skill_name = Column(String(255), nullable=False)
    category = Column(String(50), nullable=False)  # programming, data, soft_skill, tool, framework
    proficiency_level = Column(String(20), default="intermediate")  # beginner, intermediate, advanced

    user = relationship("User", back_populates="skills")


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    project_name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    technologies_used = Column(JSON, default=list)
    url = Column(String(500), nullable=True)
    bullet_points = Column(JSON, default=list)

    user = relationship("User", back_populates="projects")


class Certification(Base):
    __tablename__ = "certifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    cert_name = Column(String(255), nullable=False)
    issuing_org = Column(String(255), nullable=True)
    date_obtained = Column(String(20), nullable=True)
    expiry_date = Column(String(20), nullable=True)
    credential_url = Column(String(500), nullable=True)

    user = relationship("User", back_populates="certifications")


class TailoredResume(Base):
    __tablename__ = "tailored_resumes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    job_title_applied = Column(String(255), nullable=True)
    company_name = Column(String(255), nullable=True)
    job_description_text = Column(Text, nullable=True)
    generated_resume_content = Column(JSON, nullable=True)
    match_score = Column(Float, nullable=True)
    matched_keywords = Column(JSON, default=list)
    missing_keywords = Column(JSON, default=list)
    recommendations = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="tailored_resumes")
