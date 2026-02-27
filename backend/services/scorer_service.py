"""Match scoring service - compares user profile against parsed job description."""
import logging
import re

from backend.services.ai_service import ai_service, AIServiceError
from backend.utils.templates import SCORER_SYSTEM_PROMPT

logger = logging.getLogger(__name__)


def calculate_match_score(profile_data: dict, parsed_job: dict) -> dict:
    """
    Calculate match score between a user's profile and a parsed job description.
    Uses AI for nuanced analysis with a rule-based fallback.
    """
    try:
        profile_text = _format_profile_for_ai(profile_data)
        job_text = _format_job_for_ai(parsed_job)

        result = ai_service.generate(
            system_prompt=SCORER_SYSTEM_PROMPT,
            user_prompt=(
                f"Candidate Profile:\n{profile_text}\n\n"
                f"Job Description Data:\n{job_text}"
            ),
            response_format="json",
        )
        return result
    except AIServiceError as e:
        logger.warning(f"AI scoring failed, using fallback: {e}")
        return _fallback_scoring(profile_data, parsed_job)
    except Exception as e:
        logger.error(f"Unexpected error in calculate_match_score: {type(e).__name__}: {e}")
        return _fallback_scoring(profile_data, parsed_job)


def _format_profile_for_ai(profile: dict) -> str:
    """Format profile data as readable text for the AI."""
    lines = []
    user = profile.get("user", {})
    lines.append(f"Name: {user.get('name', 'N/A')}")
    lines.append(f"Summary: {user.get('professional_summary', 'N/A')}")

    lines.append("\nWork Experience:")
    for exp in profile.get("experiences", []):
        lines.append(f"  - {exp['job_title']} at {exp['company_name']} ({exp.get('start_date', '')} - {exp.get('end_date', 'Present')})")
        for bullet in exp.get("bullet_points", []):
            lines.append(f"    * {bullet}")
        if exp.get("skills_used"):
            lines.append(f"    Skills: {', '.join(exp['skills_used'])}")

    lines.append("\nEducation:")
    for edu in profile.get("education", []):
        lines.append(f"  - {edu['degree']} from {edu['institution']} ({edu.get('graduation_date', 'N/A')})")

    lines.append("\nSkills:")
    for skill in profile.get("skills", []):
        lines.append(f"  - {skill['skill_name']} ({skill.get('category', '')}, {skill.get('proficiency_level', '')})")

    lines.append("\nProjects:")
    for proj in profile.get("projects", []):
        lines.append(f"  - {proj['project_name']}: {proj.get('description', '')}")
        for bullet in proj.get("bullet_points", []):
            lines.append(f"    * {bullet}")

    lines.append("\nCertifications:")
    for cert in profile.get("certifications", []):
        lines.append(f"  - {cert['cert_name']} from {cert.get('issuing_org', 'N/A')}")

    return "\n".join(lines)


def _format_job_for_ai(parsed_job: dict) -> str:
    """Format parsed job data as readable text."""
    lines = []
    lines.append(f"Job Title: {parsed_job.get('job_title', 'N/A')}")
    lines.append(f"Seniority: {parsed_job.get('seniority_level', 'N/A')}")
    lines.append(f"Required Skills: {', '.join(parsed_job.get('required_skills', []))}")
    lines.append(f"Preferred Skills: {', '.join(parsed_job.get('preferred_skills', []))}")
    lines.append(f"Years Experience: {parsed_job.get('years_experience', 'N/A')}")
    lines.append(f"Education: {parsed_job.get('education_requirements', 'N/A')}")
    lines.append(f"ATS Keywords: {', '.join(parsed_job.get('ats_keywords', []))}")
    lines.append(f"Responsibilities: {', '.join(parsed_job.get('key_responsibilities', []))}")
    return "\n".join(lines)


def _fallback_scoring(profile: dict, parsed_job: dict) -> dict:
    """Rule-based scoring fallback."""
    user_skills = set()
    for skill in profile.get("skills", []):
        user_skills.add(skill["skill_name"].lower())
    for exp in profile.get("experiences", []):
        for s in exp.get("skills_used", []):
            user_skills.add(s.lower())

    all_text = _get_all_profile_text(profile).lower()

    required = [s.lower() for s in parsed_job.get("required_skills", [])]
    matched_hard = [s for s in required if s in user_skills or s in all_text]
    missing_hard = [s for s in required if s not in matched_hard]
    hard_score = (len(matched_hard) / max(len(required), 1)) * 100

    years_text = parsed_job.get("years_experience", "")
    years_required = 0
    if years_text:
        match = re.search(r"(\d+)", str(years_text))
        if match:
            years_required = int(match.group(1))
    user_years = len(profile.get("experiences", [])) * 2
    exp_score = min(100, (user_years / max(years_required, 1)) * 100)
    exp_notes = f"JD asks for {years_required} years, estimated {user_years} from profile"

    preferred = [s.lower() for s in parsed_job.get("preferred_skills", [])]
    matched_pref = [s for s in preferred if s in user_skills or s in all_text]
    missing_pref = [s for s in preferred if s not in matched_pref]
    pref_score = (len(matched_pref) / max(len(preferred), 1)) * 100

    has_education = len(profile.get("education", [])) > 0
    edu_score = 100 if has_education else 50
    edu_notes = "Has education on file" if has_education else "No education listed"

    ats_keywords = [k.lower() for k in parsed_job.get("ats_keywords", [])]
    matched_kw = [k for k in ats_keywords if k in all_text]
    missing_kw = [k for k in ats_keywords if k not in matched_kw]
    kw_score = (len(matched_kw) / max(len(ats_keywords), 1)) * 100

    overall = (
        hard_score * 0.4 + exp_score * 0.25 + pref_score * 0.15
        + edu_score * 0.10 + kw_score * 0.10
    )

    verdict = _generate_verdict(overall)

    return {
        "overall_score": round(overall, 1),
        "breakdown": {
            "hard_skills": {
                "score": round(hard_score, 1),
                "weight": 40,
                "matched": matched_hard,
                "missing": missing_hard,
            },
            "experience": {
                "score": round(exp_score, 1),
                "weight": 25,
                "notes": exp_notes,
            },
            "preferred_skills": {
                "score": round(pref_score, 1),
                "weight": 15,
                "matched": matched_pref,
                "missing": missing_pref,
            },
            "education": {
                "score": round(edu_score, 1),
                "weight": 10,
                "notes": edu_notes,
            },
            "keyword_density": {
                "score": round(kw_score, 1),
                "weight": 10,
                "top_missing_keywords": missing_kw[:5],
            },
        },
        "verdict": verdict,
    }


def _get_all_profile_text(profile: dict) -> str:
    """Combine all profile text for keyword matching."""
    parts = []
    user = profile.get("user", {})
    parts.append(user.get("professional_summary", ""))

    for exp in profile.get("experiences", []):
        parts.append(exp.get("job_title", ""))
        parts.extend(exp.get("bullet_points", []))
        parts.extend(exp.get("skills_used", []))

    for edu in profile.get("education", []):
        parts.append(edu.get("degree", ""))
        parts.extend(edu.get("relevant_coursework", []))

    for skill in profile.get("skills", []):
        parts.append(skill.get("skill_name", ""))

    for proj in profile.get("projects", []):
        parts.append(proj.get("description", ""))
        parts.extend(proj.get("bullet_points", []))
        parts.extend(proj.get("technologies_used", []))

    return " ".join(parts)


def _generate_verdict(score: float) -> str:
    """Generate a human-readable verdict based on the score."""
    if score >= 85:
        return "Excellent match — your profile aligns strongly with this role"
    elif score >= 70:
        return "Strong match — you meet most requirements with some gaps to address"
    elif score >= 55:
        return "Moderate match — strong foundation but several skill gaps to close"
    elif score >= 40:
        return "Partial match — consider upskilling in key areas before applying"
    else:
        return "Low match — this role requires significant skills you haven't demonstrated yet"
