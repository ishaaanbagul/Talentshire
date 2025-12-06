# code-analyzer-service/main.py
import os
import json
from typing import List
from fastapi import FastAPI, HTTPException
from pydantic import ValidationError
from dotenv import load_dotenv

from google import genai
from google.genai import types

from schemas import Submission, AnalysisResult # Import our Pydantic schemas

# Load environment variables (like GEMINI_API_KEY) from .env file
load_dotenv() 

# --- CONFIGURATION ---
MODEL_ID = 'gemini-2.5-pro' 
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

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
    description="Analyzes code submissions using Gemini-Pro for logic, structure, and correctness.",
    version="1.0.0"
)

# --- GEMINI SCORING UTILITIES (Copied/Adapted from your Colab work) ---

def get_analysis_schema():
    """Defines the structure for the desired JSON output for Gemini's response."""
    # (Simplified for brevity, assuming the full schema from the previous response is here)
    return types.Schema(
        type=types.Type.OBJECT,
        properties={
            "Total_Score": types.Schema(type=types.Type.INTEGER, description="The final aggregate score out of 100."),
            "Improvements_Suggested": types.Schema(type=types.Type.STRING, description="Specific, actionable steps to improve the code."),
            # Include all other required fields like Code_Logic_Score, Detailed_Analysis, etc.
            "Detailed_Analysis": types.Schema(type=types.Type.STRING, description="A comprehensive paragraph explaining the overall strengths and weaknesses.")
        },
        required=["Total_Score", "Improvements_Suggested", "Detailed_Analysis"]
    )


def create_analyzer_prompt(question, expected_output, candidate_output, candidate_code):
    """Creates the detailed prompt with System Instructions."""
    # (Full prompt logic from previous steps goes here)
    # Ensure this strictly guides the model to act as a reviewer and penalize print abuse.
    SYSTEM_INSTRUCTION = "You are an expert Code Analyzer. Strictly penalize code that hardcodes output or uses excessive print statements instead of correct function logic. Return only JSON."
    
    prompt_body = f"""
    ### SCORING TASK
    Analyze the Candidate Code and assign scores out of 100 based on Logic (40), Output (40), and Structure (20).

    [... include the detailed criteria and data sections ...]
    
    **Original Question:** {question}
    **Expected Output:** {expected_output}
    **Candidate Code:** ```python\n{candidate_code}\n```
    """
    return SYSTEM_INSTRUCTION + prompt_body


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
    
    # The response.text is guaranteed to be JSON due to the config
    return json.loads(response.text)


# --- FASTAPI ENDPOINT ---

@app.post(
    "/analyze-batch/", 
    response_model=List[AnalysisResult],
    summary="Analyzes a batch of code submissions.",
)
async def analyze_batch(submissions: List[Submission]):
    """
    Receives a list of code submissions, processes them in parallel 
    (or synchronously in this simple version), and returns a list of analysis results.
    """
    results: List[AnalysisResult] = []
    
    for submission in submissions:
        try:
            # Call the core analysis logic
            gemini_output = analyze_single_submission(submission)
            
            # Map the detailed Gemini output (dict) to the required Pydantic output schema
            # We explicitly pull the required fields for the final response
            result = AnalysisResult(
                candidate_id=submission.candidate_id,
                total_score=gemini_output.get('Total_Score'),
                improvements_suggested=gemini_output.get('Improvements_Suggested', 'N/A'),
                detailed_analysis=gemini_output.get('Detailed_Analysis', 'N/A')
            )
            results.append(result)
            
        except (json.JSONDecodeError, KeyError, types.StopCandidateException, Exception) as e:
            # Handle potential errors from the API call or parsing
            results.append(AnalysisResult(
                candidate_id=submission.candidate_id,
                total_score=None,
                improvements_suggested="Could not complete analysis due to an internal error.",
                detailed_analysis=f"Processing Error: {type(e).__name__} - {str(e)}",
                error=str(e)
            ))
            # In a production service, you might log this error rather than returning it directly

    return results