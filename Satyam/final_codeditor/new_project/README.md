# 🚀 CodePlay - Microservices Code Execution Platform

**Version 2.0 - Microservices Edition**  
**Status:** ✅ Production Ready  
**Last Updated:** December 7, 2025

---

## 🎯 What is CodePlay?

CodePlay is a production-ready code execution platform with **3 independent microservices**, supporting **4 programming languages** (Python, Java, SQL, PySpark), and built for easy team integration.

### Key Highlights
- ✅ **Microservices Architecture** - Independent, scalable services
- ✅ **4 Languages** - Python, Java, SQL, PySpark
- ✅ **Production Ready** - Docker, Health Checks, Monitoring
- ✅ **Smart Input Parsing** - Shows code input prompts in UI
- ✅ **MongoDB Integration** - With mock fallback
- ✅ **Complete Documentation** - Architecture, API, Deployment guides

---

## 🏗️ Architecture at a Glance

```
Frontend (React)
    ↓
    ├→ Execution Service (8001) - Python, Java, SQL, PySpark
    ├→ Problem Service (8002) - Problem data
    └→ Submission Service (8003) - Code storage
        ↓
    MongoDB (27017)
```

**5 Services Total:**
1. **Frontend** (Port 3000) - React UI with Monaco Editor
2. **Execution Service** (Port 8001) - Code execution engine
3. **Problem Service** (Port 8002) - Problem management
4. **Submission Service** (Port 8003) - Submission storage
5. **MongoDB** (Port 27017) - Data persistence

---

## ⚡ Quick Start (5 Minutes)

### Prerequisites
- Docker Desktop (Windows/Mac) or Docker (Linux)
- No need to install Python, Java, or any compilers!

### 1️⃣ Start Services

```bash
cd c:\Users\MSI\new_project
docker compose up -d --build
```

### 2️⃣ Verify Services Started

```bash
docker compose ps

# Should see 5 containers: frontend, execution-service, problem-service, 
# submission-service, mongodb - all "Up"
```

### 3️⃣ Health Checks

```bash
curl http://localhost:8001/health  # Execution Service
curl http://localhost:8002/health  # Problem Service
curl http://localhost:8003/health  # Submission Service
```

### 4️⃣ Access Frontend

Open browser: **http://localhost:3000**

### 5️⃣ Run Your First Test

```bash
# Automated testing (all 4 languages)
python test_microservices.py

# Or PowerShell
.\test_microservices.ps1
```

---

## 📚 Documentation Index

**START HERE:** [DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md) - Complete guide to all docs

| Document | Purpose |
|----------|---------|
| **[DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md)** | Complete index & navigation |
| [MICROSERVICES_ARCHITECTURE.md](MICROSERVICES_ARCHITECTURE.md) | System design & architecture |
| [API_REFERENCE.md](API_REFERENCE.md) | Complete API documentation |
| [QUICK_START_TESTING.md](QUICK_START_TESTING.md) | Testing procedures |
| [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) | Production deployment |
| [CUSTOMIZATION_GUIDE.md](CUSTOMIZATION_GUIDE.md) | Extending the platform |

---

## 🔧 Quick API Examples

### Execute Python

```bash
curl -X POST http://localhost:8001/run \
  -H "Content-Type: application/json" \
  -d '{
    "language": "python",
    "files": [{"name": "main", "content": "print(3+5)"}],
    "stdin": ""
  }'
```

**Response:**
```json
{
  "run": {
    "stdout": "8\n",
    "stderr": "",
    "output": "8\n",
    "code": 0
  },
  "status": "success",
  "language": "python"
}
```

### Fetch Problem

```bash
curl http://localhost:8002/problem/1
```

### Submit Code

```bash
curl -X POST http://localhost:8003/submission \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "student123",
    "problem_id": "1",
    "language": "python",
    "code": "print(3+5)"
  }'
```

See [API_REFERENCE.md](API_REFERENCE.md) for complete documentation.

---

## 🎯 Supported Languages

### Python 3.11
```python
x = int(input("Enter number: "))
print(x * 2)
```

### Java
```java
public class Main {
    public static void main(String[] args) {
        System.out.println(5 + 3);
    }
}
```

### SQL (SQLite3)
```sql
SELECT 1 + 2 as result;
```

### PySpark (NEW!)
```python
from pyspark.sql import SparkSession
spark = SparkSession.builder.appName("App").master("local[1]").getOrCreate()
df = spark.createDataFrame([(1, "Alice")], ["id", "name"])
df.show()
```

---

## ✨ Key Features

### ✅ Smart Input Parsing
- Frontend extracts `input()` calls from code
- Shows prompts in green text: "Enter number:"
- Better UX for interactive programs

### ✅ Problem Schema (Optimized)
```json
{
  "id": "1",
  "title": "Sum Two Numbers",
  "description": "Add two numbers",
  "difficulty": "Easy",
  "labels": ["arithmetic", "basic"],
  "sample_input": "3\n5",
  "sample_output": "8",
  "constraints": "1 <= a, b <= 1000"
}
```

### ✅ Submission Storage
- Automatic UUID generation
- User ID tracking
- Timestamp recording
- MongoDB + mock fallback

### ✅ Production Ready
- Docker Compose orchestration
- Health checks on all services
- MongoDB authentication
- Error handling & timeouts
- Comprehensive logging

---

## 🧪 Testing

### Automated Testing

**Python Script:**
```bash
python test_microservices.py
```

**PowerShell Script:**
```powershell
.\test_microservices.ps1

# Or test specific language:
.\test_microservices.ps1 -TestType python
.\test_microservices.ps1 -TestType java
.\test_microservices.ps1 -TestType sql
.\test_microservices.ps1 -TestType pyspark
```

### Manual Testing

See [QUICK_START_TESTING.md](QUICK_START_TESTING.md) for step-by-step verification with curl commands.

---

## 🚀 Deployment

### Local Development
```bash
docker compose up -d --build
```

### Production Server

See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for complete guide including:
- Nginx reverse proxy setup
- SSL/TLS certificates (Let's Encrypt)
- MongoDB backups
- Monitoring & alerts
- Scaling strategies
- Security hardening

Quick deployment:
```bash
# Copy to server
scp -r . user@server:/home/user/codeplay

# On server
cd /home/user/codeplay
docker compose up -d --build
```

---

## 📋 System Requirements

### Minimum
- CPU: 2 cores
- RAM: 4GB
- Storage: 20GB

### Recommended
- CPU: 4+ cores
- RAM: 8GB
- Storage: 50GB

### OS
- Linux (Ubuntu 20.04+) recommended
- Windows Server / Windows with Docker
- macOS with Docker Desktop

---

## ⚡ Performance

| Language | First Run | Typical Run |
|----------|-----------|------------|
| Python | <500ms | <300ms |
| Java | 1-2s | 1-2s |
| SQL | <500ms | <300ms |
| PySpark | ~30s | 5-10s |

**Timeout Settings:**
- Python: 10 seconds
- Java: 10 seconds
- SQL: 10 seconds
- PySpark: 30 seconds

**Concurrent Support:**
- Local: 10-20 concurrent requests
- Production (scaled): 100+ requests

---

## 🔗 Integration with Other Modules

### Admin Module (Problem Management)
- **Write to:** MongoDB `coding_problems` collection
- **Schema:** id, title, description, difficulty, labels, sample_input, sample_output, constraints
- **Fetch via:** `GET /problem/{id}`

### Analyzer Module (Code Analysis)
- **Read from:** MongoDB `code_submissions` collection
- **Query:** Get submissions by user_id or problem_id
- **API:** `GET /submissions/{user_id}`

### Report Generator
- **Use:** Execution Service results from `POST /run`
- **Storage:** MongoDB submissions collection

---

## 🛠️ Project Structure

```
new_project/
├── services/
│   ├── execution_service/
│   │   ├── main.py              # Python, Java, SQL, PySpark execution
│   │   ├── requirements.txt      # pyspark==3.5.0
│   │   └── Dockerfile           # Python 3.11 + Java + Spark
│   ├── problem_service/
│   │   ├── main.py              # Problem fetching
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   └── submission_service/
│       ├── main.py              # Submission storage
│       ├── requirements.txt
│       └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   └── EditorPanel.jsx  # Input parsing, multi-service calls
│   │   ├── index.css            # Dark theme styling
│   │   └── ...
│   └── Dockerfile               # Node build + Nginx serve
├── docker-compose.yml           # Orchestration
├── DOCUMENTATION_INDEX.md       # 👈 START HERE
├── API_REFERENCE.md
├── DEPLOYMENT_GUIDE.md
├── QUICK_START_TESTING.md
├── test_microservices.py        # Automated testing
├── test_microservices.ps1       # PowerShell testing
└── [other docs]
```

---

## ❓ FAQ

### Q: How is code executed?
**A:** Direct subprocess execution in isolated containers. Fast, reliable, no external compiler services needed.

### Q: Does it work offline?
**A:** Yes! MongoDB falls back to mock storage. All containers are self-contained.

### Q: Can I add more languages?
**A:** Yes! See [CUSTOMIZATION_GUIDE.md](CUSTOMIZATION_GUIDE.md). Add executor function and update routes.

### Q: How do I deploy to production?
**A:** See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md). Includes Nginx, SSL, backups, monitoring.

### Q: Can I scale individual services?
**A:** Yes! Each microservice can be scaled independently with Docker Compose or Kubernetes.

### Q: What about security?
**A:** Code runs in isolated containers with timeouts. MongoDB authenticated. See DEPLOYMENT_GUIDE for hardening.

### Q: What's the difference from v1.0?
**A:** v2.0 is microservices-based. v1.0 was monolithic. v2.0 is independently scalable, easier to integrate, supports PySpark.

---

## 📝 Version Information

- **Release Date:** December 7, 2025
- **Version:** 2.0 (Microservices Edition)
- **Python:** 3.11
- **Node.js:** 18 (React)
- **Java:** OpenJDK 11
- **MongoDB:** 5.0+
- **Docker Compose:** 3.8
- **Status:** ✅ Production Ready

---

## 🎉 Getting Started Now

```bash
# 1. Navigate to project
cd c:\Users\MSI\new_project

# 2. Start services
docker compose up -d --build

# 3. Wait 10-15 seconds for services to start
sleep 10

# 4. Verify services
curl http://localhost:8001/health

# 5. Run tests
python test_microservices.py

# 6. Open browser
# http://localhost:3000

# 7. Read documentation
# See DOCUMENTATION_INDEX.md
```

---

## 📞 Support & Help

| Question | Reference |
|----------|-----------|
| How do I use the API? | [API_REFERENCE.md](API_REFERENCE.md) |
| What's the architecture? | [MICROSERVICES_ARCHITECTURE.md](MICROSERVICES_ARCHITECTURE.md) |
| How do I test it? | [QUICK_START_TESTING.md](QUICK_START_TESTING.md) |
| How do I deploy? | [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) |
| How do I customize it? | [CUSTOMIZATION_GUIDE.md](CUSTOMIZATION_GUIDE.md) |
| What are all the docs? | [DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md) |

---

## 🛑 Stopping Services

```bash
# Stop all services (keep data)
docker compose stop

# Stop and remove containers (keep data)
docker compose down

# Stop, remove containers AND delete data
docker compose down -v
```

---

## 🔄 Common Tasks

### View Logs
```bash
docker compose logs -f execution-service
docker compose logs -f problem-service
docker compose logs -f submission-service
```

### Rebuild Services
```bash
docker compose up -d --build
```

### Reset Everything
```bash
docker compose down -v
docker compose up -d --build
```

### Check Resource Usage
```bash
docker stats
```

---

## 📄 License

[Your License Here]

---

## 👥 Built For Team Integration

CodePlay v2.0 is designed for seamless integration with:
- Admin modules (problem management)
- Analyzer modules (code analysis)
- Report generators
- Separate team deployments
- Easy horizontal scaling

---

**🚀 Ready to begin? Start here:** [DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md)

