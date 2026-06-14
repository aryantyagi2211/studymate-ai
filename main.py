"""
main.py — StudyMate AI session runner (Microsoft Agent Framework)

Requirements:
    pip install agent-framework --pre
    pip install agent-framework-openai --pre
    pip install python-dotenv

This version actually talks to the student:
- The Profiler Agent has a real back-and-forth conversation.
- The Teaching Agent checks for understanding and re-teaches if needed.
- The Examiner Agent asks one question at a time and grades real answers.
"""

import asyncio
import json

from agents import (
    ceo_agent,
    profiler_agent,
    knowledge_checker,
    learning_path_agent,
    adaptive_planner,
    teaching_agent,
    examiner_agent,
    manager_insights_agent,
)

from tasks import (
    task_ceo,
    task_profiler,
    task_knowledge_checker,
    task_learning_path,
    task_adaptive_plan,
    task_teaching,
    task_examiner,
    task_manager_insights,
    LEARNER,
    CERT,
)


def build_prompt(task, context=""):
    """Turn a task dict into the message we send to an agent, optionally
    including a short summary of what's happened earlier in the session."""
    prompt = task["description"]
    if context:
        prompt = (
            f"Here's what's happened so far in this session:\n{context}\n\n"
            f"---\n\n{prompt}"
        )
    prompt += f"\n\nExpected output: {task['expected_output']}"
    return prompt


async def run_step(agent, prompt, session=None):
    """Send one message to an agent and return its reply as plain text."""
    response = await agent.run(prompt, session=session)
    # Get the text content from the response
    if hasattr(response, 'text'):
        return response.text
    elif hasattr(response, 'content'):
        return str(response.content)
    else:
        return str(response)


def print_header(title):
    print("\n" + "-" * 50)
    print(title)
    print("-" * 50)


# ---------------------------------------------------------------------------
# Exam flow — the Examiner Agent returns the exam as JSON, so we can walk the
# student through it one question at a time and grade real answers.
# ---------------------------------------------------------------------------

EXAM_FORMAT_INSTRUCTIONS = """
For this exam, ignore the "Expected output" format described above. Instead,
return ONLY valid JSON, with no markdown formatting, no code fences, and no
extra commentary. Use exactly this structure:

{
  "questions": [
    {
      "type": "mcq",
      "skill": "<skill this question tests>",
      "question": "<question text>",
      "options": ["<option A>", "<option B>", "<option C>", "<option D>"],
      "correct_answer": "<exact text of the correct option>",
      "explanation": "<one line explanation>"
    },
    {
      "type": "mcq",
      "skill": "<skill this question tests>",
      "question": "<question text>",
      "options": ["<option A>", "<option B>", "<option C>", "<option D>"],
      "correct_answer": "<exact text of the correct option>",
      "explanation": "<one line explanation>"
    },
    {
      "type": "open",
      "skill": "<skill this question tests>",
      "question": "<question text>",
      "model_answer": "<model answer>"
    }
  ]
}
"""


def parse_mcq_json(raw_text):
    """Try to extract MCQ questions from the agent's reply."""
    cleaned = raw_text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        if cleaned.lower().startswith("json"):
            cleaned = cleaned[4:]
        cleaned = cleaned.strip()
    try:
        data = json.loads(cleaned)
        return data.get("questions", [])
    except (json.JSONDecodeError, AttributeError) as e:
        print(f"Warning: Could not parse JSON: {e}")
        return []


async def run_knowledge_assessment():
    """Run the interactive knowledge checker with 10 MCQs presented one by one."""
    
    print_header("[Knowledge Checker] Quick diagnostic")
    
    # Get 10 MCQs from Knowledge Checker
    assessment_prompt = build_prompt(task_knowledge_checker)
    raw = await run_step(knowledge_checker, assessment_prompt)
    
    questions = parse_mcq_json(raw)
    
    if not questions or len(questions) < 5:
        print("⚠️  Couldn't generate proper assessment questions. Here's the raw response:\n")
        print(raw)
        return {"total": 0, "correct": 0, "percentage": 0, "skill_scores": {}}
    
    print(f"📋 Assessment ready! {len(questions)} questions to test your knowledge.\n")
    print("Instructions: Answer each question by typing A, B, C, or D\n")
    
    results = []
    correct_count = 0
    
    for q in questions:
        print("-" * 60)
        print(f"\n📝 Question {q.get('id', '?')} — {q.get('skill', 'General')}\n")
        print(q.get('question', ''))
        print()
        
        options = q.get('options', [])
        for idx, option in enumerate(options):
            print(f"  {chr(65 + idx)}. {option}")
        
        # Get user answer
        while True:
            answer = input("\n👉 Your answer (A/B/C/D): ").strip().upper()
            if answer in ['A', 'B', 'C', 'D']:
                break
            print("❌ Please enter A, B, C, or D")
        
        correct_answer = q.get('correct_answer', '').strip().upper()
        is_correct = (answer == correct_answer)
        
        if is_correct:
            correct_count += 1
            print("✅ Correct!")
        else:
            print(f"❌ Incorrect. The correct answer is: {correct_answer}")
        
        print(f"💡 {q.get('explanation', '')}")
        
        results.append({
            "id": q.get('id'),
            "skill": q.get('skill', 'General'),
            "correct": is_correct
        })
        
        print()
    
    # Calculate scores
    total = len(results)
    percentage = int((correct_count / total) * 100) if total > 0 else 0
    
    # Calculate skill-wise scores
    skill_scores = {}
    for r in results:
        skill = r['skill']
        if skill not in skill_scores:
            skill_scores[skill] = {'correct': 0, 'total': 0}
        skill_scores[skill]['total'] += 1
        if r['correct']:
            skill_scores[skill]['correct'] += 1
    
    # Generate summary
    print("\n" + "=" * 60)
    print("📊 ASSESSMENT RESULTS")
    print("=" * 60)
    print(f"\n🎯 Overall Score: {correct_count}/{total} ({percentage}%)\n")
    
    print("📈 Skill Breakdown:")
    assessment_summary = []
    for skill, scores in skill_scores.items():
        skill_pct = int((scores['correct'] / scores['total']) * 100)
        
        if skill_pct >= 80:
            level = "STRONG ✅"
            recommendation = "You're doing great! Just a quick refresher needed."
        elif skill_pct >= 60:
            level = "MEDIUM ⚠️"
            recommendation = "You understand the basics but need more practice."
        else:
            level = "WEAK ❌"
            recommendation = "This needs focused teaching from the ground up."
        
        print(f"\n  • {skill}: {scores['correct']}/{scores['total']} ({skill_pct}%) — {level}")
        print(f"    {recommendation}")
        
        assessment_summary.append(f"{skill}: {skill_pct}% ({level})")
    
    print("\n" + "=" * 60)
    
    return {
        "total": total,
        "correct": correct_count,
        "percentage": percentage,
        "skill_scores": skill_scores,
        "summary": "\n".join(assessment_summary)
    }


def parse_exam_json(raw_text):
    """Try to pull a list of questions out of the agent's reply."""
    cleaned = raw_text.strip()
    
    # Remove markdown code fences
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        if cleaned.lower().startswith("json"):
            cleaned = cleaned[4:]
        cleaned = cleaned.strip()
    
    # Find the first valid JSON object
    import re
    json_matches = re.findall(r'\{[\s\S]*?"questions"[\s\S]*?\}', cleaned)
    
    if json_matches:
        # Use the first match only
        cleaned = json_matches[0]
    
    try:
        data = json.loads(cleaned)
        questions = data.get("questions", [])
        
        # Ensure we have valid questions with required fields
        valid_questions = []
        for q in questions:
            if "question" in q and ("options" in q or "type" in q):
                valid_questions.append(q)
        
        return valid_questions
    except (json.JSONDecodeError, AttributeError) as e:
        print(f"⚠️  JSON Parse Error: {e}")
        return []


def to_option_text(value, options):
    """Let the student answer with A/B/C/D, and let correct_answer be either
    a letter or the option text — normalize both to the option text."""
    letters = {chr(65 + i): option for i, option in enumerate(options)}
    key = value.strip().upper()
    return letters.get(key, value)


async def run_exam_interactive():
    """Run interactive exam with 15 questions asked one by one (like knowledge checker)."""
    
    print_header("[Examiner Agent] Final Exam - 15 Questions")
    print("📝 Mix of multiple-choice and open-ended questions.")
    print("Difficulty levels: 🟢 Easy (1-5), 🟡 Medium (6-10), 🔴 Hard (11-15)\n")
    
    examiner_session = examiner_agent.create_session()
    
    # Initial prompt to start the exam
    start_prompt = f"""Start the certification exam for {LEARNER['name']}.
    
Skills to test: {', '.join(CERT['skills'])}

Begin by asking Question 1 (EASY MCQ). Remember to:
- Show difficulty level
- Provide 4 options (A/B/C/D)
- Ask ONE question at a time"""
    
    reply = await run_step(examiner_agent, start_prompt, session=examiner_session)
    print(reply)
    
    # Track results
    results = {
        'total': 15,
        'correct': 0,
        'mcq_correct': 0,
        'mcq_total': 10,
        'answers': []
    }
    
    # Interactive Q&A for 15 questions
    for question_num in range(1, 16):
        # Get student answer
        if question_num <= 10:
            # MCQ questions
            while True:
                answer = input("\n👉 Your answer (A/B/C/D): ").strip().upper()
                if answer in ['A', 'B', 'C', 'D']:
                    break
                print("❌ Please enter A, B, C, or D")
        else:
            # Open-ended questions
            answer = input("\n✍️  Your detailed answer:\n> ").strip()
        
        # Send answer to examiner
        reply = await run_step(examiner_agent, answer, session=examiner_session)
        print("\n" + reply)
        
        # Track if correct (look for ✅ or "correct" in response)
        if question_num <= 10 and ("✅" in reply or "correct" in reply.lower()):
            results['mcq_correct'] += 1
            results['correct'] += 1
        
        results['answers'].append({
            'question_num': question_num,
            'answer': answer,
            'feedback': reply
        })
        
        print("\n" + "-" * 70)
        
        # Check if this is the last question
        if question_num >= 15:
            break
    
    # Get final summary from examiner
    summary_prompt = """Provide the final exam summary:
- MCQ Score: X/10
- Open-ended Q&A: Brief assessment
- Overall Performance
- Skills that need more work"""
    
    final_summary = await run_step(examiner_agent, summary_prompt, session=examiner_session)
    
    print("\n" + "=" * 70)
    print("📊 FINAL EXAM RESULTS")
    print("=" * 70)
    print(final_summary)
    print("=" * 70)
    
    return final_summary


async def run_exam_old(context):
    """OLD VERSION: Build the exam with 15 questions from JSON (kept as backup)"""
    exam_prompt = build_prompt(task_examiner, context) + "\n\n" + EXAM_FORMAT_INSTRUCTIONS

    raw = await run_step(examiner_agent, exam_prompt)
    questions = parse_exam_json(raw)

    if not questions or len(questions) < 10:
        print("⚠️  Couldn't build a proper exam this time — here's the raw result:\n")
        print(raw)
        return raw

    print(f"📝 Exam ready! {len(questions)} questions to test your knowledge.")
    print("Mix of multiple-choice and open-ended questions.\n")

    results = []
    mcq_correct = 0
    mcq_total = 0
    
    for i, q in enumerate(questions, start=1):
        difficulty_emoji = {"easy": "🟢", "medium": "🟡", "hard": "🔴"}.get(q.get('difficulty', 'medium').lower(), "⚪")
        
        print("\n" + "=" * 70)
        print(f"\nQuestion {i}/{len(questions)} {difficulty_emoji} [{q.get('difficulty', 'medium').upper()}] — {q.get('skill', 'General')}")
        print("-" * 70)
        print(q.get("question", ""))

        if q.get("type") == "mcq":
            options = q.get("options", [])
            print()
            for idx, option in enumerate(options):
                print(f"  {chr(65 + idx)}. {option}")

            while True:
                answer = input("\n👉 Your answer (A/B/C/D): ").strip().upper()
                if answer in ['A', 'B', 'C', 'D']:
                    break
                print("❌ Please enter A, B, C, or D")
            
            chosen = answer
            correct_answer = q.get("correct_answer", "").strip().upper()
            is_correct = (chosen == correct_answer)
            
            mcq_total += 1
            if is_correct:
                mcq_correct += 1
                print("✅ Correct!")
            else:
                print(f"❌ Incorrect — the correct answer was: {correct_answer}")
            
            if q.get("explanation"):
                print(f"💡 {q['explanation']}")

            results.append({
                "skill": q.get("skill", "General"),
                "type": "mcq",
                "difficulty": q.get("difficulty", "medium"),
                "correct": is_correct,
            })
            
        else:  # Q&A type
            print("\n💭 This is an open-ended question. Provide a detailed answer.\n")
            answer = input("✍️  Your answer:\n> ").strip()
            
            results.append({
                "skill": q.get("skill", "General"),
                "type": "qa",
                "difficulty": q.get("difficulty", "hard"),
                "question": q.get("question", ""),
                "model_answer": q.get("model_answer", ""),
                "key_points": q.get("key_points", []),
                "student_answer": answer,
            })

    # Grade Q&A answers using the Examiner agent with improved accuracy measurement
    open_results = [r for r in results if r["type"] == "qa"]
    grading_notes = ""
    qa_scores = []
    
    if open_results:
        print("\n" + "=" * 70)
        print("🤖 Examiner is grading your open-ended answers...")
        print("=" * 70)
        
        grading_prompt = """Grade each student answer based on the model answer and key points. For each question:

1. Compare the student's answer to the model answer
2. Check if key points are covered
3. Assign a score from 0-100%
4. Provide brief feedback

Return your grading in this format for each question:

Question [number]:
Score: [0-100]%
Accuracy: [Excellent/Good/Fair/Poor]
Feedback: [Brief explanation of what was good and what was missing]

---

"""
        
        for idx, r in enumerate(open_results, 1):
            grading_prompt += f"""
Question {idx}: {r['question']}

Model Answer: {r['model_answer']}

Key Points to Cover: {', '.join(r['key_points'])}

Student Answer: {r['student_answer']}

---
"""
        
        grading_notes = await run_step(examiner_agent, grading_prompt)
        
        # Parse scores from grading notes
        import re
        score_matches = re.findall(r'Score:\s*(\d+)', grading_notes)
        for score_str in score_matches:
            qa_scores.append(int(score_str))
        
        print("\n" + grading_notes)

    # Calculate overall scores
    print("\n" + "=" * 70)
    print("📊 EXAM RESULTS")
    print("=" * 70)
    
    # MCQ scores
    mcq_percentage = int((mcq_correct / mcq_total) * 100) if mcq_total > 0 else 0
    print(f"\n📝 Multiple Choice: {mcq_correct}/{mcq_total} ({mcq_percentage}%)")
    
    # Q&A scores
    if qa_scores:
        avg_qa_score = sum(qa_scores) / len(qa_scores)
        print(f"💭 Open-Ended Q&A: {avg_qa_score:.0f}% average accuracy")
    else:
        avg_qa_score = 0
    
    # Overall score
    if mcq_total > 0 and qa_scores:
        overall_score = (mcq_percentage * 0.6) + (avg_qa_score * 0.4)  # 60% MCQ, 40% Q&A
    elif mcq_total > 0:
        overall_score = mcq_percentage
    else:
        overall_score = avg_qa_score
    
    print(f"\n🎯 Overall Score: {overall_score:.0f}%")
    
    # Difficulty breakdown
    print("\n📈 Performance by Difficulty:")
    for difficulty in ["easy", "medium", "hard"]:
        diff_results = [r for r in results if r.get("difficulty") == difficulty and r["type"] == "mcq"]
        if diff_results:
            diff_correct = sum(1 for r in diff_results if r["correct"])
            diff_total = len(diff_results)
            diff_pct = int((diff_correct / diff_total) * 100)
            emoji = {"easy": "🟢", "medium": "🟡", "hard": "🔴"}[difficulty]
            print(f"  {emoji} {difficulty.upper()}: {diff_correct}/{diff_total} ({diff_pct}%)")
    
    # Skill-wise scores
    skill_scores = {}
    for r in results:
        if r["type"] == "mcq":
            skill_scores.setdefault(r["skill"], []).append(r["correct"])

    print("\n📚 Performance by Skill:")
    summary_lines = []
    for skill, outcomes in skill_scores.items():
        pct = (sum(outcomes) / len(outcomes)) * 100
        flag = " — ⚠️  flagged for more teaching" if pct < 60 else ""
        print(f"  • {skill}: {pct:.0f}%{flag}")
        summary_lines.append(f"{skill}: {pct:.0f}%{flag}")

    if grading_notes:
        summary_lines.append(f"\nOpen-ended Q&A feedback:\n{grading_notes}")
    
    print("\n" + "=" * 70)

    return "\n".join(summary_lines)


# ---------------------------------------------------------------------------
# Main session
# ---------------------------------------------------------------------------

async def run_studymate():
    memory = {}

    print("=" * 60)
    print("        STUDYMATE AI — MULTI AGENT SYSTEM")
    print("=" * 60)

    # ---------- CEO: Welcome ----------
    print_header("[CEO] Welcome")
    ceo_session = ceo_agent.create_session()
    memory["ceo_intro"] = await run_step(ceo_agent, build_prompt(task_ceo), session=ceo_session)
    print(memory["ceo_intro"])

    # ---------- Profiler Agent: a real conversation ----------
    print_header(f"[Profiler Agent] Getting to know {LEARNER['name']}")
    profiler_session = profiler_agent.create_session()
    reply = await run_step(profiler_agent, build_prompt(task_profiler), session=profiler_session)
    print(reply)
    print("\n(Reply below to keep chatting — type 'done' when you're ready to move on.)")

    for _ in range(4):
        student_reply = input("\nYou: ").strip()
        if not student_reply or student_reply.lower() in ("done", "skip", "next"):
            break
        reply = await run_step(profiler_agent, student_reply, session=profiler_session)
        print("\n" + reply)

    memory["profile"] = await run_step(
        profiler_agent,
        "In 2-3 sentences, summarize this student's motivation, mindset, and "
        "what direction we should set for their learning journey. This is for "
        "the next agent, not the student — no greetings, just the summary.",
        session=profiler_session,
    )

    # ---------- Knowledge Checker ----------
    assessment_results = await run_knowledge_assessment()
    memory["knowledge"] = assessment_results["summary"]

    # ---------- Learning Path Agent ----------
    print_header("[Learning Path Agent] Resources for you")
    memory["learning_path"] = await run_step(
        learning_path_agent, build_prompt(task_learning_path, memory["knowledge"])
    )
    print(memory["learning_path"])
    
    # Ask user to continue
    print("\n" + "=" * 60)
    continue_input = input("\n➡️  Continue to Adaptive Planner? (yes/no): ").strip().lower()
    if continue_input not in ['yes', 'y']:
        print("\n⏸️  Session paused. Run again to continue from here.")
        return

    # ---------- Adaptive Planner ----------
    print_header("[Adaptive Planner] Your study schedule")
    planner_session = adaptive_planner.create_session()
    
    # Agent asks first question
    reply = await run_step(adaptive_planner, build_prompt(task_adaptive_plan, memory["learning_path"]), session=planner_session)
    print(reply)
    
    # Interactive Q&A - agent will ask 3 questions one by one
    questions_answered = 0
    max_questions = 5  # Allow up to 5 exchanges
    
    for _ in range(max_questions):
        student_reply = input("\n> ").strip()
        if not student_reply:
            print("⚠️  Please provide an answer.")
            continue
            
        reply = await run_step(adaptive_planner, student_reply, session=planner_session)
        print("\n" + reply)
        
        questions_answered += 1
        
        # Check if schedule is ready (contains time/hours/days keywords)
        if any(word in reply.lower() for word in ["schedule", "daily study time", "best time:", "skip days:"]):
            break
        
        if questions_answered >= 3:
            # Force schedule creation
            final_prompt = "Based on my answers, please create my 1-week study schedule now."
            reply = await run_step(adaptive_planner, final_prompt, session=planner_session)
            print("\n" + reply)
            break
    
    memory["plan"] = reply

    # ========== ADAPTIVE LEARNING LOOP ==========
    # Keep teaching and testing until student passes (score >= 80%)
    max_iterations = 5  # Prevent infinite loops
    iteration = 0
    passing_score = 80  # Student needs 80% to pass
    
    weak_skills = []  # Track which skills need work
    
    while iteration < max_iterations:
        iteration += 1
        
        print("\n" + "=" * 60)
        print(f"📚 LEARNING CYCLE {iteration}")
        print("=" * 60)
        
        # ---------- Teaching Agent: comprehension-check loop ----------
        print_header(f"[Teaching Agent] Teaching Session #{iteration}")
        teaching_session = teaching_agent.create_session()
        
        # Focus on weak skills if this is a retry
        if weak_skills:
            focus_prompt = f"The student struggled with these skills: {', '.join(weak_skills)}. Focus your teaching on these areas specifically. Teach the concepts they're missing."
        else:
            focus_prompt = memory["knowledge"]
        
        reply = await run_step(
            teaching_agent, build_prompt(task_teaching, focus_prompt), session=teaching_session
        )
        print(reply)

        for attempt in range(3):
            understanding = input("\nDid that make sense? (yes / no / somewhat): ").strip().lower()
            if understanding.startswith("y"):
                break
            reply = await run_step(
                teaching_agent,
                f"The student said '{understanding}' — that didn't fully land. "
                f"Teach the same concept again from a different angle: a new "
                f"example, a different analogy, or a simpler breakdown.",
                session=teaching_session,
            )
            print("\n" + reply)
        else:
            print("\n(Let's keep this in mind and come back to it after the test.)")

        memory["teaching"] = reply

        # ---------- Examiner Agent: Interactive exam ----------
        memory["exam"] = await run_exam_interactive()

        # ---------- Manager Insights: Analyze performance ----------
        print_header("[Manager Insights] Performance Analysis")
        memory["insights"] = await run_step(
            manager_insights_agent,
            build_prompt(task_manager_insights, f"{memory['exam']}\n\nIteration: {iteration}"),
        )
        print(memory["insights"])
        
        # ---------- CEO Decision: Continue or advance? ----------
        print_header(f"[CEO] Decision - Cycle {iteration}")
        
        # Parse exam score from insights (look for percentage)
        import re
        score_match = re.search(r'(\d+)%', memory["insights"])
        current_score = int(score_match.group(1)) if score_match else 0
        
        # Extract weak skills from insights
        weak_skills = []
        if "weak" in memory["insights"].lower() or "struggle" in memory["insights"].lower():
            # Parse skill names from insights
            from tasks import CERT
            for skill in CERT['skills']:
                if skill.lower() in memory["insights"].lower():
                    weak_skills.append(skill)
        
        decision_prompt = f"""Iteration {iteration} complete. 
        
Student score: {current_score}%
Weak skills: {', '.join(weak_skills) if weak_skills else 'None identified'}

Manager Insights:
{memory['insights']}

Make your decision:
- If score >= 80% and no major weak areas: CONGRATULATE and say they're ready to advance
- If score < 80% or weak skills exist: Say we'll do another teaching cycle on [specific skills]

Keep response SHORT (2-3 sentences)."""
        
        ceo_decision = await run_step(ceo_agent, decision_prompt, session=ceo_session)
        print(ceo_decision)
        
        # Check if student passed
        if current_score >= passing_score and not weak_skills:
            print("\n" + "=" * 60)
            print("✅ STUDENT PASSED! Moving to final decision...")
            print("=" * 60)
            break
        else:
            print("\n" + "=" * 60)
            print(f"📖 Score: {current_score}% - Below passing score ({passing_score}%)")
            if weak_skills:
                print(f"🎯 Will focus on: {', '.join(weak_skills)}")
            print(f"🔄 Starting Learning Cycle {iteration + 1}...")
            print("=" * 60)
            await asyncio.sleep(2)  # Brief pause before next cycle
    
    # ---------- Final CEO Decision ----------
    print_header("[CEO] Final Decision")
    final_decision_prompt = f"""Final session complete after {iteration} learning cycle(s).

Student's journey:
- Final score: {current_score}%
- Cycles completed: {iteration}
- Status: {'PASSED' if current_score >= passing_score else 'NEEDS MORE TIME'}

Provide your final decision and next steps for {LEARNER['name']}.
Keep it SHORT and encouraging (2-3 sentences)."""
    
    memory["ceo_decision"] = await run_step(ceo_agent, final_decision_prompt, session=ceo_session)
    print(memory["ceo_decision"])

    print("\n" + "=" * 60)
    print("        STUDYMATE AI — SESSION COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(run_studymate())