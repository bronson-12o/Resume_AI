"""Skill gap recommendations and sector exploration service."""
from backend.services.ai_service import ai_service
from backend.utils.templates import RECOMMENDER_SYSTEM_PROMPT, SECTOR_EXPLORER_SYSTEM_PROMPT
from backend.utils.ats_keywords import SKILL_LEARNING_RESOURCES, KEYWORD_SYNONYMS


def get_skill_recommendations(match_result: dict, profile_data: dict) -> dict:
    """Generate skill gap recommendations based on match scoring results."""
    try:
        result = ai_service.generate(
            system_prompt=RECOMMENDER_SYSTEM_PROMPT,
            user_prompt=(
                f"Match Scoring Result:\n{_format_match_result(match_result)}\n\n"
                f"Candidate Profile Summary:\n{_format_profile_summary(profile_data)}\n\n"
                f"Provide specific, actionable recommendations to improve this candidate's match."
            ),
            response_format="json",
        )
        # Enrich with curated learning resources
        result = _enrich_with_resources(result)
        return result
    except Exception:
        return _fallback_recommendations(match_result)


def get_sector_suggestions(profile_data: dict) -> dict:
    """Suggest alternative job titles and industries based on user's profile."""
    profile_summary = _format_profile_summary(profile_data)

    result = ai_service.generate(
        system_prompt=SECTOR_EXPLORER_SYSTEM_PROMPT,
        user_prompt=(
            f"Analyze this candidate's profile and suggest alternative career paths:\n\n"
            f"{profile_summary}"
        ),
        response_format="json",
    )
    return result


def _format_match_result(match_result: dict) -> str:
    """Format match result as readable text."""
    lines = [f"Overall Score: {match_result.get('overall_score', 'N/A')}/100"]
    breakdown = match_result.get("breakdown", {})

    for category, data in breakdown.items():
        lines.append(f"\n{category.replace('_', ' ').title()}:")
        lines.append(f"  Score: {data.get('score', 'N/A')}")
        if data.get("matched"):
            lines.append(f"  Matched: {', '.join(data['matched'])}")
        if data.get("missing"):
            lines.append(f"  Missing: {', '.join(data['missing'])}")
        if data.get("notes"):
            lines.append(f"  Notes: {data['notes']}")
        if data.get("top_missing_keywords"):
            lines.append(f"  Missing Keywords: {', '.join(data['top_missing_keywords'])}")

    lines.append(f"\nVerdict: {match_result.get('verdict', '')}")
    return "\n".join(lines)


def _format_profile_summary(profile: dict) -> str:
    """Create a concise profile summary."""
    lines = []
    user = profile.get("user", {})
    lines.append(f"Summary: {user.get('professional_summary', 'N/A')}")

    skills = [s["skill_name"] for s in profile.get("skills", [])]
    lines.append(f"Skills: {', '.join(skills)}")

    for exp in profile.get("experiences", []):
        lines.append(f"Experience: {exp['job_title']} at {exp['company_name']}")

    for edu in profile.get("education", []):
        lines.append(f"Education: {edu['degree']} from {edu['institution']}")

    return "\n".join(lines)


def _enrich_with_resources(recommendations: dict) -> dict:
    """Enrich AI recommendations with curated learning resources."""
    for rec in recommendations.get("skill_recommendations", []):
        skill_lower = rec.get("skill", "").lower()
        if skill_lower in SKILL_LEARNING_RESOURCES:
            resource = SKILL_LEARNING_RESOURCES[skill_lower]
            rec["curated_resource"] = resource

    # Enrich keyword suggestions with synonym info
    for suggestion in recommendations.get("keyword_suggestions", []):
        keyword = suggestion.get("missing_keyword", "").lower()
        if keyword in KEYWORD_SYNONYMS:
            suggestion["known_equivalents"] = KEYWORD_SYNONYMS[keyword]

    return recommendations


def _fallback_recommendations(match_result: dict) -> dict:
    """Generate basic recommendations without AI."""
    recommendations = {
        "skill_recommendations": [],
        "keyword_suggestions": [],
        "general_advice": "",
    }

    breakdown = match_result.get("breakdown", {})

    # Missing hard skills
    for skill in breakdown.get("hard_skills", {}).get("missing", []):
        skill_lower = skill.lower()
        rec = {
            "skill": skill,
            "priority": "high",
            "reason": "Required skill listed in job description",
            "learning_path": "Search for online courses or tutorials",
            "estimated_time": "2-4 weeks",
        }
        if skill_lower in SKILL_LEARNING_RESOURCES:
            rec["curated_resource"] = SKILL_LEARNING_RESOURCES[skill_lower]
            rec["learning_path"] = SKILL_LEARNING_RESOURCES[skill_lower]["resource"]
            rec["estimated_time"] = SKILL_LEARNING_RESOURCES[skill_lower]["estimated_time"]
        recommendations["skill_recommendations"].append(rec)

    # Missing preferred skills
    for skill in breakdown.get("preferred_skills", {}).get("missing", []):
        skill_lower = skill.lower()
        rec = {
            "skill": skill,
            "priority": "medium",
            "reason": "Preferred skill in job description",
            "learning_path": "Search for online courses or tutorials",
            "estimated_time": "1-2 weeks",
        }
        if skill_lower in SKILL_LEARNING_RESOURCES:
            rec["curated_resource"] = SKILL_LEARNING_RESOURCES[skill_lower]
        recommendations["skill_recommendations"].append(rec)

    # Missing keywords
    for keyword in breakdown.get("keyword_density", {}).get("top_missing_keywords", []):
        suggestion = {
            "missing_keyword": keyword,
            "existing_equivalent": None,
            "suggestion": f"Try incorporating '{keyword}' into your resume descriptions where your experience supports it",
        }
        keyword_lower = keyword.lower()
        if keyword_lower in KEYWORD_SYNONYMS:
            suggestion["existing_equivalent"] = KEYWORD_SYNONYMS[keyword_lower][0]
            suggestion["suggestion"] = (
                f"You may already have equivalent experience. "
                f"Consider rephrasing to include '{keyword}' — "
                f"similar to: {', '.join(KEYWORD_SYNONYMS[keyword_lower])}"
            )
        recommendations["keyword_suggestions"].append(suggestion)

    score = match_result.get("overall_score", 0)
    if score >= 70:
        recommendations["general_advice"] = "You're in a strong position. Focus on tailoring your resume language to match the JD keywords."
    elif score >= 50:
        recommendations["general_advice"] = "Solid foundation. Closing the skill gaps listed above would significantly improve your match."
    else:
        recommendations["general_advice"] = "Consider upskilling in the high-priority areas before applying, or look at more aligned roles."

    return recommendations
