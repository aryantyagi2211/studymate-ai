# 🎓 StudyMate AI
### 8 Reasoning Agents That Actually Teach You — Not Just Dump Content At You

> Built for **Microsoft Agents League Hackathon 2026** · Reasoning Agents Track · Powered by Groq LLM

---

## The Real Problem Nobody Talks About

You've probably tried to prepare for a certification before. You paid for a course. You watched 40 hours of videos. You read documentation. And then you sat in the exam and blanked on the exact concepts you thought you understood.

**Why does this happen?**

Because most learning platforms treat every student the same. They give you the same content, the same schedule, and the same tests — regardless of what you already know, how busy your week is, or whether you actually understood what you just read.

StudyMate AI was built to fix this. Not with more content. With smarter agents that reason about *you*.

---

## What StudyMate AI Actually Does

Instead of a single AI model answering questions, StudyMate AI uses **8 specialized agents** that each have one job and do it well. They pass information to each other, reason about your performance, and adapt the entire learning journey based on what they find.

Here's the key thing that makes it different: **it loops.**

If you score below 70% on the exam, the system doesn't just show you your score and move on. The CEO Agent reads the Manager's report, identifies exactly which concepts you're weak on, sends you back to the Teaching Agent with a completely new explanation approach, then retests you. This loop runs until you hit 85%+.

That's not a feature. That's how actual learning works.

---

## The 8 Agents — What Each One Does

### 🧠 1. Profiler Agent
*"Let me understand who you are before we start"*

Before a single question is asked, the Profiler has a real conversation with you. Not a form. Not a dropdown. A conversation.

It finds out why you actually want this certification (your boss told you to? a promotion? genuine curiosity?), how you're feeling about starting, and what worries you most. This shapes how every other agent talks to you.

---

### 🔍 2. Knowledge Checker
*"What do you already know? Let's find out fast"*

10 diagnostic MCQs covering every skill area in your certification. Questions appear one at a time. After you answer all 10, it ranks every skill:

- **STRONG** → We'll skip this. No wasted time.
- **MEDIUM** → Quick reinforcement only.
- **WEAK** → This is where we focus.

---

### 📚 3. Learning Path Designer
*"Here's exactly what you need — nothing more"*

Takes your skill ranking and builds a focused resource list. For every weak area: the best Microsoft Learn module, a YouTube channel worth watching, a hands-on exercise you can actually do, and a realistic time estimate.

It skips what you're already strong at. Completely. No padding.

---

### 📅 4. Adaptive Planner
*"A schedule for your real life, not your ideal life"*

Asks you how many hours you can actually study per day, when your energy is highest, which days you'll skip, and if anything stressful is coming up. Then it builds a week-by-week plan around those answers — including a 10-minute emergency plan for the days when everything falls apart.

---

### 👨‍🏫 5. Teaching Agent
*"I'll explain this until it actually clicks"*

Takes your weakest skill and teaches it two ways: a plain-language explanation, and a real job scenario where this concept shows up in practice. Then it asks if it made sense.

If you say no — it doesn't repeat itself. It finds a completely different angle, a new analogy, a simpler breakdown. It only moves on when you say you understood.

---

### ✍️ 6. Examiner Agent
*"Let's see what you actually know"*

15 questions: 5 easy MCQs, 5 medium MCQs, 5 hard open-ended questions. Questions appear one at a time. After each MCQ you get instant feedback. After the open-ended questions you get a detailed comparison against the model answer.

Results are scored by difficulty level so the system knows exactly where your gaps are.

---

### 📊 7. Manager Insights Agent
*"Here's what the data actually says"*

Analyzes everything — exam scores by difficulty, which skills failed, your work signals (meeting load, energy level, upcoming stress). Writes a short, honest report for the CEO. Three sections: what went well, what needs attention, and what should happen next.

No fluff. The CEO needs to make a fast decision.

---

### 🎓 8. CEO Decision Maker
*"Ready to move on, or do you need more help?"*

Reads the Manager's report and makes the call:

```
Score 85%+  → "You're ready. Here's your next step."
Score 70-84% → "One more practice round on [specific skill]"
Score below 70% → "Back to teaching. Here's what we'll focus on."
```

This triggers the adaptive loop. The system keeps going until you're actually ready.

---

## The Adaptive Loop — Why This Matters

```
Profiler → Knowledge Checker → Learning Path → Study Plan
                                                    ↓
                                             Teaching Agent
                                                    ↓
                                             Examiner Agent
                                                    ↓
                                          Manager Insights
                                                    ↓
                                           CEO Decision
                                          ↙           ↘
                               Score 85%+         Score below 85%
                              Move forward    ←── Loop back to Teaching
```

Most learning systems are linear. You go through them once and you're done, ready or not. StudyMate AI is a loop. You stay in it until you're genuinely prepared.

---

## Microsoft IQ Integration

This project integrates with **Foundry IQ** as the intelligence layer:

- Agent reasoning is grounded in certification-specific knowledge bases
- Each agent's decision logic follows the Foundry IQ retrieval pattern: understand context → retrieve relevant information → reason → respond
- The multi-agent orchestration follows Microsoft Agent Framework patterns for sequential and adaptive agent handoff

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| LLM | Groq API (LLaMA 3.1 8B + LLaMA 3.3 70B) |
| Agent Framework | Custom SimpleAgent class with session management |
| Rate Limiting | Multi-key rotation + exponential backoff |
| Data | Synthetic student profiles (no real PII) |
| UI | Streamlit |
| Language | Python 3.10+ |

---

## Why Groq Instead of Azure OpenAI

Azure OpenAI requires a paid subscription with credit card verification — which isn't available in all regions. Groq provides free-tier access to LLaMA models with the same OpenAI-compatible API, making this project accessible to anyone who wants to run it.

The agent architecture is model-agnostic. Swapping Groq for Azure OpenAI is a one-line change in `agents.py`.

---

## Running It Yourself

**Prerequisites:**
- Python 3.10+
- Free Groq API key from [console.groq.com](https://console.groq.com)

**Setup:**

```bash
git clone https://github.com/aryantyagi2211/studymate-ai
cd studymate-ai

python -m venv .venv
.venv\Scripts\activate     # Windows
source .venv/bin/activate  # Mac/Linux

pip install -r requirements.txt
```

**Create a `.env` file:**
```
GROQ_API_KEY=your_key_here
```

**Run:**
```bash
# Terminal version
python main.py

# Web UI
streamlit run app.py
```

---

## Project Structure

```
studymate-ai/
├── agents.py          # All 8 agent definitions
├── tasks.py           # Task prompts for each agent
├── main.py            # Terminal orchestrator
├── app.py             # Streamlit web UI
├── data/
│   └── data.py        # Synthetic learner + certification data
├── requirements.txt
└── .env               # Your API key (not committed)
```

---

## Synthetic Data Notice

All student data used in this project is synthetic and created specifically for this demo. No real names, real emails, real employee records, or any PII was used. Learner IDs like `L-1001` and employee IDs like `EMP-001` are fictional identifiers.

---

## What's Next

The foundation is built. Here's what comes next:

- **Real-time user input** — instead of demo profiles, you enter your own details
- **Any certification** — currently AZ-204, AZ-400, DP-203 — expandable to any cert
- **Microsoft 365 Work IQ integration** — use real calendar and meeting data for smarter scheduling
- **Foundry IQ knowledge base** — upload your company's internal training docs and ground the agents in them
- **Parent/manager dashboard** — visibility into team certification readiness

---

## Built By

**Aryan Tyagi** — [github.com/aryantyagi2211](https://github.com/aryantyagi2211)

*Microsoft Agents League Hackathon 2026 · Reasoning Agents Track*

---

> *"The best learning system isn't the one with the most content. It's the one that knows when to stop, when to loop back, and when you're actually ready."*