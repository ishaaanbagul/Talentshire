# Database Integration Guide

## Overview

The Online Test Report Dashboard now includes automatic database support for storing examination reports. Reports are:
- ✓ Always generated as PDF files (local storage)
- ✓ Optionally saved to PostgreSQL database
- ✓ Queryable through new API endpoints (when database is configured)

The database is **optional** - if not configured, the system works exactly as before with PDF-only output.

## Quick Start

### 1. Install Dependencies

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Database (Optional)

Set ONE of these environment variables:

**Option A: Single URL variable (recommended)**
```powershell
$env:DATABASE_URL = "postgresql+psycopg2://user:password@localhost:5432/reportdb"
```

**Option B: Individual component variables**
```powershell
$env:PGUSER = "report_user"
$env:PGPASSWORD = "your_password"
$env:PGHOST = "localhost"
$env:PGPORT = "5432"
$env:PGDATABASE = "reportdb"
```

### 3. Initialize Database

```bash
python setup_database.py
```

This will:
- ✓ Test database connection
- ✓ Create schema and tables
- ✓ Show current statistics

### 4. Start Backend

```bash
python main.py
```

## Database Setup Options

### PostgreSQL on Windows (Local)

1. **Download & Install PostgreSQL**
   - https://www.postgresql.org/download/windows/
   - Remember the superuser password

2. **Create Database & User**
   ```sql
   -- Using pgAdmin or psql
   CREATE USER report_user WITH PASSWORD 'secure_password';
   CREATE DATABASE reportdb OWNER report_user;
   ```

3. **Set Environment Variable**
   ```powershell
   $env:DATABASE_URL = "postgresql+psycopg2://report_user:secure_password@localhost:5432/reportdb"
   ```

### PostgreSQL with Docker

```bash
docker run --name test_report_db \
  -e POSTGRES_USER=report_user \
  -e POSTGRES_PASSWORD=secure_password \
  -e POSTGRES_DB=reportdb \
  -p 5432:5432 \
  -d postgres:15
```

Then set `DATABASE_URL` as above.

### Cloud Database (AWS RDS, Azure, Google Cloud)

1. Create PostgreSQL instance
2. Get connection string from provider
3. Set `DATABASE_URL`:
   ```powershell
   $env:DATABASE_URL = "postgresql+psycopg2://user:pass@aws-host:5432/db"
   ```

## Files Changed/Added

### New Files:
- **`models.py`** - SQLAlchemy ORM model for `ExaminationReport`
- **`database_service.py`** - Database operations (save, retrieve, query)
- **`setup_database.py`** - Database initialization and testing
- **`DATABASE_INTEGRATION.md`** - Detailed documentation

### Updated Files:
- **`main.py`** - Integrated database saving into report generation
- **`requirements.txt`** - Already includes `sqlalchemy` and `psycopg2-binary`

## API Endpoints

### Generate & Save Report (Enhanced)
```
POST /api/report
```
- Generates PDF (same as before)
- Saves to database if configured
- Returns PDF file

### Get Report by ID
```
GET /api/report/{report_id}
```
Returns JSON report data from database.

### Get Reports for Candidate
```
GET /api/reports/candidate/{email}?limit=10&offset=0
```
Returns all reports for a candidate.

### Get All Reports
```
GET /api/reports?limit=100&offset=0
```
Returns paginated list of all reports.

## Database Schema

### `examination_reports` Table

```sql
- id (UUID, PRIMARY KEY)
- candidate_id (String, indexed)
- candidate_name (String)
- candidate_email (String, indexed)
- created_at (DateTime, indexed)
- updated_at (DateTime)
- mcq_marks_obtained (Float)
- mcq_max_marks (Float)
- mcq_percentage (Float)
- coding_marks_obtained (Float)
- coding_max_marks (Float)
- coding_percentage (Float)
- coding_attempt_count (Integer)
- coding_total_count (Integer)
- proctoring_compliance (Float)
- proctoring_focus_deviation (Float)
- full_report_data (JSON - complete report backup)
- pdf_file_path (String)
- pdf_file_size (Integer)
- status (String)
- notes (Text)
```

## Testing

### Test Connection Only
```bash
python -c "from db import test_connection; print('Connected!' if test_connection() else 'Failed')"
```

### Initialize and Test
```bash
python setup_database.py
```

### Verify from Python REPL
```python
from database_service import get_all_reports
reports = get_all_reports(limit=5)
print(f"Found {len(reports)} reports")
```

## Troubleshooting

### "Database not configured"
- Set `DATABASE_URL` or individual PG_* variables
- Restart the application

### "Connection refused"
- Check PostgreSQL is running: `pg_isready -h localhost`
- Verify host, port, credentials

### "Permission denied"
- Verify user has CREATE TABLE permissions
- Check database ownership

### "No such module: psycopg2"
- Run: `pip install psycopg2-binary`

## Backward Compatibility

✓ If no database is configured:
  - System works exactly as before
  - PDFs still generated locally
  - No API changes
  - No errors or warnings

✓ If database fails but configured:
  - PDF still generated and returned
  - Database save error logged
  - Client unaffected

## Features

✅ Automatic schema initialization
✅ UUID primary keys for distributed systems
✅ Indexed queries for performance
✅ JSON backup of complete report
✅ Graceful degradation without database
✅ Optional proctoring data storage
✅ Pagination support for large datasets
✅ Candidate history tracking

## Environment Variables Reference

| Variable | Example | Purpose |
|----------|---------|---------|
| `DATABASE_URL` | `postgresql+psycopg2://user:pass@host:port/db` | Full connection string (takes precedence) |
| `PGUSER` | `report_user` | Username (if no DATABASE_URL) |
| `PGPASSWORD` | `secure_pwd` | Password |
| `PGHOST` | `localhost` | Server host |
| `PGPORT` | `5432` | Server port |
| `PGDATABASE` | `reportdb` | Database name |

## Next Steps

1. Set `DATABASE_URL` environment variable
2. Run `python setup_database.py`
3. Start `python main.py`
4. Test with: `curl http://localhost:8000/api/reports`

---

**Status:** ✅ Complete and tested
**Version:** 1.0.0
**Last Updated:** December 9, 2025

