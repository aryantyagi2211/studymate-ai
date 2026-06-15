from data.data import DEMO_STUDENT, CERT_GUIDE

# Dynamic student data - set at runtime (custom or demo)
LEARNER = None  # Will be set by main.py
CERT = None     # Will be set after learner chooses certification


def set_learner_data(name, role, certification):
    """Set the current learner data for this session"""
    global LEARNER, CERT
    LEARNER = {
        "name": name,
        "role": role,
        "certification": certification
    }
    # Get cert data from guide or create basic one
    CERT = CERT_GUIDE.get(certification, {
        "full_name": f"{certification} Certification",
        "skills": ["Core Skills", "Advanced Topics", "Best Practices"],
        "recommended_hours": 20,
        "passing_score": 700,
        "exam_format": "Multiple choice questions",
        "difficulty": "Intermediate"
    })


def use_demo_data():
    """Load demo student data"""
    set_learner_data(
        DEMO_STUDENT["name"],
        DEMO_STUDENT["role"],
        DEMO_STUDENT["certification"]
    )


task_ceo = {
    "description": lambda: f"""
    Welcome {LEARNER['name']} to StudyMate AI.
    
    Student info:
    - Role: {LEARNER['role']}
    - Goal: {LEARNER['certification']}
    
    Give a warm, SHORT welcome (2-3 sentences) explaining the journey:
    profile → assess → learn → test → improve
    """,
    "expected_output": "Short welcome message (under 100 words) explaining the StudyMate AI process"
}


task_profiler = {
    "description": lambda: f"""
{LEARNER['name']} just signed up for {LEARNER['certification']}. They work as {LEARNER['role']}.

Get to know them - not just their cert goal. Ask naturally:
- Why do they want this cert? (career, manager said to, genuine interest, whatever)
- How are they feeling? (excited/nervous/overwhelmed/etc)
- What worries them most?

Based on their role, make a warm guess about motivation and set the tone. Keep under 150 words, one message from a real person, no headings or bullets.
    """,
    "expected_output": "A short, warm message (under 150 words) that asks about motivation, feelings, and worries in a natural, human way."
}


task_knowledge_checker = {
    "description": lambda: f"""
    Create a comprehensive knowledge assessment for {LEARNER['name']} to understand their current skill level.

    Certification: {LEARNER['certification']}
    Skills required: {CERT['skills']}

    Create 10 multiple-choice questions (MCQs) covering all required skills:
    - 3-4 questions per major skill area
    - Each question should have 4 options (A, B, C, D)
    - One correct answer per question
    - Questions should range from basic to intermediate difficulty

    CRITICAL: Return ONLY valid JSON in this EXACT format (no markdown, no code fences, no extra text):

    {{
      "questions": [
        {{
          "id": 1,
          "skill": "API Development",
          "question": "What is the primary purpose of API keys?",
          "options": ["Option A text", "Option B text", "Option C text", "Option D text"],
          "correct_answer": "A",
          "explanation": "Brief explanation of why this is correct"
        }}
      ]
    }}

    The system will present these questions one by one to the student.
    """,
    "expected_output": "JSON object with 10 MCQ questions, each with id, skill, question text, 4 options, correct answer (A/B/C/D), and explanation."
}

task_learning_path = {
    "description": lambda: f"""
    {LEARNER['name']} ({LEARNER['role']}) is working toward
    {LEARNER['certification']} ({CERT['full_name']}).

    Skills to focus on: {CERT['skills']}
    Recommended study hours: {CERT['recommended_hours']}

    For each skill that still needs work, point them to:
    - The most relevant official Microsoft Learn module
    - One great video or channel
    - One well-written article or blog post
    - A hands-on exercise, sandbox, or repo to practice with
    - A community (subreddit, Discord, forum) where people discuss this topic
    - A realistic time estimate for that skill alone

    Skip any skill they're already strong in. Keep the whole thing under 250
    words and casual in tone — like a senior dev texting a junior friend a
    list of "here's what actually helped me."
    """,
    "expected_output": "A short, casual resource list (under 250 words) covering each weak skill with concrete resources and time estimates."
}


task_adaptive_plan = {
    "description": lambda: f"""
    Build a study schedule for {LEARNER['name']} that fits around their actual life.

    Certification: {LEARNER['certification']}
    Recommended study hours: {CERT['recommended_hours']}
    
    The Adaptive Planner agent will ask them directly about:
    - How many hours per day they can study
    - What time works best (morning/afternoon/evening)  
    - Any busy days they need to skip

    Build a realistic week-by-week schedule with:
    - A daily study target that fits their available time
    - Confirmation of which days are skip days
    - A 10-minute emergency plan for busy days

    Make it feel achievable and personalized to their actual constraints.
    """,
    "expected_output": "A personalized week-by-week study schedule with daily targets, skip days, and emergency plan."
}


task_teaching = {
    "description": lambda: f"""
    Teach {LEARNER['name']} the concept they need most right now.

    Certification: {LEARNER['certification']}
    Skills in scope: {CERT['skills']}

    Look at the skill ranking from the Knowledge Checker and start with
    whichever skill came out weakest. Teach it in two ways — a simple, clear
    explanation, and a real-world example from an actual job scenario.

    Then ask if it made sense. If the answer is no or "somewhat," teach it
    again from a different angle. Only move on to the next concept once it's
    clear this one has landed.
    """,
    "expected_output": "A two-way teaching of the weakest concept, with a comprehension check before moving on."
}


task_examiner = {
    "description": lambda: f"""
    Create a comprehensive exam for {LEARNER['name']} based on what the Teaching Agent just covered.

    Certification: {LEARNER['certification']}
    Skills in scope: {CERT['skills']}

    Create exactly 15 questions with varying difficulty levels:
    - 5 EASY questions (multiple choice)
    - 5 MEDIUM questions (multiple choice)
    - 5 HARD questions (open-ended Q&A style)

    For MCQ questions:
    - Each has 4 options (A, B, C, D)
    - One correct answer
    - Brief explanation

    For Q&A questions:
    - Open-ended question requiring detailed answer
    - Provide a model answer for comparison
    - Specify key points that should be covered

    CRITICAL: Return ONLY valid JSON in this EXACT format (no markdown, no code fences):

    {{
      "questions": [
        {{
          "id": 1,
          "type": "mcq",
          "difficulty": "easy",
          "skill": "API Development",
          "question": "Question text here?",
          "options": ["Option A", "Option B", "Option C", "Option D"],
          "correct_answer": "B",
          "explanation": "Brief explanation"
        }},
        {{
          "id": 11,
          "type": "qa",
          "difficulty": "hard",
          "skill": "Azure Functions",
          "question": "Explain question text here?",
          "model_answer": "Detailed model answer",
          "key_points": ["Point 1", "Point 2", "Point 3"]
        }}
      ]
    }}

    Label each question with the skill it tests. After scoring, flag any skill where the student scored below 60% for more teaching.
    """,
    "expected_output": "JSON with 15 questions (10 MCQ: 5 easy + 5 medium, 5 Q&A: hard), each labeled with difficulty and skill, with answers and explanations."
}


task_manager_insights = {
    "description": lambda: f"""
    Put together a report on {LEARNER['name']}'s session so the CEO can decide what happens next.

    Student: {LEARNER['name']} ({LEARNER['role']})
    Certification: {LEARNER['certification']}

    Write three short sections:
    1. How did they do? — What went well, where did they struggle?
    2. What needs attention? — Which skills are still weak?
    3. Recommendation — Should they go back to Teaching for more explanation, Examiner for more practice, or are they ready to move on?

    Keep it short enough that the CEO can act on it immediately.
    """,
    "expected_output": "A 3-part report — performance summary, attention areas, and a clear recommendation."
}
