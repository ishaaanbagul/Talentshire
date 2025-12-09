
# Online Test Report Dashboard (FastAPI + React)

This project contains a professional-style report dashboard for an online test platform.
It includes:
- Donut charts (two colors only) showing percentage of marks for MCQ and Coding.
- Summary of correct/wrong MCQ, coding output status.
- Optional Proctoring section which can be toggled on/off by evaluator before downloading PDF.
- Backend API (FastAPI) that generates a PDF report using ReportLab.
- Frontend (React + Chart.js) that displays charts and candidate info, and can download the PDF.

## How to run (dev)
### Backend
```
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend (dev)
```
cd frontend
npm install
npm run dev
```
Open http://localhost:1234 (Parcel default) or check console for served port. The frontend expects backend on http://localhost:8000.

## Notes & Professional Improvements you can add later
- Use HTML->PDF renderer (wkhtmltopdf or WeasyPrint) for pixel-perfect reports.
- Store generated reports in object storage (S3) and return signed URLs for download.
- Add authentication and evaluator roles.
- Add audit logs and tamper-proofing for proctoring data.
- Add unit tests and CI pipeline, containerize with Docker for reproducible deployments.
