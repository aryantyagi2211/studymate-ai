import streamlit as st
from agents import (
    client, ceo_agent, profiler_agent, knowledge_checker,
    learning_path_agent, adaptive_planner, teaching_agent,
    examiner_agent, manager_insights_agent
)
from tasks import (
    task_ceo, task_profiler, task_knowledge_checker,
    task_learning_path, task_adaptive_plan, task_teaching,
    task_examiner, task_manager_insights
)
from data.data import LEARNER_DATA, WORK_SIGNALS, CERT_GUIDE, TEAM

# ── helpers ──────────────────────────────────────────────
def call_llm(agent, task, context=""):
    messages = [{"role": "system", "content":
        f"You are {agent['name']}.\nRole: {agent['role']}\nGoal: {agent['goal']}\nBackstory: {agent['backstory']}"}]
    if context:
        messages.append({"role": "assistant", "content": f"Previous context:\n{context}"})
    messages.append({"role": "user", "content":
        f"{task['description']}\n\nExpected output: {task['expected_output']}"})
    return client.chat.completions.create(
        model="llama-3.3-70b-versatile", messages=messages
    ).choices[0].message.content

def call_llm_custom(agent, user_msg, context=""):
    messages = [{"role": "system", "content":
        f"You are {agent['name']}.\nRole: {agent['role']}\nGoal: {agent['goal']}\nBackstory: {agent['backstory']}"}]
    if context:
        messages.append({"role": "assistant", "content": f"Previous context:\n{context}"})
    messages.append({"role": "user", "content": user_msg})
    return client.chat.completions.create(
        model="llama-3.3-70b-versatile", messages=messages
    ).choices[0].message.content

# ── page config ───────────────────────────────────────────
st.set_page_config(page_title="StudyMate AI", page_icon="🎓", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.main { background: #0a0a0f; }

.hero-title {
    font-size: 3rem; font-weight: 800;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    margin-bottom: 0.2rem;
}
.hero-sub {
    font-size: 1.1rem; color: #8b8fa8; margin-bottom: 2rem;
}
.agent-card {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
    border: 1px solid #2d2d4e;
    border-radius: 16px;
    padding: 1.5rem;
    margin-bottom: 1rem;
    box-shadow: 0 4px 24px rgba(102,126,234,0.08);
}
.agent-header {
    font-size: 1.1rem; font-weight: 700;
    color: #667eea; margin-bottom: 0.8rem;
}
.step-badge {
    background: linear-gradient(135deg, #667eea, #764ba2);
    color: white; border-radius: 20px;
    padding: 2px 12px; font-size: 0.75rem;
    font-weight: 600; display: inline-block;
    margin-bottom: 0.5rem;
}
.progress-bar-container {
    background: #1a1a2e; border-radius: 10px;
    height: 8px; margin: 1rem 0;
}
.progress-bar-fill {
    background: linear-gradient(90deg, #667eea, #f093fb);
    height: 8px; border-radius: 10px;
    transition: width 0.5s ease;
}
.metric-card {
    background: linear-gradient(135deg, #1a1a2e, #16213e);
    border: 1px solid #2d2d4e;
    border-radius: 12px; padding: 1rem;
    text-align: center;
}
.metric-value {
    font-size: 2rem; font-weight: 800;
    background: linear-gradient(135deg, #667eea, #f093fb);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.metric-label { color: #8b8fa8; font-size: 0.85rem; }
.status-risk { color: #ff6b6b; font-weight: 700; }
.status-good { color: #51cf66; font-weight: 700; }
.status-warn { color: #ffd43b; font-weight: 700; }
.sidebar-card {
    background: linear-gradient(135deg, #1a1a2e, #16213e);
    border: 1px solid #2d2d4e;
    border-radius: 12px; padding: 1rem;
    margin-bottom: 0.5rem;
}
.loop-badge {
    background: linear-gradient(135deg, #f093fb, #f5576c);
    color: white; border-radius: 8px;
    padding: 8px 16px; font-weight: 700;
    font-size: 0.9rem; display: inline-block;
    margin-bottom: 1rem;
}
</style>
""", unsafe_allow_html=True)

# ── session state ─────────────────────────────────────────
for k, v in [("step", 0), ("memory", {}), ("answers", {}), ("loop_count", 0)]:
    if k not in st.session_state:
        st.session_state[k] = v

# ── sidebar ───────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🎓 StudyMate AI")
    st.markdown("---")

    learner_id = st.selectbox("👤 Select Learner", ["L-1001", "L-1002", "L-1003"])
    employee_id = st.selectbox("💼 Select Employee", ["EMP-001", "EMP-002", "EMP-003"])

    learner = LEARNER_DATA[learner_id]
    work = WORK_SIGNALS[employee_id]
    cert = CERT_GUIDE[learner["certification"]]

    st.markdown("---")
    st.markdown(f"""
    <div class='sidebar-card'>
        <div style='color:#667eea;font-weight:700;margin-bottom:8px'>👤 {learner['name']}</div>
        <div style='color:#8b8fa8;font-size:0.85rem'>🏢 {learner['role']}</div>
        <div style='color:#8b8fa8;font-size:0.85rem'>📜 {learner['certification']}</div>
        <div style='color:#8b8fa8;font-size:0.85rem'>⏱️ {learner['hours_studied']} hrs studied</div>
        <div style='color:#8b8fa8;font-size:0.85rem'>📊 {learner['practice_score']}% score</div>
    </div>
    """, unsafe_allow_html=True)

    # Progress
    total_steps = 9
    current = min(st.session_state.step, total_steps)
    pct = int((current / total_steps) * 100)
    st.markdown(f"""
    <div style='margin-top:1rem'>
        <div style='color:#8b8fa8;font-size:0.8rem;margin-bottom:4px'>Progress — {pct}%</div>
        <div class='progress-bar-container'>
            <div class='progress-bar-fill' style='width:{pct}%'></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    if st.button("🚀 Start StudyMate AI", use_container_width=True):
        st.session_state.step = 1
        st.session_state.memory = {}
        st.session_state.answers = {}
        st.session_state.loop_count = 0
        st.rerun()

    if st.session_state.loop_count > 0:
        st.markdown(f"""
        <div style='text-align:center;margin-top:1rem'>
            <div class='loop-badge'>🔄 Loop #{st.session_state.loop_count}</div>
        </div>
        """, unsafe_allow_html=True)

# ── hero ──────────────────────────────────────────────────
st.markdown("""
<div class='hero-title'>🎓 StudyMate AI</div>
<div class='hero-sub'>Your Personal AI Learning Team — 8 Intelligent Agents Working Together</div>
""", unsafe_allow_html=True)

# Agent step labels
STEPS = [
    "", "🏢 CEO", "🧠 Profiler", "🔍 Knowledge Check",
    "📚 Learning Path", "📅 Study Plan",
    "👨‍🏫 Teaching", "📝 Exam", "📊 Manager", "🏢 CEO Decision"
]

if st.session_state.step == 0:
    # Landing
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div class='agent-card'>
            <div style='font-size:2rem'>🧠</div>
            <div style='color:#667eea;font-weight:700;margin:8px 0'>8 AI Agents</div>
            <div style='color:#8b8fa8;font-size:0.9rem'>CEO, Profiler, Knowledge Checker, Learning Path, Adaptive Planner, Teacher, Examiner, Manager</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class='agent-card'>
            <div style='font-size:2rem'>🔄</div>
            <div style='color:#667eea;font-weight:700;margin:8px 0'>Adaptive Loop</div>
            <div style='color:#8b8fa8;font-size:0.9rem'>CEO reviews performance and sends student back to Teaching if weak areas found</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class='agent-card'>
            <div style='font-size:2rem'>📊</div>
            <div style='color:#667eea;font-weight:700;margin:8px 0'>Team Insights</div>
            <div style='color:#8b8fa8;font-size:0.9rem'>Manager tracks full team performance and reports to CEO for smart decisions</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    for i, member in enumerate(TEAM):
        col = [col1, col2, col3][i]
        with col:
            status_class = "status-risk" if member["status"] == "At Risk" else \
                          "status-good" if member["status"] == "On Track" else "status-warn"
            st.markdown(f"""
            <div class='metric-card'>
                <div class='metric-value'>{member['practice_score']}%</div>
                <div class='metric-label'>{member['name']}</div>
                <div class='metric-label'>{member['role']}</div>
                <div class='{status_class}'>{member['status']}</div>
            </div>
            """, unsafe_allow_html=True)

# ── STEP 1 — CEO Welcome ──────────────────────────────────
if st.session_state.step >= 1:
    st.markdown(f"<div class='step-badge'>Step 1 of 9</div>", unsafe_allow_html=True)
    st.markdown("<div class='agent-card'>", unsafe_allow_html=True)
    st.markdown("<div class='agent-header'>🏢 CEO Agent — Welcome</div>", unsafe_allow_html=True)
    if "ceo_intro" not in st.session_state.memory:
        with st.spinner("CEO Agent is welcoming you..."):
            st.session_state.memory["ceo_intro"] = call_llm(ceo_agent, task_ceo)
    st.markdown(st.session_state.memory["ceo_intro"])
    if st.session_state.step == 1:
        if st.button("➡️ Meet Your Profiler", key="btn1", type="primary"):
            st.session_state.step = 2
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# ── STEP 2 — Profiler ─────────────────────────────────────
if st.session_state.step >= 2:
    st.markdown("<div class='step-badge'>Step 2 of 9</div>", unsafe_allow_html=True)
    st.markdown("<div class='agent-card'>", unsafe_allow_html=True)
    st.markdown("<div class='agent-header'>🧠 Profiler Agent — Understanding Your Why</div>", unsafe_allow_html=True)
    if "profile" not in st.session_state.memory:
        with st.spinner("Profiling your motivation..."):
            st.session_state.memory["profile"] = call_llm(profiler_agent, task_profiler, st.session_state.memory["ceo_intro"])
    st.markdown(st.session_state.memory["profile"])
    if st.session_state.step == 2:
        motivation = st.radio("**What's your motivation?**",
            ["🏢 Company requires it", "🚀 Career growth or promotion", "💡 Personal interest and curiosity"],
            key="motivation_choice")
        if st.button("➡️ Check My Knowledge", key="btn2", type="primary"):
            st.session_state.answers["motivation"] = motivation
            st.session_state.step = 3
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# ── STEP 3 — Knowledge Checker ────────────────────────────
if st.session_state.step >= 3:
    st.markdown("<div class='step-badge'>Step 3 of 9</div>", unsafe_allow_html=True)
    st.markdown("<div class='agent-card'>", unsafe_allow_html=True)
    st.markdown("<div class='agent-header'>🔍 Knowledge Checker — Baseline Assessment</div>", unsafe_allow_html=True)
    if "knowledge_questions" not in st.session_state.memory:
        with st.spinner("Generating your diagnostic questions..."):
            q_task = {
                "description": f"""Generate exactly 3 MCQ questions for {learner['certification']}.
Skills: {cert['skills']}
Format EXACTLY:
Q1: [question]
A) B) C) D)
ANSWER: [letter]
Do NOT show answers yet.""",
                "expected_output": "3 MCQ questions without answers shown."
            }
            st.session_state.memory["knowledge_questions"] = call_llm(knowledge_checker, q_task)
    st.markdown("**Answer honestly — this helps us build your perfect learning path:**")
    st.markdown(st.session_state.memory["knowledge_questions"])
    if st.session_state.step == 3:
        col1, col2, col3 = st.columns(3)
        with col1: q1 = st.radio("**Q1 Answer:**", ["A", "B", "C", "D"], key="q1")
        with col2: q2 = st.radio("**Q2 Answer:**", ["A", "B", "C", "D"], key="q2")
        with col3: q3 = st.radio("**Q3 Answer:**", ["A", "B", "C", "D"], key="q3")
        if st.button("✅ Submit Answers", key="btn3", type="primary"):
            st.session_state.answers.update({"q1": q1, "q2": q2, "q3": q3})
            with st.spinner("Analyzing your knowledge..."):
                eval_msg = f"""Questions: {st.session_state.memory['knowledge_questions']}
Student answers: Q1={q1}, Q2={q2}, Q3={q3}
1. Show correct answer for each
2. Right or wrong for student
3. Rank each skill: STRONG / MEDIUM / WEAK
4. Give encouraging feedback"""
                st.session_state.memory["knowledge"] = call_llm_custom(knowledge_checker, eval_msg)
            st.markdown("### 📊 Your Results:")
            st.markdown(st.session_state.memory["knowledge"])
            st.session_state.step = 4
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# ── STEP 4 — Learning Path ────────────────────────────────
if st.session_state.step >= 4:
    st.markdown("<div class='step-badge'>Step 4 of 9</div>", unsafe_allow_html=True)
    st.markdown("<div class='agent-card'>", unsafe_allow_html=True)
    st.markdown("<div class='agent-header'>📚 Learning Path Agent — Your Custom Path</div>", unsafe_allow_html=True)
    if "learning_path" not in st.session_state.memory:
        with st.spinner("Building your personalized learning path..."):
            st.session_state.memory["learning_path"] = call_llm(learning_path_agent, task_learning_path, st.session_state.memory["knowledge"])
    st.markdown(st.session_state.memory["learning_path"])
    if st.session_state.step == 4:
        if st.button("➡️ Build My Study Plan", key="btn4", type="primary"):
            st.session_state.step = 5
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# ── STEP 5 — Adaptive Planner ─────────────────────────────
if st.session_state.step >= 5:
    st.markdown("<div class='step-badge'>Step 5 of 9</div>", unsafe_allow_html=True)
    st.markdown("<div class='agent-card'>", unsafe_allow_html=True)
    st.markdown("<div class='agent-header'>📅 Adaptive Planner — Your Schedule</div>", unsafe_allow_html=True)
    if "plan" not in st.session_state.memory:
        with st.spinner("Creating your realistic study schedule..."):
            st.session_state.memory["plan"] = call_llm(adaptive_planner, task_adaptive_plan, st.session_state.memory["learning_path"])
    st.markdown(st.session_state.memory["plan"])
    if st.session_state.step == 5:
        if st.button("➡️ Start Learning", key="btn5", type="primary"):
            st.session_state.step = 6
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# ── STEP 6 — Teaching Agent ───────────────────────────────
if st.session_state.step >= 6:
    st.markdown("<div class='step-badge'>Step 6 of 9</div>", unsafe_allow_html=True)
    st.markdown("<div class='agent-card'>", unsafe_allow_html=True)
    st.markdown("<div class='agent-header'>👨‍🏫 Teaching Agent — Learn Your Weak Areas</div>", unsafe_allow_html=True)
    if "teaching" not in st.session_state.memory:
        with st.spinner("Preparing your personalized lesson..."):
            st.session_state.memory["teaching"] = call_llm(teaching_agent, task_teaching, st.session_state.memory["knowledge"])
    st.markdown(st.session_state.memory["teaching"])
    if st.session_state.step == 6:
        understood = st.radio("**Did that make sense?**",
            ["✅ Yes, I understood!", "🤔 Somewhat", "❌ No, explain differently"], key="understood")
        if st.button("➡️ Continue", key="btn6", type="primary"):
            if "❌" in understood:
                with st.spinner("Finding a better way to explain..."):
                    retry_msg = f"""Student did not understand.
Previous: {st.session_state.memory['teaching']}
Explain the same concept from a completely different angle.
Use a new analogy and different example. Keep it very simple."""
                    st.session_state.memory["teaching"] = call_llm_custom(teaching_agent, retry_msg)
                st.rerun()
            else:
                st.session_state.step = 7
                st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# ── STEP 7 — Examiner ─────────────────────────────────────
if st.session_state.step >= 7:
    st.markdown("<div class='step-badge'>Step 7 of 9</div>", unsafe_allow_html=True)
    st.markdown("<div class='agent-card'>", unsafe_allow_html=True)
    st.markdown("<div class='agent-header'>📝 Examiner Agent — Test Your Knowledge</div>", unsafe_allow_html=True)
    if "exam_questions" not in st.session_state.memory:
        with st.spinner("Preparing your exam..."):
            eq_task = {
                "description": f"""Generate 2 MCQ + 1 Q&A for {learner['certification']}.
Skills: {cert['skills']}
MCQ format: MCQ1: [q] A) B) C) D) ANSWER: [letter]
QA format: QA1: [q] MODEL_ANSWER: [answer]
Do NOT reveal answers yet.""",
                "expected_output": "2 MCQ + 1 Q&A without answers."
            }
            st.session_state.memory["exam_questions"] = call_llm(examiner_agent, eq_task)
    st.markdown("**Answer carefully — your results go to the CEO for review:**")
    st.markdown(st.session_state.memory["exam_questions"])
    if st.session_state.step == 7:
        col1, col2 = st.columns(2)
        with col1: mcq1 = st.radio("**MCQ1:**", ["A", "B", "C", "D"], key="mcq1")
        with col2: mcq2 = st.radio("**MCQ2:**", ["A", "B", "C", "D"], key="mcq2")
        qa1 = st.text_area("**Your Q&A Answer:**", placeholder="Write your answer here...", key="qa1")
        if st.button("✅ Submit Exam", key="btn7", type="primary"):
            with st.spinner("Evaluating your performance..."):
                eval_msg = f"""Questions: {st.session_state.memory['exam_questions']}
MCQ1: {mcq1}, MCQ2: {mcq2}, Q&A: {qa1}
1. Reveal correct answers
2. Score each
3. Overall % score
4. Flag skills below 60%
5. Encouraging feedback"""
                st.session_state.memory["exam"] = call_llm_custom(examiner_agent, eval_msg)
            st.markdown("### 📊 Exam Results:")
            st.markdown(st.session_state.memory["exam"])
            st.session_state.step = 8
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# ── STEP 8 — Manager Insights ─────────────────────────────
if st.session_state.step >= 8:
    st.markdown("<div class='step-badge'>Step 8 of 9</div>", unsafe_allow_html=True)
    st.markdown("<div class='agent-card'>", unsafe_allow_html=True)
    st.markdown("<div class='agent-header'>📊 Manager Insights — Team Performance Report</div>", unsafe_allow_html=True)
    if "insights" not in st.session_state.memory:
        with st.spinner("Generating manager report..."):
            st.session_state.memory["insights"] = call_llm(
                manager_insights_agent, task_manager_insights,
                f"{st.session_state.memory['exam']}\n{st.session_state.memory['plan']}")
    st.markdown(st.session_state.memory["insights"])
    if st.session_state.step == 8:
        if st.button("➡️ CEO Final Decision", key="btn8", type="primary"):
            st.session_state.step = 9
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# ── STEP 9 — CEO Final Decision + Loop ───────────────────
if st.session_state.step >= 9:
    st.markdown("<div class='step-badge'>Step 9 of 9</div>", unsafe_allow_html=True)
    st.markdown("<div class='agent-card'>", unsafe_allow_html=True)
    st.markdown("<div class='agent-header'>🏢 CEO Agent — Final Decision</div>", unsafe_allow_html=True)
    if "ceo_decision" not in st.session_state.memory:
        with st.spinner("CEO reviewing all performance data..."):
            ceo_msg = f"""Manager report: {st.session_state.memory['insights']}
Exam results: {st.session_state.memory['exam']}

Make final decision for this student:
- If score below 70% in any skill: recommend going back to Teaching Agent
- If score 70-85%: recommend more practice
- If score above 85%: congratulate and say ready to move on

Be specific about which skill needs work.
End with a clear recommendation: NEEDS_MORE_TEACHING / NEEDS_MORE_PRACTICE / READY_TO_MOVE_ON"""
            st.session_state.memory["ceo_decision"] = call_llm_custom(
                ceo_agent, ceo_msg, st.session_state.memory["insights"])
    st.markdown(st.session_state.memory["ceo_decision"])

    st.markdown("---")

    # CEO Loop Decision
    decision_text = st.session_state.memory["ceo_decision"].upper()
    if "NEEDS_MORE_TEACHING" in decision_text:
        st.error("⚠️ CEO Decision: Student needs more teaching on weak areas.")
        if st.button("🔄 Go Back to Teaching Agent", key="loop_teach", type="primary"):
            st.session_state.loop_count += 1
            del st.session_state.memory["teaching"]
            del st.session_state.memory["exam_questions"]
            del st.session_state.memory["exam"]
            del st.session_state.memory["insights"]
            del st.session_state.memory["ceo_decision"]
            st.session_state.step = 6
            st.rerun()
    elif "NEEDS_MORE_PRACTICE" in decision_text:
        st.warning("📝 CEO Decision: Student needs more practice.")
        if st.button("🔄 Go Back to Examiner Agent", key="loop_exam", type="primary"):
            st.session_state.loop_count += 1
            del st.session_state.memory["exam_questions"]
            del st.session_state.memory["exam"]
            del st.session_state.memory["insights"]
            del st.session_state.memory["ceo_decision"]
            st.session_state.step = 7
            st.rerun()
    else:
        st.success("🎉 CEO Decision: Student is ready to move on!")
        st.balloons()

    # Team metrics
    st.markdown("### 📊 Team Overview")
    col1, col2, col3 = st.columns(3)
    for i, member in enumerate(TEAM):
        col = [col1, col2, col3][i]
        with col:
            status_class = "status-risk" if member["status"] == "At Risk" else \
                          "status-good" if member["status"] == "On Track" else "status-warn"
            st.markdown(f"""
            <div class='metric-card'>
                <div class='metric-value'>{member['practice_score']}%</div>
                <div style='color:white;font-weight:700'>{member['name']}</div>
                <div class='metric-label'>{member['role']} — {member['certification']}</div>
                <div class='{status_class}'>{member['status']}</div>
                <div class='metric-label'>⏱️ {member['hours_studied']} hrs studied</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)