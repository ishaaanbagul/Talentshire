
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from report_generator import generate_pdf_report
import glob
from typing import Optional
import uuid, os, json

app = FastAPI(title="Online Test Report API")

# Add CORS middleware to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CandidateReport(BaseModel):
    candidate: dict
    mcq: dict
    coding: dict
    proctoring: Optional[dict] = None
    include_proctoring: Optional[bool] = True

@app.post("/api/report")
async def create_report(payload: CandidateReport):
    # payload validation handled by Pydantic
    out_dir = "reports"
    os.makedirs(out_dir, exist_ok=True)
    fname = f"report_{uuid.uuid4().hex}.pdf"
    path = os.path.join(out_dir, fname)
    try:
        # Convert Pydantic model to dict and ensure all required fields exist
        data_dict = payload.dict()
        # Ensure nested dictionaries exist
        if 'candidate' not in data_dict:
            data_dict['candidate'] = {}
        if 'mcq' not in data_dict:
            data_dict['mcq'] = {}
        if 'coding' not in data_dict:
            data_dict['coding'] = {}
        
        generate_pdf_report(data_dict, path)
        
        # Check if file was created
        if not os.path.exists(path):
            raise HTTPException(status_code=500, detail="PDF file was not created")
            
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_detail = f"Error generating PDF: {str(e)}\n{traceback.format_exc()}"
        raise HTTPException(status_code=500, detail=error_detail)
    
    candidate_name = payload.candidate.get('name', 'report') if payload.candidate else 'report'
    return FileResponse(
        path, 
        media_type="application/pdf", 
        filename=f"{candidate_name}.pdf"
    )

@app.get("/api/sample")
async def sample_data():
    try:
        with open("static_sample.json", "r") as f:
            sample = json.load(f)
        return JSONResponse(sample)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Sample data not found")
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Invalid JSON in sample file")


@app.get("/api/report/latest")
async def latest_report():
    """Return the most recently generated PDF report from the `reports/` folder."""
    out_dir = "reports"
    if not os.path.exists(out_dir):
        raise HTTPException(status_code=404, detail="No reports available")

    pdfs = sorted(glob.glob(os.path.join(out_dir, "*.pdf")), key=os.path.getmtime, reverse=True)
    if not pdfs:
        raise HTTPException(status_code=404, detail="No reports available")

    latest = pdfs[0]
    return FileResponse(latest, media_type="application/pdf", filename=os.path.basename(latest))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
