import streamlit as st
from agents import (
    client,
    orchestrator,
    motivation_profiler,
    diagnostic_agent,
    learning_path_agent,
    adaptive_planner,
    teaching_agent,
    assessment_agent,
    engagement_agent,
    manager_insights_agent
)
from tasks import (
    task_motivation_profile,
    task_diagnostic,
    task_learning_path,
    task_adaptive_plan,
    task_teaching,
    task_assessment,
    task_engagement,
    task_manager_insights
)
from data.data import LEARNER, WORK, CERT_GUIDE, TEAM

def call_llm(agent, task, context=""):
    messages = [
        {
            "role": "system",
            "content": f"""You are {agent['name']}.
Role: {agent['role']}
Goal: {agent['goal']}
Backstory: {agent['backstory']}"""
        }
    ]
    if context:
        messages.append({
            "role": "assistant",
            "content": f"Previous agent context:\n{context}"
        })
    messages.append({
        "role": "user",
        "content": f"{task['description']}\n\nExpected output: {task['expected_output']}"
    })
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages
    )
    return response.choices[0].message.content

# Page config
st.set_page_config(
    page_title="StudyMate AI",
    page_icon="🎓",
    layout="wide"
)

# Header
st.title("🎓 StudyMate AI")
st.markdown("### Your Personal AI Learning Team — Powered by 8 Intelligent Agents")
st.divider()

# Sidebar — Learner Input
with st.sidebar:
    st.header("👤 Learner Profile")
    learner_id = st.selectbox("Select Learner", ["L-1001", "L-1002", "L-1003"])
    employee_id = st.selectbox("Select Employee", ["EMP-001", "EMP-002"])

    learner = LEARNER[learner_id]
    work = WORK[employee_id]
    cert = CERT_GUIDE[learner["certification"]]

    st.divider()
    st.markdown(f"**Role:** {learner['role']}")
    st.markdown(f"**Certification:** {learner['certification']}")
    st.markdown(f"**Hours Studied:** {learner['hours_studied']}")
    st.markdown(f"**Practice Score:** {learner['practice_score']}%")
    st.markdown(f"**Meeting Hours/Week:** {work['meeting_hours']}")
    st.markdown(f"**Focus Hours/Week:** {work['focus_hours']}")
    st.markdown(f"**Preferred Slot:** {work['preferred_slot']}")

    st.divider()
    run_button = st.button("🚀 Run StudyMate AI", use_container_width=True)

# Progress bar display
if run_button:
    memory = {}

    st.markdown("## 🤖 Agent Outputs")

    # Agent 1
    with st.expander("🧠 Agent 1 — Motivation Profiler", expanded=True):
        with st.spinner("Profiling motivation..."):
            memory["motivation"] = call_llm(motivation_profiler, task_motivation_profile)
        st.markdown(memory["motivation"])

    # Agent 2
    with st.expander("🔍 Agent 2 — Diagnostic Agent", expanded=True):
        with st.spinner("Running diagnostic..."):
            memory["diagnostic"] = call_llm(diagnostic_agent, task_diagnostic, memory["motivation"])
        st.markdown(memory["diagnostic"])

    # Agent 3
    with st.expander("📚 Agent 3 — Learning Path Agent", expanded=True):
        with st.spinner("Building learning path..."):
            memory["learning_path"] = call_llm(learning_path_agent, task_learning_path, memory["diagnostic"])
        st.markdown(memory["learning_path"])

    # Agent 4
    with st.expander("📅 Agent 4 — Adaptive Planner", expanded=True):
        with st.spinner("Creating study plan..."):
            memory["plan"] = call_llm(adaptive_planner, task_adaptive_plan, memory["learning_path"])
        st.markdown(memory["plan"])

    # Agent 5
    with st.expander("👨‍🏫 Agent 5 — Teaching Agent", expanded=True):
        with st.spinner("Preparing lesson..."):
            memory["teaching"] = call_llm(teaching_agent, task_teaching, memory["diagnostic"])
        st.markdown(memory["teaching"])

    # Agent 6
    with st.expander("📝 Agent 6 — Assessment Agent", expanded=True):
        with st.spinner("Generating assessment..."):
            memory["assessment"] = call_llm(assessment_agent, task_assessment, memory["teaching"])
        st.markdown(memory["assessment"])

    # Agent 7
    with st.expander("💪 Agent 7 — Engagement Agent", expanded=True):
        with st.spinner("Building engagement strategy..."):
            memory["engagement"] = call_llm(engagement_agent, task_engagement, memory["plan"])
        st.markdown(memory["engagement"])

    # Agent 8
    with st.expander("📊 Agent 8 — Manager Insights", expanded=True):
        with st.spinner("Generating manager report..."):
            memory["insights"] = call_llm(
                manager_insights_agent,
                task_manager_insights,
                f"{memory['assessment']}\n{memory['engagement']}"
            )
        st.markdown(memory["insights"])

    st.divider()
    st.success("✅ StudyMate AI Session Complete!")

    # Score display
    st.markdown("### 📊 Team Overview")
    col1, col2, col3 = st.columns(3)
    for i, member in enumerate(TEAM):
        col = [col1, col2, col3][i]
        with col:
            st.metric(
                label=f"{member['role']}",
                value=f"{member['practice_score']}%",
                delta=f"{member['hours_studied']} hrs studied"
            )