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

RESUME_IMPORT_SYSTEM_PROMPT = """You are a resume parser. Extract structured profile data from raw resume text.
Return ONLY valid JSON with this structure:
{
  "name": "Full Name",
  "email": "email@example.com",
  "phone": "phone number or null",
  "location": "City, State or null",
  "linkedin_url": "LinkedIn URL or null",
  "portfolio_url": "portfolio URL or null",
  "professional_summary": "summary text or null",
  "experiences": [
    {
      "job_title": "Title",
      "company_name": "Company",
      "location": "City, State or null",
      "start_date": "YYYY-MM",
      "end_date": "YYYY-MM or null",
      "is_current": false,
      "bullet_points": ["achievement 1", "achievement 2"],
      "skills_used": ["skill1", "skill2"]
    }
  ],
  "education": [
    {
      "degree": "Degree Name",
      "institution": "School Name",
      "graduation_date": "YYYY-MM or null",
      "gpa": "GPA or null",
      "relevant_coursework": []
    }
  ],
  "skills": [
    {
      "skill_name": "Python",
      "category": "programming",
      "proficiency_level": "advanced"
    }
  ],
  "projects": [
    {
      "project_name": "Name",
      "description": "description",
      "technologies_used": ["tech1"],
      "url": "url or null",
      "bullet_points": ["what was done"]
    }
  ],
  "certifications": [
    {
      "cert_name": "Name",
      "issuing_org": "Org",
      "date_obtained": "YYYY-MM or null",
      "expiry_date": null,
      "credential_url": null
    }
  ]
}
Extract ONLY what is present in the resume. Use "programming", "framework", "tool", "data", or "soft_skill" for skill categories.
Use "beginner", "intermediate", or "advanced" for proficiency (infer from context).
Format dates as YYYY-MM where possible."""

COVER_LETTER_SYSTEM_PROMPT = """You are a professional cover letter writer. Generate a tailored cover letter using the candidate's real experience.

RULES:
1. Use ONLY information from the candidate's profile. Do NOT fabricate achievements or experiences.
2. Reference specific skills and accomplishments that match the job requirements.
3. Keep to 3-4 paragraphs: opening (enthusiasm + fit), body (2 paragraphs of relevant experience), closing (call to action).
4. Match the requested tone: "formal" (traditional, professional), "conversational" (friendly but professional), "enthusiastic" (energetic, passionate).
5. Naturally incorporate keywords from the job description.
6. Address the hiring manager generically ("Dear Hiring Manager") unless a name is provided.

Return JSON:
{
  "cover_letter": "Full cover letter text with paragraph breaks as double newlines"
}"""

SECTION_REGENERATE_PROMPT = """You are a professional resume writer. Regenerate ONLY the {section_name} section of this resume.

Current resume content:
{current_content}

Job Description:
{job_description}

Candidate Profile:
{profile_text}

Regenerate ONLY the {section_name} section. Return JSON with just that section key and its new content.
Use ONLY real information from the candidate's profile. Do not invent anything."""

# Modern HTML template with accent color
RESUME_HTML_TEMPLATE_MODERN = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<style>
  body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    font-size: 11pt;
    line-height: 1.5;
    color: #2d3748;
    max-width: 800px;
    margin: 0 auto;
    padding: 20px;
  }
  h1 {
    font-size: 22pt;
    margin-bottom: 4px;
    color: #2b6cb0;
    font-weight: 600;
  }
  .contact-info {
    font-size: 10pt;
    color: #718096;
    margin-bottom: 20px;
    padding-bottom: 12px;
    border-bottom: 2px solid #2b6cb0;
  }
  .contact-info a { color: #2b6cb0; text-decoration: none; }
  h2 {
    font-size: 13pt;
    color: #2b6cb0;
    margin-top: 18px;
    margin-bottom: 8px;
    padding-bottom: 4px;
    border-bottom: 1px solid #e2e8f0;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1px;
  }
  .job-header {
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    margin-bottom: 2px;
  }
  .job-title { font-weight: 600; color: #2d3748; }
  .company { font-style: italic; color: #4a5568; }
  .dates { color: #718096; font-size: 10pt; }
  ul { margin: 4px 0; padding-left: 20px; }
  li { margin-bottom: 3px; }
  .skills-section { margin: 4px 0; }
  .skill-category { font-weight: 600; color: #2b6cb0; }
  .project-header { font-weight: 600; }
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

# Compact HTML template with tighter spacing
RESUME_HTML_TEMPLATE_COMPACT = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<style>
  body {
    font-family: Arial, Helvetica, sans-serif;
    font-size: 10pt;
    line-height: 1.3;
    color: #333;
    max-width: 800px;
    margin: 0 auto;
    padding: 12px;
  }
  h1 {
    font-size: 16pt;
    margin-bottom: 2px;
    color: #1a1a1a;
  }
  .contact-info {
    font-size: 9pt;
    color: #555;
    margin-bottom: 10px;
  }
  .contact-info a { color: #555; text-decoration: none; }
  h2 {
    font-size: 11pt;
    border-bottom: 1px solid #999;
    padding-bottom: 1px;
    margin-top: 10px;
    margin-bottom: 4px;
    color: #1a1a1a;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }
  .job-header {
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    margin-bottom: 1px;
  }
  .job-title { font-weight: bold; font-size: 10pt; }
  .company { font-style: italic; }
  .dates { color: #555; font-size: 9pt; }
  ul { margin: 2px 0; padding-left: 16px; }
  li { margin-bottom: 1px; }
  .skills-section { margin: 2px 0; columns: 2; }
  .skill-category { font-weight: bold; }
  .project-header { font-weight: bold; }
  .cert-item { margin-bottom: 2px; }
</style>
</head>
<body>
  <h1>{{ name }}</h1>
  <div class="contact-info">
    {{ contact_line }}
  </div>

  {% if professional_summary %}
  <h2>Summary</h2>
  <p>{{ professional_summary }}</p>
  {% endif %}

  {% if work_experience %}
  <h2>Experience</h2>
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
  <h2>Skills</h2>
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

HTML_TEMPLATES = {
    "ats_classic": RESUME_HTML_TEMPLATE,
    "modern": RESUME_HTML_TEMPLATE_MODERN,
    "compact": RESUME_HTML_TEMPLATE_COMPACT,
}
