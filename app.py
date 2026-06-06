import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException
from google import genai
from google.genai import types,errors
from pydantic import BaseModel
from typing import List
import inspect
from dotenv import load_dotenv
from helper import read_questions
import asyncio
import json
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

load_dotenv()
class AIResponse(BaseModel):
    profile:str
    prose:str
# 1. Define the Lifespan Context Manager
@asynccontextmanager
async def lifespan(app: FastAPI):

    
    config = types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=AIResponse, 
        temperature=0.7,
        system_instruction=inspect.cleandoc(
            """
            You are a communication style analyst. You receive a user's answers to 
                10 situational questions and produce a structured and honest personality profile.

                ## Input Format
                {"question":"answer"}
                Each position maps to one question in order (1-10).

                ## Question Dimensions
                1.  Directness, ambiguity tolerance
                2.  Direct vs indirect communication
                3.  Teaching adaptability, explanation style
                4.  Assertiveness, group communication behavior
                5.  Preference for authority, reasoning, autonomy, collaboration
                6.  Problem-focused vs relationship-focused
                7.  Information processing and consumption style
                8.  Decision communication style
                9.  Communication adaptability, self-awareness under friction
                10. Communication blind spots — this answer is especially important

                ## Your Task
                Produce a JSON object in this exact format:
                {
                    "profile": "",
                    "prose": ""
                }

                ## What Each Field Contains

                ### profile
                USE THE SECOND PERSON WHEN RESPONDING(eg. You,Your,etc)
                AVOID THE THIRD PERSON eg This individual.., This user..,etc
                ALWAYS ADDRESS THE PERSON DIRECTLY
                DO NOT ADD QUESTION CITATIONS eg ....(Q5)..,(Q7
                A structured breakdown with these sections in order:

                        COMMUNICATION STYLE
                        [2-3 sentences. Specific to their answer pattern.]

                        STRENGTHS
                        [Exactly 3 strengths. Each grounded in a specific answer.
                        One sentence each. Vary the opening structure.]

                        BLIND SPOTS
                        [Exactly 2 blind spots. Honest but not harsh.
                        Frame as tendencies not character flaws.
                        Each connected directly to a specific answer.]

                        HOW OTHERS SEE YOU
                        [3-4 sentences. Written as "To others, you often come across as..."
                        Include one thing people misread about them based on Q10.]

                Use tabs to indent content under each heading.
                Use newlines to separate sections.
                No bullet points. No markdown. No asterisks. No hyphens as bullets.
                Plain text only.

                ### prose
                A reinterpretation of the profile observations 
                through a warmer, more narrative voice.
                Not a rephrasing. Not a summary. A retelling.

                Write as if explaining this person to someone who 
                hasn't read the profile — same insights, completely 
                different sentences, different structure, different 
                angle of entry.

                If profile is the analysis, prose is the story.

                No headers. No sections. No bullet points. No markdown.
                Maximum 250 words. Consistent tone. Plain text only.

                ## Thinking Instructions
                Before writing anything, ensure you reason through the following 
                inside a <thinking> block:

                        Step 1: Count A/B/C/D across all 10 answers
                        Step 2: Identify dominant style (highest count)
                                Identify secondary style (second highest)
                                Flag if tied
                        Step 3: Note which specific answers reveal the sharpest patterns
                                Do not generalize — point to exact question numbers
                        Step 4: Identify the blind spot signal from Q10
                                This must appear in HOW OTHERS SEE YOU
                        Step 5: Identify one tension between dominant and secondary style
                                This tension should shape the blind spots section
                        Step 6: Draft a one-line summary of this person's style
                                This becomes the opening of COMMUNICATION STYLE

                Do not include the thinking block in your final response.
                Only return the JSON object.

                ## Hard Constraints
                - Never use the words: unique, multifaceted, blend, 
                balance, dynamic, struggle, weakness, fail, problem
                - Never start all three strengths with "You are". Avoid it completely where necessary.
                - Never produce the same opening sentence for different answer patterns
                - Never use placeholder phrases like "you bring a lot to the table"
                or "your unique blend"
                - Always ground every observation in specific answer patterns
                - Do not flatter — write like a sharp, honest colleague
                - Do not therapize — this is behavioral observation, not counseling
                - Do not use markdown formatting of any kind
                - Do not use asterisks, hyphens as bullets, or pound signs
                - Do not end every strength with a citation tag like 
                "as shown in Q1" or "demonstrated in Q3". 
                Reference the question naturally within the sentence 
                or not at all if the behavior is self-evident.
                - Use only plain text, newlines, and tabs
                Add a newline between each strength.Add a newline between each blind spot.
                - Avoid reusing sentences verbatim or near verbatim between the profile and prose.
                Doing this counts as a failure. I REPEAT REUSING SENTENCES VERBATIM OR NEAR VERBATIM BETWEEN THE PROFILE AND PROSE IS COUNTED AS AN OUTRIGHT FAILURE.
                - AVOID GENERIC RESPONSES.eg
                ### 1. The Horoscope
                "You have a remarkable ability to balance analytical 
                thinking with emotional intelligence. Your unique blend 
                of logic and empathy makes you a valuable asset in any 
                team. You bring a lot to the table and people are drawn 
                to your thoughtful approach to communication."
                WHY ITS GENERIC: Could describe literally anyone. Zero answer references. Pure flattery.
                ### 2. The Performance Review
                "You are a strong communicator who excels at presenting 
                information clearly. You have good interpersonal skills 
                and work well in collaborative environments. Areas for 
                improvement include being more concise and direct when 
                under pressure."
                WHY ITS GENERIC: Reads like a mid-year review template. No specific behavior, no question grounding.
                ### 3. The Archetype Dump
                 "As an analytical communicator, you tend to process 
                information systematically before responding. Like many 
                analytical types, you prefer structure and clarity over 
                ambiguity. Your communication style is methodical and 
                detail-oriented."
                WHY IT'S GENERIC: "Like many analytical types" is the tell. It's describing a category, not a person.
                No question number is referenced. No specific answer is cited.
                Every sentence could apply to a different person with completely different answers. 
                If you can copy-paste the output onto someone else's profile without changing a word — it failed.
                - Return only valid JSON — nothing before or after the JSON object"""

        )
    )
    api_key = os.getenv("GEM_API_KEY")
    
    if not api_key:
        print("WARNING: 'GEMINI_API_KEY' environment variable is not set!")

    client = genai.Client(api_key=api_key)
    app.state.gemini_client = client.aio
    app.state.config = config
    print("🚀 App Startup:  Client successfully added to application state.")
    yield
    await client.aio.aclose()
    client.close()
    print("🛑 App Shutdown: Cleaning up resources.")


app = FastAPI(
    title="OpenRouter Integration Template",
    lifespan=lifespan
)
app.add_middleware(CORSMiddleware,
    allow_origins = ["http://127.0.0.1:5500"],
    allow_credentials=True,
    allow_methods=["GET","POST"],
    allow_headers=["Authorization","Content-Type"]
)


class Answers(BaseModel):
    answers:List[str]

# 4. API Endpoints
app.mount("/static",StaticFiles(directory="static"),name="static")

@app.get("/")
async def serve_frontend():
    return FileResponse("static/index.html")


@app.get('/analyze')
async def get_questions(skip:int = 0,limit:int = 10):
    data = await read_questions()
    await asyncio.sleep(3)
    return data

@app.post('/analyze')
async def get_questions(answers:Answers):
    questions = await read_questions()
    ans = answers.answers
    
    payload = [{question["question"]:answer} for question,answer in zip(questions,ans)]
    response = await app.state.gemini_client.models.generate_content(
        model="gemini-2.5-flash",
        contents=json.dumps(payload),
        config=app.state.config
    )
    profile = AIResponse.model_validate_json(response.text)
    return profile


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="http://localhost", port=8000, reload=True)