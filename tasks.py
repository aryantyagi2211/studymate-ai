from data.data import LEARNER_DATA, WORK_SIGNALS, CERT_GUIDE, TEAM

LEARNER = LEARNER_DATA["L-1001"]
WORK = WORK_SIGNALS["EMP-001"]
CERT = CERT_GUIDE[LEARNER["certification"]]

task_ceo = {
    "description": f"""
    A new student has just entered StudyMate AI.

    Student details:
    - Role: {LEARNER['role']}
    - Certification goal: {LEARNER['certification']}
    - Hours studied so far: {LEARNER['hours_studied']}
    - Practice score: {LEARNER['practice_score']}%

    Your job:
    Welcome the student warmly.
    Tell them exactly what is going to happen step by step.
    Make them feel confident that this system will guide them properly.
    Decide the first agent to activate — which is the Profiler Agent.
    """,
    "expected_output": "A warm welcome message and clear overview of what StudyMate AI will do for this student."
}

task_profiler = {
    "description": f"""
    A student wants to earn the {LEARNER['certification']} certification.
    They work as a {LEARNER['role']}.

    Your job:
    Understand why this student wants this certification.
    Present 3 possible motivation types:
    1. Company requires it
    2. Career growth or promotion
    3. Personal interest and curiosity

    For each motivation type explain what learning style works best.
    Then identify which motivation most likely fits this student and set their engagement direction.
    Point them clearly in the right direction before learning begins.
    """,
    "expected_output": "3 motivation types explained with engagement styles, and the most likely motivation identified for this student."
}

task_knowledge_checker = {
    "description": f"""
    Check how much this student already knows before we build their learning plan.

    Student details:
    - Certification: {LEARNER['certification']}
    - Skills required: {CERT['skills']}
    - Self reported practice score: {LEARNER['practice_score']}%

    Your job:
    Generate 5 questions — one per skill area.
    Show the correct answer after each question.
    Then rank every skill clearly as:
    - STRONG — student knows this well, quick revision only
    - MEDIUM — student knows basics but needs reinforcement  
    - WEAK — student needs full focused learning here

    Be honest but never make the student feel bad.
    Gaps are just the starting point.
    """,
    "expected_output": "5 diagnostic questions with answers and a clear skill ranking: STRONG / MEDIUM / WEAK for each skill."
}

task_learning_path = {
    "description": f"""
    Build a focused learning path for this student based on their skill ranking.

    Student details:
    - Role: {LEARNER['role']}
    - Certification: {LEARNER['certification']}
    - Skills needed: {CERT['skills']}
    - Hours already studied: {LEARNER['hours_studied']}
    - Total hours recommended: {CERT['recommended_hours']}

    Your job:
    Skip everything they are already strong at.
    For WEAK skills — find the best free resource and give full focus.
    For MEDIUM skills — give a quick reinforcement resource.
    For STRONG skills — give a 15 minute revision tip only.
    Align all resources properly according to their ranking.
    End with an encouraging note.
    """,
    "expected_output": "A focused learning path with resources aligned to each skill level — full resources for weak, quick tips for strong."
}

task_adaptive_plan = {
    "description": f"""
    Build a realistic study schedule for this student around their real life.

    Student details:
    - Certification: {LEARNER['certification']}
    - Hours still needed: {CERT['recommended_hours'] - LEARNER['hours_studied']}
    - Meeting hours per week: {WORK['meeting_hours']}
    - Focus hours per week: {WORK['focus_hours']}
    - Preferred study slot: {WORK['preferred_slot']}

    Your job:
    First ask about their daily routine, available hours, and any skip days or emergencies coming up.
    Then build a week by week schedule that is honest and achievable.
    Include:
    - Daily study targets
    - Which days can be skipped
    - A 10 minute emergency plan for exhausted days
    Never set them up to fail. Make progress feel possible.
    """,
    "expected_output": "A week-by-week study schedule with daily targets, skip day options, and a 10-minute emergency plan."
}

task_teaching = {
    "description": f"""
    Teach the student the concepts they need to learn.

    Student details:
    - Certification: {LEARNER['certification']}
    - Weak skills to teach: {CERT['skills']}
    - Current practice score: {LEARNER['practice_score']}%

    Your job:
    Take the weakest skill first.
    Teach it in exactly 2 ways:
    1. Clear simple explanation
    2. Real world example from a real job scenario

    After teaching ask: Did that make sense? Yes / No / Somewhat
    If No or Somewhat — teach it again from a completely different angle.
    Only move to the next concept when the student confirms they understood.
    Never skip ahead.
    """,
    "expected_output": "2-way teaching of the weakest concept with a comprehension check before moving forward."
}

task_examiner = {
    "description": f"""
    Test the student on what the Teaching Agent just taught them.

    Student details:
    - Certification: {LEARNER['certification']}
    - Skills taught: {CERT['skills']}
    - Current practice score: {LEARNER['practice_score']}%

    Your job:
    Generate a mix of question types:
    - 2 MCQ questions (4 options each, correct answer, one line explanation)
    - 1 Q&A question (open answer, model answer provided)

    For each question clearly state which skill it tests.
    After all questions show a score summary.
    Flag any skill where performance is below 60 percent — these go back to the Teaching Agent.
    Your full results go to the Manager Insights Agent.
    """,
    "expected_output": "2 MCQ + 1 Q&A question with answers, skill labels, score summary, and flags for weak areas."
}

task_manager_insights = {
    "description": f"""
    Collect all student performance data and prepare a report for the CEO.

    Team data: {TEAM}
    Work signals: {WORK_SIGNALS}

    Your job:
    Write a clear performance report with 3 sections:

    Section 1 — Student Performance:
    How is the student doing overall? Where did they struggle? What did they get right?

    Section 2 — What Needs Attention:
    Which skills are still weak? Is the student tired or overwhelmed?
    Check their condition — flag if they need a break or plan adjustment.

    Section 3 — Recommendation to CEO:
    Should this student go back to Teaching Agent for more learning?
    Or go to Examiner Agent for more practice?
    Or are they ready to move on to the next topic?

    Write clearly so the CEO can make the right decision instantly.
    """,
    "expected_output": "A 3-section performance report with student status, attention areas, and a clear recommendation to the CEO."
}