# code-analyzer-service/main.py
"""
.env
GEMINI_API_KEY = "AIzaSyBZCpUd5ObGwY8sdcfQ1qJ6fjWw86PsD9Q"
RATE_LIMIT_DELAY_SECONDS=0.5
MAX_RETRIES=3
INITIAL_BACKOFF=1.0s
"""


import os
import json
import asyncio
import logging
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Assuming these are defined in your `service.py`
from service import Submission, AnalysisResult  

# Initialize logger
logger = logging.getLogger("uvicorn")
logging.basicConfig(level=logging.INFO)

# Load environment variables (like GEMINI_API_KEY) from .env file
load_dotenv()

# --- CONFIGURATION ---
MODEL_ID = 'gemini-flash-latest'  # Changed to Gemini Flash model
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# --- RATE LIMIT / RETRY CONFIGURATION ---
RATE_LIMIT_DELAY_SECONDS = float(os.getenv('RATE_LIMIT_DELAY_SECONDS', '0.5'))
MAX_RETRIES = int(os.getenv('MAX_RETRIES', '5'))
INITIAL_BACKOFF = float(os.getenv('INITIAL_BACKOFF', '2.0'))
MAX_BACKOFF = float(os.getenv('MAX_BACKOFF', '60.0'))  # Cap backoff at 60 seconds

# Ensure API key is loaded
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in environment variables. Check your .env file.")

# Initialize Gemini Client (once, globally)
try:
    client = genai.Client(api_key=GEMINI_API_KEY)
except Exception as e:
    raise RuntimeError(f"Failed to initialize Gemini Client: {e}")

# Initialize FastAPI App
app = FastAPI(
    title="Gemini Code Analyzer Microservice",
    description="Analyzes code submissions using Gemini Flash for logic, structure, and correctness.",
    version="1.0.0"
)

# --- Pydantic Models (Schemas) ---
class Submission(BaseModel):
    candidate_id: str
    question: str
    expected_output: str
    candidate_output: str
    candidate_code: str

class AnalysisResult(BaseModel):
    candidate_id: str
    total_score: Optional[int] = None
    improvements_suggested: str
    detailed_analysis: str
    code_review: Optional[dict] = None
    error: Optional[str] = None

# --- GEMINI SCORING UTILITIES ---
def get_analysis_schema():
    """Defines the structure for the desired JSON output for Gemini's response."""
    return types.Schema(
        type=types.Type.OBJECT,
        properties={
            "Total_Score": types.Schema(type=types.Type.INTEGER, description="The final aggregate score out of 100."),
            "Improvements_Suggested": types.Schema(type=types.Type.STRING, description="Specific, actionable steps to improve the code."),
            "Detailed_Analysis": types.Schema(type=types.Type.STRING, description="A comprehensive paragraph explaining the overall strengths and weaknesses.")
        },
        required=["Total_Score", "Improvements_Suggested", "Detailed_Analysis"]
    )

def get_code_review_schema():
    """Defines the structure for AI code review (senior engineer perspective)."""
    return types.Schema(
        type=types.Type.OBJECT,
        properties={
            "Style_And_Readability": types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "score": types.Schema(type=types.Type.INTEGER, description="Score out of 10."),
                    "findings": types.Schema(type=types.Type.STRING, description="Analysis of naming conventions, formatting, comments.")
                },
                required=["score", "findings"]
            ),
            "Maintainability": types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "score": types.Schema(type=types.Type.INTEGER, description="Score out of 10."),
                    "findings": types.Schema(type=types.Type.STRING, description="Code reusability, modularity, and maintainability assessment.")
                },
                required=["score", "findings"]
            ),
            "Complexity_Analysis": types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "time_complexity": types.Schema(type=types.Type.STRING, description="Big-O time complexity with explanation."),
                    "space_complexity": types.Schema(type=types.Type.STRING, description="Big-O space complexity with explanation."),
                    "assessment": types.Schema(type=types.Type.STRING, description="Natural-language reasoning about efficiency.")
                },
                required=["time_complexity", "space_complexity", "assessment"]
            ),
            "Security_Review": types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "vulnerabilities": types.Schema(type=types.Type.STRING, description="Identified security issues or empty string if none."),
                    "recommendations": types.Schema(type=types.Type.STRING, description="Security best practices to implement.")
                },
                required=["vulnerabilities", "recommendations"]
            ),
            "Suggested_Refactors": types.Schema(
                type=types.Type.ARRAY,
                items=types.Schema(
                    type=types.Type.OBJECT,
                    properties={
                        "refactor_title": types.Schema(type=types.Type.STRING, description="Title of the refactoring suggestion."),
                        "reason": types.Schema(type=types.Type.STRING, description="Why this refactoring matters."),
                        "example": types.Schema(type=types.Type.STRING, description="Code example of the suggested change.")
                    },
                    required=["refactor_title", "reason", "example"]
                ),
                description="Array of refactoring suggestions with examples."
            )
        },
        required=["Style_And_Readability", "Maintainability", "Complexity_Analysis", "Security_Review", "Suggested_Refactors"]
    )

# --- Missing Prompt Creation Functions ---
def create_analyzer_prompt(question, expected_output, candidate_output, candidate_code):
    """Creates the detailed prompt for Gemini's analysis."""
    SYSTEM_INSTRUCTION = "You are an expert Code Analyzer. Strictly penalize code that hardcodes output or uses excessive print statements instead of correct function logic. Return only JSON."
    
    prompt_body = f"""
    ### SCORING TASK
    Analyze the Candidate Code and assign scores out of 100 based on Logic (40), Output (40), and Structure (20).

    **Original Question:** {question}
    **Expected Output:** {expected_output}
    **Candidate Output:** {candidate_output}
    **Candidate Code:** ```python\n{candidate_code}\n```
    """
    return SYSTEM_INSTRUCTION + prompt_body

def create_code_review_prompt(question, expected_output, candidate_output, candidate_code):
    """Creates the prompt for a detailed AI code review (senior engineer perspective)."""
    SYSTEM_INSTRUCTION = "You are a senior code reviewer with 10+ years of experience. Provide honest, constructive feedback on code quality, security, and best practices. Return only JSON."
    
    prompt_body = f"""
    ### AI CODE REVIEW (SENIOR ENGINEER PERSPECTIVE)
    Perform a comprehensive code review analyzing:
    1. Style & Readability: Naming conventions, formatting, documentation, clarity
    2. Maintainability: Code reusability, modularity, adherence to best practices
    3. Complexity Analysis: Time and space complexity with Big-O notation and natural-language reasoning
    4. Security: Vulnerability detection, input validation, safe practices
    5. Suggested Refactors: Concrete improvements with code examples

    **Original Question:** {question}
    **Expected Output:** {expected_output}
    **Candidate Output:** {candidate_output}
    **Candidate Code:** ```python\n{candidate_code}\n```
    """
    return SYSTEM_INSTRUCTION + prompt_body

# --- AI ANALYSIS AND REVIEW FUNCTIONS ---
async def _call_with_retries(submission: Submission) -> dict:
    """Call analyze_single_submission in a thread, retrying on transient quota/service errors."""
    attempt = 0
    backoff = INITIAL_BACKOFF
    while True:
        try:
            result = await asyncio.to_thread(analyze_single_submission, submission)
            return result
        except Exception as e:
            text = str(e)
            attempt += 1
            is_retryable = (
                'RESOURCE_EXHAUSTED' in text or 
                '429' in text or 
                '503' in text or 
                'rate limit' in text.lower() or 
                'overloaded' in text.lower() or 
                'UNAVAILABLE' in text
            )
            if attempt > MAX_RETRIES:
                logger.error(f"Max retries ({MAX_RETRIES}) exceeded for {submission.candidate_id}. Error: {text}")
                raise
            if is_retryable:
                logger.warning(f"Attempt {attempt}/{MAX_RETRIES}: Retryable error for {submission.candidate_id}. Backing off {backoff}s...")
                await asyncio.sleep(backoff)
                backoff = min(backoff * 2, MAX_BACKOFF)
                continue
            logger.error(f"Non-retryable error for {submission.candidate_id}: {text}")
            raise

async def _call_code_review_with_retries(submission: Submission) -> dict:
    """Call perform_code_review in a thread, retrying on transient quota/service errors."""
    attempt = 0
    backoff = INITIAL_BACKOFF
    while True:
        try:
            result = await asyncio.to_thread(perform_code_review, submission)
            return result
        except Exception as e:
            text = str(e)
            attempt += 1
            is_retryable = (
                'RESOURCE_EXHAUSTED' in text or 
                '429' in text or 
                '503' in text or 
                'rate limit' in text.lower() or 
                'overloaded' in text.lower() or 
                'UNAVAILABLE' in text
            )
            if attempt > MAX_RETRIES:
                logger.error(f"Max retries ({MAX_RETRIES}) exceeded for code review of {submission.candidate_id}. Error: {text}")
                raise
            if is_retryable:
                logger.warning(f"Attempt {attempt}/{MAX_RETRIES}: Retryable error in code review for {submission.candidate_id}. Backing off {backoff}s...")
                await asyncio.sleep(backoff)
                backoff = min(backoff * 2, MAX_BACKOFF)
                continue
            logger.error(f"Non-retryable error in code review for {submission.candidate_id}: {text}")
            raise

def analyze_single_submission(submission: Submission) -> dict:
    """The core logic to call the Gemini API for a single submission."""
    prompt = create_analyzer_prompt(
        submission.question, 
        submission.expected_output, 
        submission.candidate_output, 
        submission.candidate_code
    )
    
    response = client.models.generate_content(
        model=MODEL_ID,
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": get_analysis_schema()
        }
    )
    
    return json.loads(response.text)

def perform_code_review(submission: Submission) -> dict:
    """Call Gemini API for AI code review (senior engineer perspective)."""
    prompt = create_code_review_prompt(
        submission.question,
        submission.expected_output,
        submission.candidate_output,
        submission.candidate_code
    )
    
    response = client.models.generate_content(
        model=MODEL_ID,
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": get_code_review_schema()
        }
    )
    
    return json.loads(response.text)

@app.post("/analyze-batch/", response_model=List[AnalysisResult])
async def analyze_batch(submissions: List[Submission]):
    """Receives a list of code submissions, processes them in parallel and returns a list of analysis results."""
    results: List[AnalysisResult] = []
    
    for submission in submissions:
        try:
            gemini_output = await _call_with_retries(submission)
            code_review_output = await _call_code_review_with_retries(submission)
            
            result = AnalysisResult(
                candidate_id=submission.candidate_id,
                total_score=gemini_output.get('Total_Score'),
                improvements_suggested=gemini_output.get('Improvements_Suggested', 'N/A'),
                detailed_analysis=gemini_output.get('Detailed_Analysis', 'N/A'),
                code_review=code_review_output
            )
            results.append(result)

        except Exception as e:
            error_text = str(e)
            logger.error(f"Failed to analyze submission {submission.candidate_id}: {error_text}")
            results.append(AnalysisResult(
                candidate_id=submission.candidate_id,
                total_score=None,
                improvements_suggested="Could not complete analysis. The API service is currently unavailable. Please try again in a few moments.",
                detailed_analysis=f"Processing Error: {type(e).__name__} - Service Temporarily Unavailable. Please retry the submission.",
                code_review=None,
                error=error_text
            ))
        await asyncio.sleep(RATE_LIMIT_DELAY_SECONDS)

    return results
