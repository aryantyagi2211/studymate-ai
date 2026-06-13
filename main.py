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


def run_studymate():
    memory = {}

    print("=" * 60)
    print("        STUDYMATE AI — MULTI AGENT SYSTEM")
    print("=" * 60)

    print("\n[AGENT 1] Motivation Profiler")
    print("-" * 40)
    memory["motivation"] = call_llm(motivation_profiler, task_motivation_profile)
    print(memory["motivation"])

    print("\n[AGENT 2] Diagnostic Agent")
    print("-" * 40)
    memory["diagnostic"] = call_llm(diagnostic_agent, task_diagnostic, memory["motivation"])
    print(memory["diagnostic"])

    print("\n[AGENT 3] Learning Path Agent")
    print("-" * 40)
    memory["learning_path"] = call_llm(learning_path_agent, task_learning_path, memory["diagnostic"])
    print(memory["learning_path"])

    print("\n[AGENT 4] Adaptive Planner")
    print("-" * 40)
    memory["plan"] = call_llm(adaptive_planner, task_adaptive_plan, memory["learning_path"])
    print(memory["plan"])

    print("\n[AGENT 5] Teaching Agent")
    print("-" * 40)
    memory["teaching"] = call_llm(teaching_agent, task_teaching, memory["diagnostic"])
    print(memory["teaching"])

    print("\n[AGENT 6] Assessment Agent")
    print("-" * 40)
    memory["assessment"] = call_llm(assessment_agent, task_assessment, memory["teaching"])
    print(memory["assessment"])

    print("\n[AGENT 7] Engagement Agent")
    print("-" * 40)
    memory["engagement"] = call_llm(engagement_agent, task_engagement, memory["plan"])
    print(memory["engagement"])

    print("\n[AGENT 8] Manager Insights")
    print("-" * 40)
    memory["insights"] = call_llm(
        manager_insights_agent,
        task_manager_insights,
        f"{memory['assessment']}\n{memory['engagement']}"
    )
    print(memory["insights"])

    print("\n" + "=" * 60)
    print("        STUDYMATE AI — SESSION COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    run_studymate()