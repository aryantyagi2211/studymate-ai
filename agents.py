"""
agents.py — StudyMate AI Agent Definitions (Direct Groq Integration)

Enhanced agent implementation with verbose/debug, reasoning, and Foundry IQ search.
"""

from openai import AsyncOpenAI, RateLimitError
from dotenv import load_dotenv
import os
import asyncio
import random
import time
from datetime import datetime

load_dotenv()

# Multiple API keys for rotation
API_KEYS = []

# Collect all GROQ_API_KEY* environment variables
for key in ["GROQ_API_KEY", "GROQ_API_KEY_2", "GROQ_API_KEY_3", "GROQ_API_KEY_4", "GROQ_API_KEY_5"]:
    api_key = os.getenv(key)
    if api_key and api_key.strip():
        API_KEYS.append(api_key.strip())

# Also support comma-separated keys in GROQ_API_KEY
if os.getenv("GROQ_API_KEY"):
    for key in os.getenv("GROQ_API_KEY", "").split(","):
        if key.strip() and key.strip() not in API_KEYS:
            API_KEYS.append(key.strip())

if not API_KEYS:
    raise ValueError("No GROQ_API_KEY found in .env file!")

print(f"[API] Loaded {len(API_KEYS)} API key(s) for rotation")

# Multiple models for load balancing and rate limit handling
# Using stable models without tool-calling issues
MODELS = [
    "llama-3.1-8b-instant",
    "llama-3.3-70b-versatile"
]

def get_groq_client():
    """Get a Groq client with a random API key"""
    api_key = random.choice(API_KEYS)
    return AsyncOpenAI(
        base_url="https://api.groq.com/openai/v1",
        api_key=api_key,
    )

def get_model():
    """Rotate between available models to handle rate limits"""
    return random.choice(MODELS)


def print_debug(message: str, verbose: bool = False):
    """Print debug messages when verbose mode is enabled"""
    if verbose:
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[DEBUG {timestamp}] {message}")


def print_reasoning(step: int, thought: str, verbose: bool = False):
    """Print reasoning steps when verbose mode is enabled"""
    if verbose:
        print(f"[REASONING Step {step}] {thought}")


class SimpleAgent:
    def __init__(self, name, description, instructions, verbose=False, reasoning=False, enable_tools=False):
        self.name = name
        self.description = description
        self.instructions = instructions
        self.verbose = verbose
        self.reasoning = reasoning
        self.enable_tools = enable_tools
        self.tool_calls_count = 0
        self.total_tokens = 0
        
    def create_session(self):
        """Create a new conversation session"""
        return []  # Just a list to store message history
    
    def _build_reasoning_prompt(self, prompt: str) -> str:
        """Add chain-of-thought reasoning to the prompt"""
        # Check if this agent needs pure output (JSON, etc.)
        needs_pure_output = any(keyword in self.instructions.lower() for keyword in [
            "return only valid json",
            "only json",
            "must return only",
            "critical: you must return only"
        ])
        
        if needs_pure_output:
            return prompt
        
        # Flatten reasoning into rough string - not too structured
        reasoning_template = """Think step-by-step: What's the student asking? What do I know about their level? What approach makes sense here? How should I respond? Now answer: {prompt}"""
        
        return reasoning_template.format(prompt=prompt)
    
    def _check_if_needs_search(self, prompt: str) -> bool:
        """Determine if the prompt would benefit from web search"""
        search_triggers = [
            "latest", "current", "recent", "tutorial", "documentation",
            "learn more", "resources", "guide", "example", "how to",
            "best practices", "official", "2024", "2025", "updated"
        ]
        prompt_lower = prompt.lower()
        return any(trigger in prompt_lower for trigger in search_triggers)
    
    async def _perform_search(self, query: str) -> str:
        """Perform web search using Microsoft Foundry IQ (or fallback to SerpAPI)"""
        try:
            # Import Foundry IQ search
            from tools.foundry_search import foundry_search, format_foundry_results
            
            print_debug(f"Performing Foundry IQ search: {query}", self.verbose)
            
            # Extract certification if available (check instructions)
            certification = None
            if "AZ-204" in self.instructions or "az-204" in self.instructions.lower():
                certification = "AZ-204"
            
            results = foundry_search(query, num_results=3, certification=certification)
            formatted = format_foundry_results(results, max_results=3)
            self.tool_calls_count += 1
            
            if self.verbose:
                print(f"\n[TOOL CALL] foundry_search (Microsoft IQ)")
                print(f"[QUERY] {query}")
                if certification:
                    print(f"[CERTIFICATION FILTER] {certification}")
                foundry_active = results[0].get('foundry_iq', False) if results else False
                print(f"[FOUNDRY IQ ACTIVE] {foundry_active}")
                print(formatted)
            
            return formatted
        except ImportError:
            # Fallback to basic web search
            print_debug("Foundry IQ not available, using SerpAPI", self.verbose)
            try:
                from tools.web_search import web_search, format_search_results
                results = web_search(query, num_results=3)
                formatted = format_search_results(results, max_results=3)
                self.tool_calls_count += 1
                
                if self.verbose:
                    print(f"\n[TOOL CALL] web_search (fallback)")
                    print(f"[QUERY] {query}")
                    print(formatted)
                
                return formatted
            except Exception as e:
                print_debug(f"Search error: {e}", self.verbose)
                return ""
        except Exception as e:
            print_debug(f"Search error: {e}", self.verbose)
            return ""
    
    async def run(self, prompt, session=None, max_retries=3):
        """Run the agent with a prompt, with rate limit handling"""
        start_time = time.time()
        
        if session is None:
            session = []
        
        # Verbose mode: Show input details
        if self.verbose:
            print("\n" + "="*70)
            print(f"[AGENT] {self.name}")
            print(f"[INPUT] {prompt[:100]}{'...' if len(prompt) > 100 else ''}")
            print(f"[SESSION] {len(session)} messages in history")
            # print(f"[DEBUG] Full prompt: {prompt[:200]}...")  # sometimes useful for debugging
        
        # Check if we should search for information
        search_context = ""
        if self.enable_tools and self._check_if_needs_search(prompt):
            # Extract key terms for search
            search_query = prompt[:200]  # Simple approach: use first part of prompt
            search_context = await self._perform_search(search_query)
        
        # Build enhanced prompt with reasoning if enabled
        enhanced_prompt = prompt
        if self.reasoning:
            enhanced_prompt = self._build_reasoning_prompt(prompt)
            print_debug("Chain-of-Thought reasoning enabled", self.verbose)
        
        # Add search context if available
        if search_context:
            enhanced_prompt = f"{search_context}\n\nBased on the above search results:\n{enhanced_prompt}"
        
        # Build messages with system instructions
        messages = [{"role": "system", "content": self.instructions}]
        
        # Add conversation history
        messages.extend(session)
        
        # Add user message
        messages.append({"role": "user", "content": enhanced_prompt})
        
        # Try different models and API keys if rate limited
        for attempt in range(max_retries):
            try:
                groq_client = get_groq_client()
                model = get_model()
                
                print_debug(f"Using model: {model}", self.verbose)
                
                # Avoid tool-capable models if they cause issues
                if model == "openai/gpt-oss-20b":
                    model = "llama-3.1-8b-instant"  # Fallback to stable model
                
                response = await groq_client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=0.7,
                    max_tokens=2000,  # Limit response length
                )
                
                assistant_message = response.choices[0].message.content
                
                # Track token usage (approximate)
                prompt_tokens = sum(len(m.get("content", "")) for m in messages) // 4
                completion_tokens = len(assistant_message) // 4
                self.total_tokens += (prompt_tokens + completion_tokens)
                
                # Update session history
                session.append({"role": "user", "content": prompt})
                session.append({"role": "assistant", "content": assistant_message})
                
                # Verbose mode: Show output details
                elapsed = time.time() - start_time
                if self.verbose:
                    print(f"[MODEL] {model}")
                    print(f"[TOKENS] ~{prompt_tokens} prompt + ~{completion_tokens} completion = ~{prompt_tokens + completion_tokens} total")
                    print(f"[TIME] {elapsed:.2f}s")
                    print(f"[TOOLS USED] {self.tool_calls_count} calls this session")
                    print(f"[OUTPUT LENGTH] {len(assistant_message)} characters")
                    print("="*70 + "\n")
                
                # Return response object
                class Response:
                    def __init__(self, text):
                        self.text = text
                        self.content = text
                
                return Response(assistant_message)
                
            except RateLimitError as e:
                if attempt < max_retries - 1:
                    wait_time = 10 * (attempt + 1)  # Exponential backoff
                    print(f"\n[WARNING] Rate limit hit. Trying different API key/model in {wait_time}s...")
                    await asyncio.sleep(wait_time)
                else:
                    print(f"\n[ERROR] Rate limit error after {max_retries} attempts.")
                    print("All API keys exhausted. Please wait or add more API keys in .env")
                    print("Format: GROQ_API_KEY=key1,key2,key3")
                    raise


ceo_agent = SimpleAgent(
    name="CEO Agent",
    description="Chief Orchestrator of StudyMate AI",
    verbose=False,
    reasoning=False,
    enable_tools=False,
    instructions="""You are the CEO of StudyMate AI. Be warm, confident, and CONCISE.

When welcoming a new student:
- Welcome them in 2-3 sentences max
- Briefly explain what will happen (profile → assess → learn → test)
- Keep it simple and encouraging

When making final decisions:
- State your decision clearly in 2-3 sentences
- If more teaching needed: say which concept
- If more practice needed: say which skill  
- If ready to advance: congratulate and state next step

NO long explanations. NO bullet points. Just clear, direct communication."""
)


profiler_agent = SimpleAgent(
    name="Profiler Agent",
    verbose=False,
    reasoning=True,
    enable_tools=False,
    description="The Student's First Friend at StudyMate",
    instructions="""You are the first person a new student talks to at StudyMate. Think of yourself as a friendly senior who is genuinely curious about them — not a form they have to fill out.

Before any learning begins, help the student feel seen. Find out:
- Why they actually want this certification — a promotion, a career goal, curiosity, or pressure from someone else are all valid answers
- How they are feeling about starting — excited, nervous, overwhelmed, or something else
- What worries them most about this certification

Respond to what they actually say, the way a real person would. Use their answers to understand what is really motivating them, and gently set the tone for the learning journey ahead.

Keep your messages short, warm, and conversational — no bullet points, no headings, and nothing that sounds like a script."""
)


knowledge_checker = SimpleAgent(
    name="Knowledge Checker",
    description="Baseline Knowledge Assessor",
    verbose=False,
    reasoning=True,
    enable_tools=False,
    instructions="""You are the Knowledge Checker. Your job is to create a comprehensive assessment to understand where the student currently stands.

Create exactly 10 multiple-choice questions (MCQs) that cover all required skills for their certification. Each question should:
- Test a specific concept or skill
- Have 4 options (A, B, C, D)
- Have one correct answer
- Include a brief explanation

CRITICAL: You MUST return ONLY valid JSON with NO markdown formatting, NO code fences, NO extra text. 

Use this EXACT format:

{
  "questions": [
    {
      "id": 1,
      "skill": "API Development",
      "question": "What is the primary purpose of API keys in API development?",
      "options": ["To encrypt data", "To authenticate and authorize access", "To compress requests", "To cache responses"],
      "correct_answer": "B",
      "explanation": "API keys provide a secure way to authenticate and authorize access to APIs"
    }
  ]
}

The questions will be presented to the student one at a time, so make each question clear and self-contained."""
)


learning_path_agent = SimpleAgent(
    description="Expert Learning Path Designer",
    name="Learning Path Agent",
    verbose=False,
    reasoning=True,
    enable_tools=True,
    instructions="""You are the Learning Path Agent — a senior developer who has tried a hundred different resources and knows exactly what's worth a student's time.

For each skill the student needs to work on, recommend a focused set of resources: official documentation, a strong video or course, a well-written article or blog post, and a hands-on exercise or small project they can actually build.

Be specific. Name real resources whenever you're confident they exist. If you're not sure a link is correct, give the student a precise search term instead of guessing a URL — a dead link is worse than no link.

Keep the tone casual and encouraging, like a senior dev pointing a junior teammate in the right direction — not a formal list of references."""
)


adaptive_planner = SimpleAgent(
    name="Adaptive Planner Agent",
    description="Personal Study Schedule Builder",
    reasoning=True,
    verbose=False,
    enable_tools=False,
    instructions="""You are the Adaptive Planner. Ask questions ONE AT A TIME to build a study schedule.

If this is your first message, ask ONLY:
"How many hours per day can you realistically study?"

After they answer, ask the NEXT question:
"What time works best for you? (morning/afternoon/evening)"

After they answer, ask the FINAL question:
"Any busy days coming up when you can't study?"

Once you have all 3 answers, create a CONCISE 1-week schedule (under 150 words):
- Daily study time: [X hours]
- Best time: [morning/afternoon/evening]
- Skip days: [list days]
- Emergency backup: 10-min quick review plan

Keep it simple and actionable."""
)


teaching_agent = SimpleAgent(
    name="Teaching Agent",
    description="The World's Most Patient Concept Teacher",
    verbose=False,
    reasoning=True,
    enable_tools=True,
    instructions="""You are the Teaching Agent — patient, encouraging, and never in a rush.

Take the concept the student needs most and teach it in two ways:
1. A clear, simple explanation in plain language
2. A real-world example from an actual job scenario, showing how this concept shows up in practice

After teaching, ask the student if it made sense. If they say no or only partly, teach the same concept again from a different angle — a new example, a different analogy, or a simpler breakdown — until it clicks.

Never move on to the next concept until the student confirms they understood this one."""
)


examiner_agent = SimpleAgent(
    name="Examiner Agent",
    description="Fair and Thorough Certification Examiner",
    verbose=False,
    reasoning=True,
    enable_tools=False,
    instructions="""You are the Examiner — fair, clear, and focused on testing what the student learned.

You will conduct a 15-question exam by asking questions ONE AT A TIME:
- Questions 1-5: EASY multiple choice (A/B/C/D)
- Questions 6-10: MEDIUM multiple choice (A/B/C/D)
- Questions 11-15: HARD open-ended questions

For each MCQ:
- State the difficulty level ([EASY] / [MEDIUM] / [HARD])
- Ask the question clearly
- Provide 4 options labeled A, B, C, D
- Wait for student's answer
- Tell them if correct/incorrect
- Give brief explanation

For open-ended questions:
- State it's a detailed question
- Ask the question
- Wait for their answer
- Provide feedback on their response

Ask ONE question at a time. Keep track of which question number you're on (1-15).
After question 15, provide a final score summary."""
)


manager_insights_agent = SimpleAgent(
    name="Manager Insights Agent",
    description="Student Performance Reporter and Analyst",
    verbose=False,
    reasoning=True,
    enable_tools=False,
    instructions="""You are the Manager Insights Agent. Provide SHORT, actionable reports to the CEO.

Format (keep under 100 words total):

**Performance:** [1 sentence on what went well and what struggled]
**Concerns:** [1 sentence on weak skills or stress signals]
**Recommendation:** [1 clear sentence: more teaching/practice/advance]

Be direct. No fluff. CEO needs to make fast decisions."""
)


# TODO: might want to add retry logic for tool failures
# TODO: consider adding caching for repeated Foundry IQ searches
