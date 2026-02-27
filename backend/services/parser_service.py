"""Job description parsing service."""
import logging
import re
from collections import Counter

from backend.services.ai_service import ai_service, AIServiceError

logger = logging.getLogger(__name__)


def parse_job_description(job_description_text: str) -> dict:
    """Parse a raw job description into structured data using AI."""
    try:
        result = ai_service.generate(
            system_prompt=_get_parser_prompt(),
            user_prompt=f"Parse the following job description:\n\n{job_description_text}",
            response_format="json",
        )
        return result
    except AIServiceError as e:
        logger.warning(f"AI parsing failed, using fallback: {e}")
        return _fallback_parse(job_description_text)
    except Exception as e:
        logger.error(f"Unexpected error in parse_job_description: {type(e).__name__}: {e}")
        return _fallback_parse(job_description_text)


def _get_parser_prompt():
    from backend.utils.templates import JOB_PARSER_SYSTEM_PROMPT
    return JOB_PARSER_SYSTEM_PROMPT


def _fallback_parse(text: str) -> dict:
    """Basic keyword extraction fallback if AI service fails."""
    text_lower = text.lower()

    # Try to extract job title from first few lines
    lines = text.strip().split("\n")
    job_title = lines[0].strip() if lines else "Unknown"

    # Extract skills using common patterns
    skill_patterns = [
        r"(?:proficient|experience|knowledge|familiar)\s+(?:in|with)\s+([^.;\n]+)",
        r"(?:skills?|requirements?|qualifications?)[\s:]*([^.;\n]+)",
    ]
    skills_found = []
    for pattern in skill_patterns:
        matches = re.findall(pattern, text_lower)
        for match in matches:
            # Split by commas and 'and'
            parts = re.split(r"[,]|\band\b", match)
            skills_found.extend([p.strip() for p in parts if len(p.strip()) > 1])

    # Extract years of experience
    years_match = re.search(r"(\d+)\+?\s*(?:years?|yrs?)\s*(?:of)?\s*(?:experience)?", text_lower)
    years_experience = years_match.group(0) if years_match else None

    # Basic keyword extraction by word frequency
    words = re.findall(r"\b[a-zA-Z]{3,}\b", text)
    word_freq = Counter(words)
    # Filter out common English words
    stop_words = {
        "the", "and", "for", "with", "that", "this", "you", "are", "will",
        "our", "your", "from", "have", "has", "been", "their", "they",
        "about", "would", "other", "which", "some", "can", "may", "also",
        "not", "all", "but", "more", "into", "than", "its", "who", "what",
        "should", "must", "these", "those", "such", "each", "any", "both",
        "work", "working", "ability", "experience", "strong", "team",
    }
    keywords = [
        word for word, count in word_freq.most_common(30)
        if word.lower() not in stop_words
    ]

    # Detect seniority
    seniority = "mid"
    if any(term in text_lower for term in ["senior", "sr.", "lead", "principal", "staff"]):
        seniority = "senior"
    elif any(term in text_lower for term in ["junior", "jr.", "entry", "associate", "intern"]):
        seniority = "entry"

    return {
        "job_title": job_title,
        "company_name": None,
        "required_skills": skills_found[:10],
        "preferred_skills": [],
        "years_experience": years_experience,
        "education_requirements": None,
        "key_responsibilities": [],
        "ats_keywords": keywords[:15],
        "seniority_level": seniority,
    }
