LEARNER_DATA = {
    "L-1001": {
        "name": "Arjun Sharma",
        "role": "Cloud Engineer",
        "certification": "AZ-204",
        "hours_studied": 18,
        "practice_score": 67,
        "daily_hours_available": 1.5,
        "preferred_slot": "Morning",
        "skip_days": ["Sunday"],
        "emergency": "Project deadline next week"
    },
    "L-1002": {
        "name": "Priya Mehta",
        "role": "DevOps Engineer",
        "certification": "AZ-400",
        "hours_studied": 24,
        "practice_score": 82,
        "daily_hours_available": 2,
        "preferred_slot": "Evening",
        "skip_days": ["Saturday", "Sunday"],
        "emergency": "None"
    },
    "L-1003": {
        "name": "Rohan Verma",
        "role": "Data Engineer",
        "certification": "DP-203",
        "hours_studied": 20,
        "practice_score": 74,
        "daily_hours_available": 1,
        "preferred_slot": "Afternoon",
        "skip_days": ["Friday"],
        "emergency": "Family event next weekend"
    },
}

WORK_SIGNALS = {
    "EMP-001": {
        "name": "Arjun Sharma",
        "meeting_hours": 22,
        "focus_hours": 10,
        "preferred_slot": "Morning",
        "energy_level": "Low by evening",
        "best_focus_day": "Tuesday"
    },
    "EMP-002": {
        "name": "Priya Mehta",
        "meeting_hours": 15,
        "focus_hours": 18,
        "preferred_slot": "Evening",
        "energy_level": "High in evening",
        "best_focus_day": "Wednesday"
    },
    "EMP-003": {
        "name": "Rohan Verma",
        "meeting_hours": 18,
        "focus_hours": 12,
        "preferred_slot": "Afternoon",
        "energy_level": "Peak after lunch",
        "best_focus_day": "Thursday"
    },
}

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

TEAM = [
    {
        "id": "L-1001",
        "name": "Arjun Sharma",
        "role": "Cloud Engineer",
        "certification": "AZ-204",
        "hours_studied": 18,
        "practice_score": 67,
        "status": "At Risk",
        "emergency": "Project deadline next week"
    },
    {
        "id": "L-1002",
        "name": "Priya Mehta",
        "role": "DevOps Engineer",
        "certification": "AZ-400",
        "hours_studied": 24,
        "practice_score": 82,
        "status": "On Track",
        "emergency": "None"
    },
    {
        "id": "L-1003",
        "name": "Rohan Verma",
        "role": "Data Engineer",
        "certification": "DP-203",
        "hours_studied": 20,
        "practice_score": 74,
        "status": "Needs Attention",
        "emergency": "Family event next weekend"
    },
]