
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from report_generator import generate_pdf_report
from database_service import save_report, get_report, get_candidate_reports, get_all_reports, init_database
from db import test_connection
import glob
from typing import Optional
import uuid, os, json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Online Test Report API")

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database on application startup."""
    logger.info("Application starting up...")
    db_available = test_connection()
    if db_available:
        logger.info("Database connection successful.")
        init_database()
    else:
        logger.warning("Database not configured or connection failed. Reports will not be saved to database.")
    logger.info("Application ready.")

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
    """Generate and save a PDF report, optionally storing it in the database."""
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
        
        # Generate PDF
        generate_pdf_report(data_dict, path)
        
        # Check if file was created
        if not os.path.exists(path):
            raise HTTPException(status_code=500, detail="PDF file was not created")
        
        # Get file size
        pdf_size = os.path.getsize(path)
        
        # Save report to database (optional - won't fail if DB not available)
        report_id = save_report(
            candidate_data=data_dict.get('candidate', {}),
            mcq_data=data_dict.get('mcq', {}),
            coding_data=data_dict.get('coding', {}),
            proctoring_data=data_dict.get('proctoring'),
            full_report_data=data_dict,
            pdf_file_path=path,
            pdf_file_size=pdf_size
        )
        
        logger.info(f"Report generated and {'saved to database' if report_id else 'stored as PDF only'}: {fname}")
            
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_detail = f"Error generating PDF: {str(e)}\n{traceback.format_exc()}"
        logger.error(error_detail)
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
        with open("static_sample.json", "r", encoding="utf-8") as f:
            sample = json.load(f)
        return JSONResponse(sample)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Sample data not found")
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Invalid JSON in sample file")


@app.get("/api/report/{report_id}")
async def get_report_by_id(report_id: str):
    """Retrieve a report from the database by ID."""
    report = get_report(report_id)
    if not report:
        raise HTTPException(status_code=404, detail=f"Report {report_id} not found")
    return JSONResponse(report)


@app.get("/api/reports/candidate/{candidate_email}")
async def get_reports_for_candidate(candidate_email: str, limit: int = 10, offset: int = 0):
    """Retrieve all reports for a specific candidate by email."""
    reports = get_candidate_reports(candidate_email, limit=limit, offset=offset)
    return JSONResponse({"candidate_email": candidate_email, "reports": reports, "count": len(reports)})


@app.get("/api/reports")
async def get_all_reports_endpoint(limit: int = 100, offset: int = 0):
    """Retrieve all reports from the database."""
    reports = get_all_reports(limit=limit, offset=offset)
    return JSONResponse({"reports": reports, "count": len(reports), "limit": limit, "offset": offset})


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
