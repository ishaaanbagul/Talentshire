PostgreSQL Integration (Windows / Cross-platform)
===============================================

This file explains how to configure a PostgreSQL connection for the backend in a cross-platform way (works on macOS and Windows).

1) Install dependencies

On the office Windows machine, create a Python virtual environment and install backend requirements:

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

2) Set environment variables

You can either set a single `DATABASE_URL` environment variable, or provide components:

- `DATABASE_URL` example:
  `postgresql+psycopg2://user:password@host:5432/dbname`

- Or set individual variables (Windows PowerShell):
  ```powershell
  $env:PGUSER = 'user'
  $env:PGPASSWORD = 'password'
  $env:PGHOST = 'localhost'
  $env:PGPORT = '5432'
  $env:PGDATABASE = 'dbname'
  ```

3) Test the connection

From the `backend/` folder you can run a tiny check (Python REPL):

```bash
python -c "from db import test_connection; print('OK' if test_connection() else 'NO')"
```

Notes:
- If no DB environment variables are set, the application will continue to work exactly as before: PDF generation and the web UI will NOT change. The `db.get_session()` context manager yields `None` when DB is not configured, so you can add DB code later without breaking existing behavior.
- On Windows, prefer using `psycopg2-binary` from `requirements.txt` to avoid compiling C extensions.
