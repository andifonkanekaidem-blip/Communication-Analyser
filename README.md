# Communication Style Analyzer

A web application that generates a personalized communication style profile 
from 10 situational questions. Built as a portfolio project demonstrating 
applied prompt engineering, API integration, and full-stack AI product design.

---

## What It Does

The user answers 10 situational questions designed around real communication 
friction — not hypothetical preferences. The app sends their answers to a 
backend pipeline that uses a large language model to produce two outputs:

- A structured breakdown covering communication style, strengths, blind spots, 
  and how others perceive them
- A narrative summary retelling the same insights through a warmer, 
  more personal lens

---

## Why The Questions Are Designed This Way

Most personality assessments ask what you prefer. These questions ask what 
you actually do — especially under friction, ambiguity, and conflict. 

Each question targets a specific communication dimension:

1. Directness and ambiguity tolerance
2. Direct vs indirect communication
3. Teaching adaptability and explanation style
4. Assertiveness in group settings
5. Preference for authority, reasoning, autonomy, or collaboration
6. Problem-focused vs relationship-focused communication
7. Information processing and consumption style
8. Decision communication style
9. Communication adaptability under friction
10. Communication blind spots

Questions are framed around failure and friction rather than aspiration 
to reduce socially flattering answers — the single biggest validity problem 
in self-assessment tools.

---

## Prompt Engineering Decisions

This section documents the core design choices behind the AI output layer.

### Single-call structured generation
The entire profile is generated in one API call using a structured 
Chain-of-Thought approach. The model reasons through answer patterns 
privately before producing output, ensuring observations are grounded 
in specific answers rather than general archetypes.

### Two-field output design
The model produces two distinct fields — profile and prose — with an 
explicit instruction that prose must reinterpret rather than restate. 
Profile is the analysis. Prose is the story. This prevents the model 
from treating the second field as a copy-paste with headings removed.

### Anti-generic constraints
The prompt explicitly defines what a generic response looks like with 
annotated examples, and instructs the model to treat generic output as 
a failure. Every observation must reference a specific question number. 
No output should be transferable to a user with different answers.

### Banned language
The following words are banned from output to prevent flattery and 
vague archetype language:
unique, multifaceted, blend, balance, dynamic, struggle, weakness, 
fail, problem

### Blind spot framing
Blind spots are framed as behavioral tendencies connected to specific 
answers — not character flaws or performance review criticisms. The Q10 
answer (what feedback stung most) is treated as a high-signal input and 
must appear in both the blind spots and the perception section.

---

## Failure Modes Encountered and Fixed

| Failure | Root Cause | Fix Applied |
|---|---|---|
| Empty JSON returned | CoT thinking block exceeded token budget | Added 150-word limit on thinking block |
| Verbatim prose | Model treated prose as reformatted profile | Reframed prose as a retelling for a different audience |
| Generic openings | Model pattern-matching to answer type, not specific answers | Added requirement to reference specific question numbers |
| Banned words appearing | Constraints buried at bottom of prompt | Moved hard constraints closer to relevant sections |
| Wrong JSON structure | Model nested objects inside profile field | Schema enforcement via Gemini structured output |
| Harsh blind spot tone | No explicit framing instruction | Added "frame as tendencies not character flaws" |
| All strengths starting with "You are" | No structural variation instruction | Added explicit variation requirement |

---

## Tech Stack

- **Backend:** FastAPI (Python)
- **AI:** Gemini 2.5 Flash via Google Generative AI SDK
- **Output validation:** Gemini schema enforcement (structured output)
- **Frontend:** Vanilla HTML, CSS, JavaScript
- **Serving:** FastAPI static file serving

---

## Project Structure
project/
├── main.py              # FastAPI app, routes, Gemini integration
├── questions.json       # Question and answer option definitions
├── static/
│   └── index.html       # Frontend single-page application
└── .env                 # API keys (not committed)

---

## Running Locally

```bash
# Install dependencies
pip install fastapi uvicorn google-generativeai python-dotenv

# Add your API key to .env
GEMINI_API_KEY=your_key_here

# Start the server
uvicorn main:app --reload

# Open in browser
http://localhost:8000
```

---

## What This Project Demonstrates

- Prompt design from first principles — no frameworks, no templates
- Iterative prompt refinement with documented failure modes
- Structured Chain-of-Thought to improve output grounding
- Anti-pattern awareness — designing against flattery, verbatim drift, 
  and generic archetype outputs
- Full pipeline from user input to validated AI output to rendered UI
- Separation of prompt problems from logic problems during debugging

---

## Limitations

- Results reflect behavioral tendencies based on self-reported answers, 
  not observed behavior
- A 10-question instrument cannot capture the full complexity of 
  communication style
- Model outputs may vary slightly across runs for identical inputs 
  due to temperature settings
- No answer validation — users can answer inconsistently and receive 
  a coherent but inaccurate profile

---

## Author

Built by Andy — Mechatronics Engineering student and freelance AI systems 
developer focused on prompt engineering, agent design, and AI integration 
for small businesses.
