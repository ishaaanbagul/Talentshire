# code-analyzer-service/schemas.py
from pydantic import BaseModel, Field
from typing import List, Optional

# --- Input Model (The data sent by the user/website) ---
class Submission(BaseModel):
    """Defines the input structure for a single code analysis request."""
    candidate_id: str = Field(..., description="Unique ID for the submission.")
    question: str = Field(..., description="The original programming question.")
    expected_output: str = Field(..., description="The known correct output.")
    candidate_output: str = Field(..., description="The output produced by the candidate code.")
    candidate_code: str = Field(..., description="The candidate's source code.")

    # Example data for the FastAPI documentation
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "candidate_id": "CAND_001",
                    "question": "Write a Python function to sum integers from 1 to n using a loop.",
                    "expected_output": "55",
                    "candidate_output": "55",
                    "candidate_code": "def sum_first_n_integers(n):\n    total = 0\n    for i in range(1, n + 1):\n        total += i\n    return total\nprint(sum_first_n_integers(10))"
                }
            ]
        }
    }


# --- Output Model (The required response for a single candidate) ---
class AnalysisResult(BaseModel):
    """Defines the structure of the analysis returned to the user."""
    candidate_id: str
    total_score: Optional[int] = Field(None, description="Final score out of 100.")
    improvements_suggested: str = Field(..., description="Actionable feedback for the developer.")
    detailed_analysis: str = Field(..., description="Comprehensive review of logic, structure, and output comparison.")
    error: Optional[str] = Field(None, description="Error message if processing failed for this candidate.")