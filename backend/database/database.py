from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker, DeclarativeBase
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./resume_ai.db")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _run_migrations():
    """Add columns that create_all() cannot add to existing tables."""
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()

    if "tailored_resumes" in existing_tables:
        columns = [col["name"] for col in inspector.get_columns("tailored_resumes")]
        if "saved_job_id" not in columns:
            with engine.begin() as conn:
                conn.execute(text("ALTER TABLE tailored_resumes ADD COLUMN saved_job_id INTEGER"))


def init_db():
    from backend.database.models import (
        User, WorkExperience, Education, Skill, Project,
        Certification, TailoredResume, SavedJob, CoverLetter,
    )
    Base.metadata.create_all(bind=engine)
    _run_migrations()
