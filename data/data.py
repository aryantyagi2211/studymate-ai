# Demo student data - only essential fields
# Agents will ask for other details during the session
DEMO_STUDENT = {
    "name": "Arjun Sharma",
    "role": "Cloud Engineer",
    "certification": "AZ-204"
}

# Certification guide - fallback data if web search fails
# Will be enhanced with real-time web search when possible
CERT_GUIDE = {
    "AZ-204": {
        "full_name": "Developing Solutions for Microsoft Azure",
        "skills": ["API Development", "Azure Functions", "Azure Storage"],
        "recommended_hours": 20,
        "passing_score": 700,
        "exam_format": "40-60 MCQ questions",
        "difficulty": "Intermediate"
    },
    "AZ-400": {
        "full_name": "Designing and Implementing Microsoft DevOps Solutions",
        "skills": ["CI/CD Pipelines", "GitHub Actions", "Azure Monitoring"],
        "recommended_hours": 25,
        "passing_score": 700,
        "exam_format": "40-60 MCQ questions",
        "difficulty": "Advanced"
    },
    "DP-203": {
        "full_name": "Data Engineering on Microsoft Azure",
        "skills": ["Azure Data Factory", "Azure Synapse Analytics", "Azure Data Lake"],
        "recommended_hours": 22,
        "passing_score": 700,
        "exam_format": "40-60 MCQ questions",
        "difficulty": "Intermediate"
    },
}
