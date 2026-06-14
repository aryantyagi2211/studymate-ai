from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import asyncio
import json
import os

from agents import (
    ceo_agent, profiler_agent, knowledge_checker,
    learning_path_agent, adaptive_planner, teaching_agent,
    examiner_agent, manager_insights_agent
)
from tasks import (
    task_ceo, task_profiler, task_knowledge_checker,
    task_learning_path, task_adaptive_plan, task_teaching,
    task_examiner, task_manager_insights
)
from data.data import LEARNER_DATA, WORK_SIGNALS, CERT_GUIDE, TEAM

app = Flask(__name__, static_folder='.')
CORS(app)

def run(agent, prompt, session=None):
    return asyncio.run(agent.run(prompt, session))

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/api/learners', methods=['GET'])
def get_learners():
    return jsonify({
        "learners": [
            {"id": k, "name": v["name"], "role": v["role"],
             "certification": v["certification"], "score": v["practice_score"],
             "hours": v["hours_studied"]}
            for k, v in LEARNER_DATA.items()
        ],
        "team": TEAM
    })

@app.route('/api/run/<agent_name>', methods=['POST'])
def run_agent(agent_name):
    data = request.json
    learner_id = data.get("learner_id", "L-1001")
    employee_id = data.get("employee_id", "EMP-001")
    context = data.get("context", "")
    extra = data.get("extra", "")

    learner = LEARNER_DATA[learner_id]
    work = WORK_SIGNALS[employee_id]
    cert = CERT_GUIDE[learner["certification"]]

    agents_map = {
        "ceo": (ceo_agent, task_ceo),
        "profiler": (profiler_agent, task_profiler),
        "knowledge": (knowledge_checker, task_knowledge_checker),
        "learning_path": (learning_path_agent, task_learning_path),
        "planner": (adaptive_planner, task_adaptive_plan),
        "teaching": (teaching_agent, task_teaching),
        "examiner": (examiner_agent, task_examiner),
        "manager": (manager_insights_agent, task_manager_insights),
    }

    if agent_name not in agents_map:
        return jsonify({"error": "Agent not found"}), 404

    agent, task = agents_map[agent_name]
    prompt = task["description"]
    if extra:
        prompt += f"\n\nAdditional context:\n{extra}"

    try:
        result = run(agent, prompt)
        return jsonify({"result": result.text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/ceo_decision', methods=['POST'])
def ceo_decision():
    data = request.json
    learner_id = data.get("learner_id", "L-1001")
    exam_score = data.get("exam_score", 0)
    exam_text = data.get("exam_text", "")
    insights = data.get("insights", "")
    loop = data.get("loop", 0)

    learner = LEARNER_DATA[learner_id]

    prompt = (
        f"Student: {learner['name']} | Cert: {learner['certification']} | Score: {exam_score}% | Loop: {loop}\n"
        f"Exam: {exam_text}\nManager: {insights}\n\n"
        "Below 70% → say exactly 'DECISION: NEEDS_MORE_TEACHING' + list weak topics\n"
        "70-84% → say exactly 'DECISION: NEEDS_MORE_PRACTICE' + skills\n"
        "85%+ → say exactly 'DECISION: READY_TO_MOVE_ON' + congratulate\n"
        "Max 120 words. Human tone."
    )

    try:
        result = run(ceo_agent, prompt)
        text = result.text
        decision = "READY_TO_MOVE_ON"
        if "NEEDS_MORE_TEACHING" in text.upper():
            decision = "NEEDS_MORE_TEACHING"
        elif "NEEDS_MORE_PRACTICE" in text.upper():
            decision = "NEEDS_MORE_PRACTICE"
        return jsonify({"result": text, "decision": decision})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/evaluate_knowledge', methods=['POST'])
def evaluate_knowledge():
    data = request.json
    learner_id = data.get("learner_id", "L-1001")
    score = data.get("score", 0)
    total = data.get("total", 10)
    results = data.get("results", "")

    learner = LEARNER_DATA[learner_id]
    cert = CERT_GUIDE[learner["certification"]]

    prompt = (
        f"Student scored {score}/{total}.\nResults:\n{results}\n"
        f"Skills: {cert['skills']}\n"
        "1. Rank each skill STRONG/MEDIUM/WEAK\n"
        "2. Short encouraging feedback (3 sentences max)\n"
        "3. Human warm tone"
    )

    try:
        result = run(knowledge_checker, prompt)
        return jsonify({"result": result.text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/evaluate_exam', methods=['POST'])
def evaluate_exam():
    data = request.json
    learner_id = data.get("learner_id", "L-1001")
    score = data.get("score", 0)
    total = data.get("total", 10)
    ep = data.get("easy_pct", 0)
    mp = data.get("medium_pct", 0)
    hp = data.get("hard_pct", 0)
    results = data.get("results", "")

    prompt = (
        f"Score: {score}/{total} = {int(score/total*100) if total else 0}% | Easy:{ep}% Med:{mp}% Hard:{hp}%\n"
        f"{results}\nHonest analysis, weak skills flagged. Max 100 words."
    )

    try:
        result = run(examiner_agent, prompt)
        return jsonify({"result": result.text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)