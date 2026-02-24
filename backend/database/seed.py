"""Optional seed script to populate the database with sample data."""
from backend.database.database import SessionLocal, init_db
from backend.database.models import User, WorkExperience, Education, Skill, Project, Certification


def seed_sample_data():
    init_db()
    db = SessionLocal()

    try:
        existing = db.query(User).filter(User.email == "jane.doe@example.com").first()
        if existing:
            print("Sample data already exists. Skipping seed.")
            return

        user = User(
            name="Jane Doe",
            email="jane.doe@example.com",
            phone="(555) 123-4567",
            location="San Francisco, CA",
            linkedin_url="https://linkedin.com/in/janedoe",
            portfolio_url="https://janedoe.dev",
            professional_summary=(
                "Results-driven software engineer with 4 years of experience building "
                "scalable web applications and data pipelines. Proficient in Python, "
                "JavaScript, and cloud technologies. Passionate about clean code and "
                "delivering impactful products."
            ),
        )
        db.add(user)
        db.flush()

        experiences = [
            WorkExperience(
                user_id=user.id,
                job_title="Software Engineer",
                company_name="TechCorp Inc.",
                location="San Francisco, CA",
                start_date="2022-01",
                end_date=None,
                is_current=True,
                bullet_points=[
                    "Developed and maintained RESTful APIs serving 50K+ daily active users using Python and FastAPI",
                    "Reduced API response times by 40% through query optimization and Redis caching",
                    "Led migration from monolithic architecture to microservices, improving deployment frequency by 3x",
                    "Mentored 2 junior developers through code reviews and pair programming sessions",
                ],
                skills_used=["Python", "FastAPI", "PostgreSQL", "Redis", "Docker", "AWS"],
            ),
            WorkExperience(
                user_id=user.id,
                job_title="Junior Developer",
                company_name="StartupXYZ",
                location="Oakland, CA",
                start_date="2020-06",
                end_date="2021-12",
                is_current=False,
                bullet_points=[
                    "Built responsive frontend features using React and TypeScript for an e-commerce platform",
                    "Implemented automated testing pipeline that caught 30% more bugs before production",
                    "Collaborated with product team to ship 15+ features in an agile environment",
                ],
                skills_used=["React", "TypeScript", "Node.js", "Jest", "Git"],
            ),
        ]
        db.add_all(experiences)

        education_items = [
            Education(
                user_id=user.id,
                degree="B.S. Computer Science",
                institution="University of California, Berkeley",
                graduation_date="2020-05",
                gpa="3.7",
                relevant_coursework=["Data Structures", "Algorithms", "Databases", "Machine Learning", "Web Development"],
            ),
        ]
        db.add_all(education_items)

        skills = [
            Skill(user_id=user.id, skill_name="Python", category="programming", proficiency_level="advanced"),
            Skill(user_id=user.id, skill_name="JavaScript", category="programming", proficiency_level="advanced"),
            Skill(user_id=user.id, skill_name="TypeScript", category="programming", proficiency_level="intermediate"),
            Skill(user_id=user.id, skill_name="SQL", category="data", proficiency_level="advanced"),
            Skill(user_id=user.id, skill_name="React", category="framework", proficiency_level="advanced"),
            Skill(user_id=user.id, skill_name="FastAPI", category="framework", proficiency_level="advanced"),
            Skill(user_id=user.id, skill_name="Docker", category="tool", proficiency_level="intermediate"),
            Skill(user_id=user.id, skill_name="AWS", category="tool", proficiency_level="intermediate"),
            Skill(user_id=user.id, skill_name="Git", category="tool", proficiency_level="advanced"),
            Skill(user_id=user.id, skill_name="Communication", category="soft_skill", proficiency_level="advanced"),
            Skill(user_id=user.id, skill_name="Team Leadership", category="soft_skill", proficiency_level="intermediate"),
        ]
        db.add_all(skills)

        projects = [
            Project(
                user_id=user.id,
                project_name="TaskFlow",
                description="A real-time collaborative task management application",
                technologies_used=["React", "Node.js", "Socket.io", "MongoDB"],
                url="https://github.com/janedoe/taskflow",
                bullet_points=[
                    "Built real-time collaboration features using WebSockets serving 200+ concurrent users",
                    "Designed and implemented RESTful API with role-based access control",
                    "Deployed on AWS using EC2, S3, and CloudFront with CI/CD pipeline",
                ],
            ),
        ]
        db.add_all(projects)

        certifications = [
            Certification(
                user_id=user.id,
                cert_name="AWS Solutions Architect Associate",
                issuing_org="Amazon Web Services",
                date_obtained="2023-03",
                expiry_date="2026-03",
                credential_url="https://aws.amazon.com/verification/12345",
            ),
        ]
        db.add_all(certifications)

        db.commit()
        print("Sample data seeded successfully!")

    except Exception as e:
        db.rollback()
        print(f"Error seeding data: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_sample_data()
