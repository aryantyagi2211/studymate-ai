from data.data import LEARNER_DATA, WORK_SIGNALS, CERT_GUIDE, TEAM

# Which student and employee record this session is for.
LEARNER_ID = "L-1001"
EMPLOYEE_ID = "EMP-001"

LEARNER = LEARNER_DATA[LEARNER_ID]
WORK = WORK_SIGNALS[EMPLOYEE_ID]
CERT = CERT_GUIDE[LEARNER["certification"]]

# Pull just this student's row from TEAM, instead of handing the whole
# team's data to an agent that's only meant to report on one person.
STUDENT_RECORD = next(member for member in TEAM if member["id"] == LEARNER_ID)


task_ceo = {
    "description": f"""
    Welcome {LEARNER['name']} to StudyMate AI.
    
    Student info:
    - Role: {LEARNER['role']}
    - Goal: {LEARNER['certification']}
    - Progress: {LEARNER['hours_studied']} hours, {LEARNER['practice_score']}% score
    
    Give a warm, SHORT welcome (2-3 sentences) explaining the journey:
    profile → assess → learn → test → improve
    """,
    "expected_output": "Short welcome message (under 100 words) explaining the StudyMate AI process"
}


task_profiler = {
    "description": f"""
    {LEARNER['name']} just signed up to prepare for {LEARNER['certification']}.
    They work as a {LEARNER['role']}.

    Before anything else, get to know them as a person — not just a
    certification goal. In your own words, naturally:
    - Ask why they actually want this certification (career growth, a
      manager's push, genuine interest — anything is a fair answer)
    - Ask how they're feeling about starting (excited, nervous, overwhelmed,
      or something else)
    - Ask what worries them most about this certification

    Based on what someone in their role is likely feeling, make a warm guess
    about their motivation and use it to set the tone for what comes next.

    Keep it under 150 words, written like one real message from a person —
    no headings, no bullet points.
    """,
    "expected_output": "A short, warm message (under 150 words) that asks about motivation, feelings, and worries in a natural, human way."
}


task_knowledge_checker = {
    "description": f"""
    Create a comprehensive knowledge assessment for {LEARNER['name']} to understand their current skill level.

    Certification: {LEARNER['certification']}
    Skills required: {CERT['skills']}
    Self-reported practice score: {LEARNER['practice_score']}%

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
    "description": f"""
    {LEARNER['name']} ({LEARNER['role']}) is working toward
    {LEARNER['certification']} ({CERT['full_name']}).

    Skills to focus on: {CERT['skills']}
    Hours remaining before the exam: {CERT['recommended_hours'] - LEARNER['hours_studied']}

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
    "description": f"""
    Build a study schedule for {LEARNER['name']} that fits around their
    actual life — not an idealized one.

    What we know about their routine:
    - Certification: {LEARNER['certification']}
    - Hours still needed: {CERT['recommended_hours'] - LEARNER['hours_studied']}
    - Time available per day: {LEARNER['daily_hours_available']} hours
    - Preferred study time: {LEARNER['preferred_slot']}
    - Days they'd rather not study: {LEARNER['skip_days']}
    - On their mind right now: {LEARNER['emergency']}

    Work signals from their job:
    - Meeting hours per week: {WORK['meeting_hours']}
    - Focus hours per week: {WORK['focus_hours']}
    - Energy levels: {WORK['energy_level']}
    - Best day for deep focus: {WORK['best_focus_day']}

    Using all of this, build a realistic week-by-week schedule with:
    - A daily study target that fits their available time
    - Confirmation of which days are skip days, and why that's okay
    - A 10-minute emergency plan for days when things go sideways

    Make it feel achievable. If what's on their mind right now makes this
    week harder than usual, acknowledge it and adjust the plan accordingly.
    """,
    "expected_output": "A week-by-week study schedule built from the student's real routine and work signals, with daily targets, skip days, and a 10-minute emergency plan."
}


task_teaching = {
    "description": f"""
    Teach {LEARNER['name']} the concept they need most right now.

    Certification: {LEARNER['certification']}
    Skills in scope: {CERT['skills']}
    Current practice score: {LEARNER['practice_score']}%

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
    "description": f"""
    Create a comprehensive exam for {LEARNER['name']} based on what the Teaching Agent just covered.

    Certification: {LEARNER['certification']}
    Skills in scope: {CERT['skills']}
    Current practice score: {LEARNER['practice_score']}%

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
    "description": f"""
    Put together a report on {LEARNER['name']}'s session so the CEO can
    decide what happens next.

    This student's record: {STUDENT_RECORD}
    Their work signals: {WORK}

    Write three short sections:

    1. How did they do? — What went well, where did they struggle?
    2. What needs attention? — Which skills are still weak? Do their work
       signals (energy levels, meeting load, anything flagged as on their
       mind) suggest they need a lighter plan or a break?
    3. Recommendation — Should they go back to the Teaching Agent for more
       explanation, to the Examiner for more practice, or are they ready to
       move on?

    Keep it short enough that the CEO can act on it immediately.
    """,
    "expected_output": "A 3-part report — performance summary, attention areas, and a clear recommendation — based only on this student's data."
}