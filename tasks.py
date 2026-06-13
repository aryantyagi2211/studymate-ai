from data.data import LEARNER, WORK, CERT_GUIDE, TEAM

LEARNER = LEARNER["L-1001"]
WORK = WORK["EMP-001"]
CERT = CERT_GUIDE[LEARNER["certification"]]

task_motivation_profile = {
    "description": f"""
    A student just walked into StudyMate AI for the first time.

    Who they are:
    - Job role: {LEARNER['role']}
    - Certification they want: {LEARNER['certification']}

    Your job:
    Find out WHY they want this certification.
    Present 3 possible motivation types and for each one explain what engagement style works best.
    Be warm, curious, and non-judgmental.
    Make them feel safe to be honest about their real reason.
    """,
    "expected_output": "3 motivation types identified with a recommended engagement style for each."
}

task_diagnostic = {
    "description": f"""
    A student needs a baseline assessment before we build their learning plan.

    About them:
    - Certification: {LEARNER['certification']}
    - Skills to test: {CERT['skills']}
    - Their current self-reported practice score: {LEARNER['practice_score']}%

    Your job:
    Generate 5 targeted questions — one per skill area.
    After each question show the correct answer.
    Then clearly label each skill as STRONG, MEDIUM, or WEAK.
    Be honest about the gaps but never make the student feel bad.
    Gaps are just the starting point.
    """,
    "expected_output": "5 diagnostic questions with answers and skill labels: STRONG / MEDIUM / WEAK."
}

task_learning_path = {
    "description": f"""
    You are helping a real person prepare for one of the most important exams of their career.

    Here is who they are:
    - They work as a {LEARNER['role']}
    - They are aiming to get certified in: {LEARNER['certification']}
    - The skills they need to master: {CERT['skills']}
    - They have already put in {LEARNER['hours_studied']} hours of hard work
    - The total recommended study time is {CERT['recommended_hours']} hours

    Your job:
    Skip anything they are already strong at.
    For every weak skill tell them exactly what to study and where to find it for free.
    Do not overwhelm them. Make every hour they have left count.
    End with a short encouraging note.
    """,
    "expected_output": "A focused learning path with one free resource per weak skill and a motivating note at the end."
}

task_adaptive_plan = {
    "description": f"""
    You are building a study schedule for someone who is genuinely trying their best.

    Their reality:
    - Certification: {LEARNER['certification']}
    - Hours still needed: {CERT['recommended_hours'] - LEARNER['hours_studied']}
    - Every week {WORK['meeting_hours']} hours are eaten up by meetings
    - They only get {WORK['focus_hours']} real focus hours to themselves
    - Their best time to learn is the: {WORK['preferred_slot']}

    Your job:
    Build a realistic week-by-week schedule that respects how busy this person is.
    Also give a 10-minute emergency plan for days when they have absolutely no time.
    Do not set them up to fail. Show them it is possible — one small step at a time.
    """,
    "expected_output": "A week-by-week study plan plus a 10-minute emergency plan for exhausted days."
}

task_teaching = {
    "description": f"""
    A student is struggling with a concept and needs your help right now.

    About them:
    - Certification: {LEARNER['certification']}
    - Weak skills: {CERT['skills']}
    - Practice score: {LEARNER['practice_score']}%

    Your job:
    Take the weakest skill and explain it in 3 completely different ways:
    1. Simple definition — explain it like they are hearing it for the first time
    2. Real world example — show them where this actually happens in a job
    3. Easy analogy — connect it to something they already understand from daily life

    End by asking: Did that make sense? Yes / No / Somewhat
    Never move on until they truly understand.
    """,
    "expected_output": "3-way explanation of the weakest skill ending with a comprehension check."
}

task_assessment = {
    "description": f"""
    You are checking how ready this student is before they walk into their exam.

    About them:
    - Certification: {LEARNER['certification']}
    - Skills to be tested: {CERT['skills']}
    - Current practice score: {LEARNER['practice_score']}%

    Your job:
    Write 3 honest practice questions that feel like the real exam.
    Each question must have 4 options (A, B, C, D).
    After each question tell them:
    - Which skill it tests
    - The correct answer
    - One line explaining why that answer is correct

    If the student scores below 60 percent on any topic flag it clearly for the Teaching Agent.
    Be the kind of examiner who wants them to pass — not to trick them.
    """,
    "expected_output": "3 MCQ questions with options, correct answer, skill tested, explanation, and flags for weak topics."
}

task_engagement = {
    "description": f"""
    You are the person in this student's corner when motivation gets hard.

    Their weekly reality:
    - {WORK['meeting_hours']} hours lost to meetings every week
    - Only {WORK['focus_hours']} hours where they can truly focus
    - They study best in the: {WORK['preferred_slot']}

    Your job:
    Create a reminder strategy that feels human — not robotic.
    Tell them when to study, how to protect that time, and what to do on the days they just do not feel like it.
    Give them a shorter plan for exhausted days.
    Remind them why they started. Keep it warm, real, and practical.
    """,
    "expected_output": "A human reminder schedule with strategies for staying consistent even on the hardest days."
}

task_manager_insights = {
    "description": f"""
    You are giving a manager an honest look at how their team is really doing.

    These are real people working hard to grow:
    {TEAM}

    Their work situation:
    {WORK}

    Your job:
    Give the manager something they can actually use.

    Section 1 — Team Pulse:
    How is the team doing overall? Be honest, not just positive.

    Section 2 — Who needs help right now:
    Name who is falling behind and show empathy for why.

    Section 3 — What the manager should do this week:
    Give 3 clear human actions the manager can take today to make a real difference.

    Write like you genuinely care about this team succeeding.
    """,
    "expected_output": "An honest manager report with team pulse, at-risk learners, and 3 clear actions for this week."
}