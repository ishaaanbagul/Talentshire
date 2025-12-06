# CodePlay - Quick Reference

## One-Liner Start

```bash
docker compose up -d && echo "Visit http://localhost:3000"
```

## Project Summary

**Status**: ✅ Production Ready

**What Works**:
- ✅ Python code execution
- ✅ Java code compilation & execution
- ✅ SQL query execution
- ✅ Syntax highlighting per language
- ✅ Standard input/output handling
- ✅ Error messages displayed
- ✅ Containerized (works anywhere with Docker)

**Technology Stack**:
- Frontend: React + Vite + Monaco Editor + Nginx
- Backend: FastAPI + Python 3.11 + Java + SQLite
- Deployment: Docker + Docker Compose
- Execution: Direct subprocess (Python, Java, SQL)

---

## File Structure (Essential)

```
new_project/
├── docker-compose.yml       ← Main config (run this!)
├── README.md               ← Full documentation
├── DEPLOYMENT.md          ← Sharing & setup guide
│
├── backend/
│   ├── main.py           ← API code
│   ├── requirements.txt   ← Python deps
│   └── Dockerfile        ← Backend container
│
└── frontend/
    ├── src/              ← React components
    ├── package.json      ← NPM deps
    ├── vite.config.js    ← Build config
    ├── Dockerfile        ← Frontend container
    └── nginx.conf        ← Web server config
```

---

## Key Commands

| Command | Purpose |
|---------|---------|
| `docker compose up -d` | Start everything |
| `docker compose down` | Stop everything |
| `docker compose logs codeplay-backend` | View backend logs |
| `docker ps` | List running containers |
| `docker compose up -d --build` | Rebuild & start |
| `docker system prune -a` | Clean up everything |

---

## API Reference

**Base URL**: `http://localhost:8000`

### POST /run
Execute code

```bash
curl -X POST http://localhost:8000/run \
  -H "Content-Type: application/json" \
  -d '{
    "language": "python",
    "files": [{"name": "main", "content": "print(5+3)"}],
    "stdin": ""
  }'
```

Response:
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

### GET /question
Get sample question

```bash
curl http://localhost:8000/question
```

---

## Sharing the Project

### Create ZIP for Distribution

```bash
# Windows PowerShell
Compress-Archive -Path new_project -DestinationPath new_project.zip

# Or via web: Upload to Drive/GitHub/Any file service
```

### Recipient Setup

```bash
# Extract
unzip new_project.zip
cd new_project

# Run (that's it!)
docker compose up -d

# Access
# Open http://localhost:3000 in browser
```

**No additional installations needed!**

---

## Common Issues & Fixes

| Issue | Fix |
|-------|-----|
| Port 3000 in use | Kill process: `netstat -ano \| findstr :3000` then `taskkill /PID <PID> /F` |
| Docker not found | Install Docker Desktop |
| Slow startup | Normal (first run builds images, ~2 min) |
| Code not executing | Check logs: `docker logs codeplay-backend` |
| Connection refused | Wait 30 seconds, services still starting |

---

## Next Steps / Enhancements

Potential improvements:
- Add authentication (login system)
- Add more languages (C++, JavaScript, etc.)
- Add problem storage (database)
- Add leaderboard / scoring
- Add code templates
- Add run history
- Add code diff/versioning
- Better error messages
- Timeout limits per language
- Memory/CPU limits

---

## Credits

Built with:
- FastAPI (backend framework)
- React + Vite (frontend)
- Monaco Editor (code editor)
- Docker (containerization)

---

**Last Updated**: Dec 6, 2025
**Version**: 1.0
**Status**: Production Ready ✅
