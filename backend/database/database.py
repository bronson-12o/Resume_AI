import logging
import os

from sqlalchemy import create_engine, event, inspect, text
from sqlalchemy.orm import sessionmaker, DeclarativeBase

logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./resume_ai.db")

engine_options = {"pool_pre_ping": True}
if DATABASE_URL.startswith("sqlite"):
    engine_options["connect_args"] = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, **engine_options)


if DATABASE_URL.startswith("sqlite"):
    @event.listens_for(engine, "connect")
    def _enable_sqlite_foreign_keys(dbapi_connection, _connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()
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
    """Add columns and indexes that create_all() cannot add to existing tables."""
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()

    # Add saved_job_id column to tailored_resumes if missing
    if "tailored_resumes" in existing_tables:
        columns = [col["name"] for col in inspector.get_columns("tailored_resumes")]
        if "saved_job_id" not in columns:
            with engine.begin() as conn:
                conn.execute(text("ALTER TABLE tailored_resumes ADD COLUMN saved_job_id INTEGER"))
                logger.info("Added saved_job_id column to tailored_resumes")
        if "match_details" not in columns:
            with engine.begin() as conn:
                conn.execute(text("ALTER TABLE tailored_resumes ADD COLUMN match_details JSON"))
                logger.info("Added match_details column to tailored_resumes")

    # Create indexes on foreign keys for existing tables
    existing_indexes = set()
    for table_name in existing_tables:
        for idx in inspector.get_indexes(table_name):
            existing_indexes.add(idx["name"])

    index_definitions = [
        ("ix_work_experiences_user_id", "work_experiences", "user_id"),
        ("ix_education_user_id", "education", "user_id"),
        ("ix_skills_user_id", "skills", "user_id"),
        ("ix_projects_user_id", "projects", "user_id"),
        ("ix_certifications_user_id", "certifications", "user_id"),
        ("ix_tailored_resumes_user_id", "tailored_resumes", "user_id"),
        ("ix_tailored_resumes_saved_job_id", "tailored_resumes", "saved_job_id"),
        ("ix_saved_jobs_user_id", "saved_jobs", "user_id"),
        ("ix_cover_letters_user_id", "cover_letters", "user_id"),
        ("ix_cover_letters_saved_job_id", "cover_letters", "saved_job_id"),
    ]

    with engine.begin() as conn:
        for idx_name, table_name, column_name in index_definitions:
            if table_name in existing_tables and idx_name not in existing_indexes:
                try:
                    conn.execute(text(f"CREATE INDEX IF NOT EXISTS {idx_name} ON {table_name} ({column_name})"))
                except Exception:
                    pass  # Index may already exist under a different name


def init_db():
    from backend.database.models import (
        User, WorkExperience, Education, Skill, Project,
        Certification, TailoredResume, SavedJob, CoverLetter,
    )
    Base.metadata.create_all(bind=engine)
    _run_migrations()
    logger.info("Database initialized")
