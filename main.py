from agents import (
    client,
    ceo_agent,
    profiler_agent,
    knowledge_checker,
    learning_path_agent,
    adaptive_planner,
    teaching_agent,
    examiner_agent,
    manager_insights_agent
)

from tasks import (
    task_ceo,
    task_profiler,
    task_knowledge_checker,
    task_learning_path,
    task_adaptive_plan,
    task_teaching,
    task_examiner,
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

    print("\n[CEO] Orchestrator — Welcome")
    print("-" * 40)
    memory["ceo_intro"] = call_llm(ceo_agent, task_ceo)
    print(memory["ceo_intro"])

    print("\n[AGENT 1] Profiler Agent")
    print("-" * 40)
    memory["profile"] = call_llm(profiler_agent, task_profiler, memory["ceo_intro"])
    print(memory["profile"])

    print("\n[AGENT 2] Knowledge Checker")
    print("-" * 40)
    memory["knowledge"] = call_llm(knowledge_checker, task_knowledge_checker, memory["profile"])
    print(memory["knowledge"])

    print("\n[AGENT 3] Learning Path Agent")
    print("-" * 40)
    memory["learning_path"] = call_llm(learning_path_agent, task_learning_path, memory["knowledge"])
    print(memory["learning_path"])

    print("\n[AGENT 4] Adaptive Planner")
    print("-" * 40)
    memory["plan"] = call_llm(adaptive_planner, task_adaptive_plan, memory["learning_path"])
    print(memory["plan"])

    print("\n[AGENT 5] Teaching Agent")
    print("-" * 40)
    memory["teaching"] = call_llm(teaching_agent, task_teaching, memory["knowledge"])
    print(memory["teaching"])

    print("\n[AGENT 6] Examiner Agent")
    print("-" * 40)
    memory["exam"] = call_llm(examiner_agent, task_examiner, memory["teaching"])
    print(memory["exam"])

    print("\n[AGENT 7] Manager Insights")
    print("-" * 40)
    memory["insights"] = call_llm(
        manager_insights_agent,
        task_manager_insights,
        f"{memory['exam']}\n{memory['plan']}"
    )
    print(memory["insights"])

    print("\n[CEO] Final Decision")
    print("-" * 40)
    ceo_decision_task = {
        "description": f"""
        Manager Insights has reported back to you.
        Here is the full report:
        {memory['insights']}

        Your job:
        Read the report carefully.
        Make a final decision:
        - If student needs more teaching — say which concept and why
        - If student needs more practice — say which skill and why
        - If student is ready to move on — congratulate them and tell them the next step
        Be clear, warm, and decisive.
        """,
        "expected_output": "A clear CEO decision — more teaching, more practice, or ready to move on — with reasoning."
    }
    memory["ceo_decision"] = call_llm(ceo_agent, ceo_decision_task, memory["insights"])
    print(memory["ceo_decision"])

    print("\n" + "=" * 60)
    print("        STUDYMATE AI — SESSION COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    run_studymate()