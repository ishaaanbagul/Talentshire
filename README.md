## Talentshire

# AI driven technical assessment platform

This repository contains a scalable online technical assessment platform designed for multiple user roles, including admins, candidates, and optional future roles such as Super Admin. The architecture separates frontend, backend, microservices, and AI components, allowing independent development and deployment.

---

## **Top-Level File Structure**

```
tech-assessment-platform/
├── frontend/       # React frontend for user interaction
├── backend/        # FastAPI backend handling API requests, business logic, and database interactions
├── services/       # microservices (notifications, PDF generation, etc.)
├── ai/             # AI / ML pipelines and FAISS integration
├── infra/          # Infrastructure and deployment configurations (Docker, Kubernetes, IaC)
├── tests/          # End-to-end and integration tests across the platform
├── scripts/        # Development and setup scripts (database setup, seeding, migrations)
├── .gitignore      # Files and directories to exclude from Git
├── README.md       # Project overview and setup instructions
└── docker-compose.yml # Local development container orchestration
 
```