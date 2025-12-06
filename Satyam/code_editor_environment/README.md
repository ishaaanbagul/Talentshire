# CodePlay - Code Execution Playground

A web-based code editor and execution platform where users write code and the backend compiles/executes it.

**Architecture:** Monolithic (FastAPI backend + React frontend)

**Supported Languages:** 
- ✅ Python 3.11
- ✅ Java (OpenJDK)
- ✅ SQL (SQLite)

**Execution Engine:** Direct subprocess (no external compiler service)

---

## Quick Start (Any OS with Docker)

### Prerequisites
- **Docker Desktop** (Windows/Mac) or Docker Engine (Linux)
- **Docker Compose** (included with Docker Desktop)
- No need to install Python, Java, or any compilers!

### Step 1: Get the Project

Clone or download the project:
```bash
git clone <your-repo-url>
cd new_project
```

Or if you have the ZIP file:
```bash
unzip new_project.zip
cd new_project
```

### Step 2: Start All Services

```bash
docker compose up -d
```

This will:
- Build the frontend (React + Vite) image
- Build the backend (FastAPI with Java, Python, SQLite) image
- Start all services in Docker containers
- Expose frontend at `http://localhost:3000`
- Expose backend at `http://localhost:8000` (internal use)

### Step 3: Access the Application

Open your browser and go to:
```
http://localhost:3000
```

### Step 4: Stop Services

```bash
docker compose down
```

To stop and remove all containers/volumes:
```bash
docker compose down -v
```

---

## Usage

1. **Select Language**: Choose Python, Java, or SQL from the dropdown
2. **Write Code**: Use the Monaco editor (syntax highlighting per language)
3. **Provide Input**: (Optional) Enter stdin values in the Input textarea
4. **Run Code**: Click "Run Code" button
5. **View Output**: Results appear in the Output console

### Example Programs

**Python:**
```python
x = int(input())
y = int(input())
print(x + y)
```
Input: `5` and `3` → Output: `8`

**Java:**
```java
import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int a = sc.nextInt();
        int b = sc.nextInt();
        System.out.println(a + b);
    }
}
```
Input: `5` and `3` → Output: `8`

**SQL:**
```sql
CREATE TABLE users (id INT, name TEXT);
INSERT INTO users VALUES (1, 'Alice'), (2, 'Bob');
SELECT * FROM users;
```
Output:
```
id|name
1|Alice
2|Bob
```

---

## Project Structure

```
new_project/
├── frontend/                    # React + Vite application
│   ├── src/
│   │   ├── components/
│   │   │   └── EditorPanel.jsx # Main code editor UI
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── index.css
│   ├── package.json
│   ├── Dockerfile               # Multi-stage: Node build + Nginx serve
│   └── nginx.conf
│
├── backend/                     # FastAPI application
│   ├── main.py                  # API endpoints (/question, /run)
│   ├── requirements.txt          # Python dependencies
│   └── Dockerfile               # Python 3.11 + Java + build tools
│
├── docker-compose.yml           # Orchestration config
├── README.md                    # This file
└── LINUX_SETUP.md              # Legacy: Linux deployment guide
```

---

## API Endpoints

### GET `/question`
Returns a sample coding question (for testing)

Response:
```json
{
  "id": "1",
  "title": "Sum Two Numbers",
  "body": "Given two integers, print their sum",
  "sample_input": "3 5",
  "sample_output": "8",
  "constraints": "-10^9 <= a,b <= 10^9",
  "difficulty": "Easy"
}
```

### POST `/run`
Execute code and return output

Request:
```json
{
  "language": "python",
  "version": null,
  "files": [
    {
      "name": "main",
      "content": "print(2+2)"
    }
  ],
  "stdin": ""
}
```

Response:
```json
{
  "run": {
    "stdout": "4\n",
    "stderr": "",
    "output": "4\n",
    "code": 0
  }
}
```

---

## Troubleshooting

### Port Already in Use
If port 3000 or 8000 is already in use, stop conflicting services:

```bash
# Windows: Find and kill process on port 3000
netstat -ano | findstr :3000
taskkill /PID <PID> /F

# Linux/Mac:
lsof -ti:3000 | xargs kill -9
```

Then start docker compose again.

### Docker Issues
```bash
# View container logs
docker logs codeplay-backend
docker logs codeplay-frontend

# Check running containers
docker ps

# Rebuild without cache
docker compose up -d --build --no-cache

# Clean up (WARNING: removes all Docker data)
docker system prune -a
```

### Code Execution Timeouts
- Python/Java: 10 second timeout
- SQL: In-memory SQLite (immediate)

If code takes longer, optimize your solution.

---

## Development

### Local Setup (Without Docker)

**Frontend:**
```bash
cd frontend
npm install --legacy-peer-deps
npm run dev
# Runs on http://localhost:5173
```

**Backend:**
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Modify Code

1. Edit source files (e.g., `backend/main.py`, `frontend/src/components/EditorPanel.jsx`)
2. Restart Docker or dev server to see changes

### Rebuild Docker Images

```bash
docker compose up -d --build
```

---

## Performance Notes

- First execution of a language takes slightly longer (runtime initialization)
- Subsequent executions are faster (cached)
- Python/Java are executed as separate processes for security
- SQL uses in-memory SQLite for isolation

---

## License

Open source - feel free to modify and distribute

---

## Support

For issues or questions:
1. Check Docker logs: `docker logs codeplay-backend`
2. Verify Docker is running: `docker ps`
3. Ensure ports 3000, 8000 are free
4. Try `docker compose down -v && docker compose up -d`

1. **Left panel** shows the problem statement (title, description, sample input/output)
2. **Right panel:**
   - Select language: Python, Java, or SQL
   - Write code in Monaco editor
   - Enter input (stdin) if needed
   - Click "▶ Run Code"
3. **Below editor:** See output/errors from Piston

**Example Python code:**
```python
x = int(input("Enter number 1: "))
y = int(input("Enter number 2: "))
print(x + y)
```

Input: `3` and `5` → Output: `8`

---

## Architecture Overview

```
┌─────────────┐
│   Browser   │ (User)
│ localhost:3000
└──────┬──────┘
       │ HTTP
       ▼
┌─────────────────────┐
│ Frontend (Nginx)    │
│ React + Monaco      │
│ port 3000           │
└──────┬──────────────┘
       │ /api/* proxied to backend
       ▼
┌──────────────────────┐
│ Backend (FastAPI)    │
│ port 8000            │
│ - GET /question      │
│ - POST /run          │
└──────┬───────────────┘
       │ httpx client
       ▼
┌──────────────────────┐
│ Piston               │
│ (Code Compiler)      │
│ port 8080            │
│ - /api/v2/execute    │
│ - /api/v2/runtimes   │
└──────────────────────┘
```

---

## File Structure

```
codeplay/
├── docker-compose.yml          # Orchestrates all services
├── README.md                    # This file
├── .gitignore
│
├── backend/
│   ├── main.py                 # FastAPI app (GET /question, POST /run)
│   ├── requirements.txt         # Python dependencies
│   ├── Dockerfile              # Backend container image
│   └── .dockerignore
│
└── frontend/
    ├── package.json            # Node.js dependencies
    ├── vite.config.js          # Vite config
    ├── index.html              # HTML entry
    ├── Dockerfile              # Multi-stage build (Node build → Nginx serve)
    ├── nginx.conf              # Nginx config (proxies /api to backend)
    ├── .dockerignore
    └── src/
        ├── main.jsx            # React entry
        ├── App.jsx             # Main app
        ├── styles.css          # Styles
        └── components/
            ├── QuestionPanel.jsx  # Left panel (problem statement)
            └── EditorPanel.jsx    # Right panel (editor + run + output)
```

---

## API Endpoints

### GET /question
Returns a dummy problem statement:
```json
{
  "id": "1",
  "title": "Sum Two Numbers",
  "body": "Given two integers, print their sum.",
  "sample_input": "3 5",
  "sample_output": "8",
  "constraints": "-10^9 <= a,b <= 10^9",
  "difficulty": "Easy"
}
```

### POST /run
Execute code via Piston.

**Request:**
```json
{
  "language": "python",
  "version": null,
  "files": [
    {"name": "main", "content": "print(3 + 5)"}
  ],
  "stdin": ""
}
```

**Response:**
```json
{
  "run": {
    "stdout": "8\n",
    "stderr": "",
    "output": "8\n",
    "code": 0
  }
}
```

---

## Management Commands

### Check Service Status
```bash
docker compose ps
```

### View Logs
```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f piston
docker compose logs -f codeplay-backend
docker compose logs -f codeplay-frontend
```

### Stop Services
```bash
docker compose stop
```

### Restart Services
```bash
docker compose restart
```

### Rebuild & Restart
```bash
docker compose down
docker compose up --build -d
```

### Check Piston Health
```bash
curl http://localhost:8080/api/v2/runtimes | jq '. | length'
# Should return: 40+ (number of languages supported)
```

---

## Troubleshooting

### Issue: "Piston connection error"
**Cause:** Piston container is not running or not healthy.

**Solution:**
```bash
docker compose restart piston
docker logs piston
```

Wait 10 seconds after restart for Piston to initialize.

### Issue: "Backend cannot reach frontend"
**Cause:** Frontend/backend containers are not on the same Docker network.

**Solution:**
```bash
docker compose down
docker compose up --build -d
```

### Issue: "Port 3000 already in use"
**Solution:**
```bash
# Find container using port 3000
docker ps | grep 3000

# Kill the container
docker stop <container-id>

# Or use a different port in docker-compose.yml
# Change "3000:80" to "3001:80"
```

---

## Environment Variables

### Backend
- `PISTON_URL` (default: `http://piston:8080`) — URL of Piston service

Set in `docker-compose.yml`:
```yaml
backend:
  environment:
    - PISTON_URL=http://piston:8080
```

---

## Future Enhancements

1. **Database Integration** — Replace dummy `/question` with MongoDB queries
2. **Code Generation Service** — Auto-generate problems
3. **Microservices Split** — Separate Question Service, Execution Service, API Gateway
4. **User Authentication** — Login/submission history
5. **Code Submission Storage** — Save candidate submissions

---

## License

MIT (or your choice)

