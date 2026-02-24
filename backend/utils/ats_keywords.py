"""Common ATS keyword lists organized by category."""

# Action verbs favored by ATS systems
ACTION_VERBS = [
    "achieved", "administered", "analyzed", "automated", "built",
    "collaborated", "created", "decreased", "delivered", "designed",
    "developed", "directed", "drove", "engineered", "established",
    "executed", "expanded", "facilitated", "generated", "grew",
    "identified", "implemented", "improved", "increased", "initiated",
    "integrated", "launched", "led", "managed", "mentored",
    "migrated", "modernized", "optimized", "orchestrated", "oversaw",
    "partnered", "pioneered", "planned", "produced", "reduced",
    "refactored", "resolved", "revamped", "scaled", "simplified",
    "spearheaded", "streamlined", "supervised", "trained", "transformed",
]

# Common cross-industry ATS keywords
COMMON_ATS_KEYWORDS = {
    "leadership": [
        "team leadership", "cross-functional", "stakeholder management",
        "strategic planning", "decision-making", "mentoring",
        "project management", "resource allocation",
    ],
    "communication": [
        "stakeholder communication", "presentation", "documentation",
        "technical writing", "client-facing", "cross-functional collaboration",
    ],
    "methodology": [
        "agile", "scrum", "kanban", "waterfall", "lean", "six sigma",
        "continuous improvement", "best practices", "OKRs", "KPIs",
    ],
    "technical_general": [
        "CI/CD", "version control", "code review", "testing",
        "debugging", "performance optimization", "scalability",
        "security", "API design", "microservices", "cloud",
    ],
}

# Standard ATS-friendly section headers
STANDARD_SECTION_HEADERS = [
    "Professional Summary",
    "Work Experience",
    "Education",
    "Technical Skills",
    "Projects",
    "Certifications",
]

# Skills to learning resources mapping
SKILL_LEARNING_RESOURCES = {
    "python": {
        "resource": "Python for Everybody on Coursera (University of Michigan)",
        "url": "https://www.coursera.org/specializations/python",
        "estimated_time": "~4 weeks",
    },
    "javascript": {
        "resource": "freeCodeCamp JavaScript Algorithms and Data Structures",
        "url": "https://www.freecodecamp.org/learn/javascript-algorithms-and-data-structures/",
        "estimated_time": "~3 weeks",
    },
    "typescript": {
        "resource": "TypeScript Handbook (Official Docs)",
        "url": "https://www.typescriptlang.org/docs/handbook/",
        "estimated_time": "~1 week if you know JavaScript",
    },
    "react": {
        "resource": "React Official Tutorial",
        "url": "https://react.dev/learn",
        "estimated_time": "~2 weeks",
    },
    "sql": {
        "resource": "SQLBolt Interactive SQL Tutorials",
        "url": "https://sqlbolt.com/",
        "estimated_time": "~1 week",
    },
    "docker": {
        "resource": "Docker Getting Started Guide",
        "url": "https://docs.docker.com/get-started/",
        "estimated_time": "~1 week",
    },
    "kubernetes": {
        "resource": "Kubernetes Basics on kubernetes.io",
        "url": "https://kubernetes.io/docs/tutorials/kubernetes-basics/",
        "estimated_time": "~2 weeks",
    },
    "k8s": {
        "resource": "Kubernetes Basics on kubernetes.io",
        "url": "https://kubernetes.io/docs/tutorials/kubernetes-basics/",
        "estimated_time": "~2 weeks",
    },
    "aws": {
        "resource": "AWS Cloud Practitioner Essentials (Free on AWS Skill Builder)",
        "url": "https://explore.skillbuilder.aws/learn/course/external/view/elearning/134/aws-cloud-practitioner-essentials",
        "estimated_time": "~2 weeks",
    },
    "terraform": {
        "resource": "HashiCorp Learn Terraform Tutorials",
        "url": "https://developer.hashicorp.com/terraform/tutorials",
        "estimated_time": "~2 weeks",
    },
    "spark": {
        "resource": "Apache Spark with Python on Coursera (Duke University)",
        "url": "https://www.coursera.org/learn/apache-spark-python",
        "estimated_time": "~2 weeks of focused study",
    },
    "airflow": {
        "resource": "Apache Airflow Tutorial (Official Docs)",
        "url": "https://airflow.apache.org/docs/apache-airflow/stable/tutorial/index.html",
        "estimated_time": "~1 week",
    },
    "java": {
        "resource": "Java Programming on Coursera (Duke University)",
        "url": "https://www.coursera.org/specializations/java-programming",
        "estimated_time": "~4 weeks",
    },
    "go": {
        "resource": "A Tour of Go (Official)",
        "url": "https://go.dev/tour/welcome/1",
        "estimated_time": "~2 weeks",
    },
    "rust": {
        "resource": "The Rust Programming Language Book",
        "url": "https://doc.rust-lang.org/book/",
        "estimated_time": "~4 weeks",
    },
    "graphql": {
        "resource": "How to GraphQL - The Fullstack Tutorial",
        "url": "https://www.howtographql.com/",
        "estimated_time": "~1 week",
    },
    "redis": {
        "resource": "Redis University (Free Courses)",
        "url": "https://university.redis.com/",
        "estimated_time": "~1 week",
    },
    "mongodb": {
        "resource": "MongoDB University Free Courses",
        "url": "https://university.mongodb.com/",
        "estimated_time": "~2 weeks",
    },
    "postgresql": {
        "resource": "PostgreSQL Tutorial",
        "url": "https://www.postgresqltutorial.com/",
        "estimated_time": "~1 week",
    },
    "machine learning": {
        "resource": "Machine Learning by Andrew Ng on Coursera",
        "url": "https://www.coursera.org/learn/machine-learning",
        "estimated_time": "~8 weeks",
    },
    "data analysis": {
        "resource": "Google Data Analytics Certificate on Coursera",
        "url": "https://www.coursera.org/professional-certificates/google-data-analytics",
        "estimated_time": "~6 weeks",
    },
    "ci/cd": {
        "resource": "GitHub Actions Documentation",
        "url": "https://docs.github.com/en/actions",
        "estimated_time": "~1 week",
    },
    "node.js": {
        "resource": "The Odin Project - NodeJS Path",
        "url": "https://www.theodinproject.com/paths/full-stack-javascript/courses/nodejs",
        "estimated_time": "~3 weeks",
    },
}

# Common keyword synonyms to detect equivalent experience
KEYWORD_SYNONYMS = {
    "stakeholder management": ["client communication", "client management", "stakeholder engagement", "client relations"],
    "cross-functional": ["cross-team", "interdepartmental", "multi-team", "collaborative"],
    "pipeline": ["workflow", "data pipeline", "ETL", "data flow", "processing pipeline"],
    "agile": ["scrum", "sprint", "kanban", "iterative development"],
    "team leadership": ["team lead", "tech lead", "people management", "team management"],
    "data-driven": ["data-informed", "analytics-driven", "metrics-driven"],
    "cloud": ["cloud computing", "AWS", "Azure", "GCP", "cloud infrastructure"],
    "microservices": ["service-oriented architecture", "SOA", "distributed systems"],
}
