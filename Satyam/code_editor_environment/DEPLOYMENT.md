# Deployment Guide

## For Sharing with Others

### What's Included
- ✅ `docker-compose.yml` - Orchestration config
- ✅ `backend/` - FastAPI backend with Java, Python, SQL support
- ✅ `frontend/` - React + Vite frontend
- ✅ All Dockerfiles for containerization
- ✅ Dependencies (package.json, requirements.txt)

### What's NOT Included (by design)
- ❌ `node_modules/` (will be installed during Docker build)
- ❌ `__pycache__/` (Python cache, not needed)
- ❌ `dist/` folders (will be built in Docker)

---

## Deployment Steps (Same on Any PC)

### 1. Extract the ZIP
```bash
unzip new_project.zip
cd new_project
```

### 2. Ensure Docker is Installed
```bash
docker --version
docker compose --version
```

If not installed:
- **Windows/Mac**: Download [Docker Desktop](https://www.docker.com/products/docker-desktop)
- **Linux**: Follow [Docker installation guide](https://docs.docker.com/engine/install/)

### 3. Start the Application
```bash
docker compose up -d
```

Wait 30-60 seconds for images to build and services to start.

### 4. Verify Services Are Running
```bash
docker ps
```

You should see 5 containers:
- `codeplay-frontend` (Nginx)
- `codeplay-backend` (FastAPI)
- `judge0` (optional, not used in current version)
- `judge0-postgres` (optional)
- `judge0-redis` (optional)

### 5. Access the Application
Open browser: **http://localhost:3000**

---

## Environment Variables (Optional)

Create a `.env` file if you need custom settings:

```env
# Backend
FASTAPI_ENV=production

# Database (not currently used)
DB_URL=sqlite:///./test.db
```

Then restart:
```bash
docker compose down
docker compose up -d
```

---

## Cross-Platform Compatibility

✅ **Windows (with Docker Desktop)** - Fully supported
✅ **macOS (with Docker Desktop)** - Fully supported  
✅ **Linux (with Docker Engine)** - Fully supported
✅ **Server/VM (any OS)** - Fully supported

**The only requirement: Docker!**

---

## Troubleshooting During Deployment

### Issue: "docker: command not found"
**Solution**: Install Docker Desktop or Docker Engine

### Issue: "Port 3000 already in use"
**Solution**: 
```bash
# Kill existing service on port 3000
# Windows:
netstat -ano | findstr :3000
taskkill /PID <PID> /F

# Linux/Mac:
lsof -ti:3000 | xargs kill -9
```

### Issue: "Cannot connect to Docker daemon"
**Solution**: Start Docker Desktop or Docker service

### Issue: Slow first startup
**Reason**: Docker is building images (1-2 minutes normal)
**Solution**: Be patient, grab coffee ☕

### Issue: Code execution errors
**Solution**: Check backend logs
```bash
docker logs codeplay-backend -f
```

---

## Performance Tips

1. **First run is slow**: Docker builds images (~2 min)
2. **Subsequent runs are fast**: Cached images (~5 sec)
3. **First code execution slow**: Runtime initialization
4. **Later executions fast**: Runtime is cached

---

## Customization

To modify the application:

1. Edit source files (e.g., `backend/main.py`, `frontend/src/App.jsx`)
2. Rebuild containers:
   ```bash
   docker compose up -d --build
   ```
3. Changes should reflect immediately

---

## Cleanup

To remove everything and start fresh:

```bash
# Stop containers
docker compose down

# Remove containers + volumes
docker compose down -v

# Remove images
docker rmi new_project-frontend new_project-backend

# Remove all unused Docker data
docker system prune -a
```

---

## System Requirements

| Aspect | Minimum | Recommended |
|--------|---------|-------------|
| **Disk Space** | 4 GB | 10 GB |
| **RAM** | 2 GB | 4 GB |
| **CPU** | 1 core | 2+ cores |
| **Internet** | Required (first run) | For Docker image downloads |

First run downloads ~1.5 GB of Docker images.

---

## Security Notes

⚠️ **This is a development/testing tool**
- Code execution is not sandboxed (use in trusted environments)
- No authentication is implemented
- No rate limiting

For production use, add:
- User authentication
- Code execution sandboxing/limits
- Input validation
- Rate limiting

---

## Support Resources

- **Docker Issues**: [Docker Docs](https://docs.docker.com/)
- **FastAPI**: [FastAPI Docs](https://fastapi.tiangolo.com/)
- **React**: [React Docs](https://react.dev/)

---

**Happy coding!** 🚀
