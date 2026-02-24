"""Resume section templates and formatting helpers."""

# ATS-compatible resume HTML template
RESUME_HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<style>
  body {
    font-family: Calibri, Arial, Helvetica, sans-serif;
    font-size: 11pt;
    line-height: 1.4;
    color: #333;
    max-width: 800px;
    margin: 0 auto;
    padding: 20px;
  }
  h1 {
    font-size: 18pt;
    margin-bottom: 4px;
    color: #1a1a1a;
  }
  .contact-info {
    font-size: 10pt;
    color: #555;
    margin-bottom: 16px;
  }
  .contact-info a { color: #555; text-decoration: none; }
  h2 {
    font-size: 13pt;
    border-bottom: 1.5px solid #333;
    padding-bottom: 2px;
    margin-top: 16px;
    margin-bottom: 8px;
    color: #1a1a1a;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }
  .job-header {
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    margin-bottom: 2px;
  }
  .job-title { font-weight: bold; }
  .company { font-style: italic; }
  .dates { color: #555; font-size: 10pt; }
  ul { margin: 4px 0; padding-left: 20px; }
  li { margin-bottom: 2px; }
  .skills-section { margin: 4px 0; }
  .skill-category { font-weight: bold; }
  .project-header { font-weight: bold; }
  .cert-item { margin-bottom: 4px; }
</style>
</head>
<body>
  <h1>{{ name }}</h1>
  <div class="contact-info">
    {{ contact_line }}
  </div>

  {% if professional_summary %}
  <h2>Professional Summary</h2>
  <p>{{ professional_summary }}</p>
  {% endif %}

  {% if work_experience %}
  <h2>Work Experience</h2>
  {% for job in work_experience %}
  <div class="job-header">
    <span><span class="job-title">{{ job.title }}</span> | <span class="company">{{ job.company }}</span></span>
    <span class="dates">{{ job.dates }}</span>
  </div>
  <ul>
    {% for bullet in job.bullets %}
    <li>{{ bullet }}</li>
    {% endfor %}
  </ul>
  {% endfor %}
  {% endif %}

  {% if education %}
  <h2>Education</h2>
  {% for edu in education %}
  <div class="job-header">
    <span><strong>{{ edu.degree }}</strong> | {{ edu.institution }}</span>
    <span class="dates">{{ edu.graduation_date }}</span>
  </div>
  {% if edu.gpa %}<p>GPA: {{ edu.gpa }}</p>{% endif %}
  {% endfor %}
  {% endif %}

  {% if skills %}
  <h2>Technical Skills</h2>
  <div class="skills-section">
    {% for category, skill_list in skills.items() %}
    <p><span class="skill-category">{{ category }}:</span> {{ skill_list | join(", ") }}</p>
    {% endfor %}
  </div>
  {% endif %}

  {% if projects %}
  <h2>Projects</h2>
  {% for project in projects %}
  <div>
    <span class="project-header">{{ project.name }}</span>
    {% if project.technologies %} | <em>{{ project.technologies | join(", ") }}</em>{% endif %}
    {% if project.url %} | <a href="{{ project.url }}">{{ project.url }}</a>{% endif %}
  </div>
  <ul>
    {% for bullet in project.bullets %}
    <li>{{ bullet }}</li>
    {% endfor %}
  </ul>
  {% endfor %}
  {% endif %}

  {% if certifications %}
  <h2>Certifications</h2>
  {% for cert in certifications %}
  <div class="cert-item">
    <strong>{{ cert.name }}</strong> — {{ cert.issuing_org }} ({{ cert.date }})
  </div>
  {% endfor %}
  {% endif %}
</body>
</html>
"""

# System prompts for AI operations
JOB_PARSER_SYSTEM_PROMPT = """You are a job description parser. Extract structured information from job descriptions.
Return ONLY valid JSON with the following structure:
{
  "job_title": "string",
  "company_name": "string or null",
  "required_skills": ["list of hard skills explicitly required"],
  "preferred_skills": ["list of nice-to-have skills"],
  "years_experience": "string describing experience requirement or null",
  "education_requirements": "string or null",
  "key_responsibilities": ["list of main responsibilities"],
  "ats_keywords": ["important keywords from the JD, weighted by frequency and position"],
  "seniority_level": "entry|mid|senior|lead"
}
Extract ONLY what is explicitly stated in the job description. Do NOT infer or add information that isn't present."""

RESUME_GENERATOR_SYSTEM_PROMPT = """You are a professional resume writer. You will be given a candidate's complete profile and a job description.

CRITICAL RULES:
1. Use ONLY information from the candidate's profile. Do NOT invent, fabricate, or embellish any experience, skill, project, or accomplishment.
2. Rephrase bullet points to naturally incorporate keywords from the job description, but ONLY when the candidate's actual experience supports it.
3. Reorder sections and bullet points to put the most relevant experience first.
4. Use strong action verbs. Quantify results where the candidate has provided numbers.
5. Format the resume with ATS-compatible structure: standard section headers (Professional Summary, Work Experience, Education, Technical Skills, Projects, Certifications), no tables, no columns, no graphics, no headers/footers.
6. The professional summary should be rewritten to align with the specific role while remaining truthful.
7. Keep to 1-2 pages of content.
8. Use standard bullet characters.
9. Spell out acronyms at least once where appropriate.
10. Include exact keyword matches from the JD — don't just use synonyms.

Return the resume as structured JSON:
{
  "professional_summary": "tailored summary string",
  "work_experience": [
    {
      "title": "Job Title",
      "company": "Company Name",
      "location": "City, State",
      "dates": "Month Year - Month Year",
      "bullets": ["achievement 1", "achievement 2"]
    }
  ],
  "education": [
    {
      "degree": "Degree",
      "institution": "School Name",
      "graduation_date": "Month Year",
      "gpa": "GPA or null"
    }
  ],
  "skills": {
    "Technical": ["skill1", "skill2"],
    "Tools & Frameworks": ["tool1", "tool2"],
    "Soft Skills": ["skill1", "skill2"]
  },
  "projects": [
    {
      "name": "Project Name",
      "technologies": ["tech1", "tech2"],
      "url": "url or null",
      "bullets": ["what you did 1", "what you did 2"]
    }
  ],
  "certifications": [
    {
      "name": "Cert Name",
      "issuing_org": "Org",
      "date": "Date"
    }
  ]
}"""

SCORER_SYSTEM_PROMPT = """You are a resume-to-job-description matching expert. Analyze how well a candidate's profile matches a job description.
Be precise and fair in scoring. Provide specific, actionable feedback.

Return JSON with this structure:
{
  "overall_score": 72,
  "breakdown": {
    "hard_skills": {
      "score": 80,
      "weight": 40,
      "matched": ["Python", "SQL"],
      "missing": ["Spark", "Airflow"]
    },
    "experience": {
      "score": 65,
      "weight": 25,
      "notes": "JD asks for 5 years, candidate has 3"
    },
    "preferred_skills": {
      "score": 60,
      "weight": 15,
      "matched": ["Docker"],
      "missing": ["K8s", "Terraform"]
    },
    "education": {
      "score": 100,
      "weight": 10,
      "notes": "Meets requirement"
    },
    "keyword_density": {
      "score": 55,
      "weight": 10,
      "top_missing_keywords": ["pipeline", "stakeholder", "cross-functional"]
    }
  },
  "verdict": "Brief overall assessment"
}"""

RECOMMENDER_SYSTEM_PROMPT = """You are a career advisor. Based on a candidate's skill gaps for a specific job, provide actionable learning recommendations.
Be specific and practical. Focus on the most impactful skills to learn.

Return JSON:
{
  "skill_recommendations": [
    {
      "skill": "Skill Name",
      "priority": "high|medium|low",
      "reason": "Why this skill matters for the role",
      "learning_path": "Specific suggestion for how to learn it",
      "estimated_time": "Rough time estimate"
    }
  ],
  "keyword_suggestions": [
    {
      "missing_keyword": "stakeholder management",
      "existing_equivalent": "client communication",
      "suggestion": "Rephrase your experience with client communication to include 'stakeholder management' terminology"
    }
  ],
  "general_advice": "Brief overall recommendation"
}"""

SECTOR_EXPLORER_SYSTEM_PROMPT = """You are a career advisor specializing in job market analysis. Analyze a candidate's full profile and suggest:
1. Alternative job titles they should search for
2. Industries where their skills are in demand but they might not have considered
3. Brief explanations for each suggestion

Return JSON:
{
  "alternative_titles": [
    {
      "title": "Job Title",
      "relevance": "Why this title fits their skills",
      "search_tip": "Optional tip for searching this title"
    }
  ],
  "industry_suggestions": [
    {
      "industry": "Industry Name",
      "explanation": "Why their skills are valuable here",
      "example_roles": ["Role 1", "Role 2"]
    }
  ],
  "career_insight": "Brief overall career insight"
}"""
