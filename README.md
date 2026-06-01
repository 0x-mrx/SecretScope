# SecretScope

SecretScope is a secure, production-grade DevSecOps platform designed to help organizations discover, inventory, monitor, classify, and remediate exposed credentials (like AWS keys, GCP keys, Slack tokens, Git tokens, etc.) across their web assets, repositories, files, and local directories.

This platform is intended for defensive security posture monitoring, compliance validation (PCI-DSS, SOC2, HIPAA), and secure development auditing.

---

## Technical Architecture

The platform runs as a multi-container Docker Compose application:

* **frontend**: Served as a React/Vite development server (mapped to port 5173).
* **backend**: FastAPI web server (port 8000). Handles authentication, project controls, audit queries, dashboard stats, and database transactions.
* **postgres**: Relational database storing user tables, scan logs, findings, encrypted raw secrets, and audit history. Implements Full-Text Search.
* **redis**: Celery message broker and caching.
* **celery_worker**: Background scan job execution. Packages `git` and `git-lfs` to analyze repository histories and commit lists.
* **celery_beat**: Scheduled scan daemon triggering periodic repository/website checks.
* **minio**: Object storage serving generated PDF/HTML reports. Falls back to local directory mapping if disabled.
* **nginx**: Reverse proxy mapping API requests to backend and web dashboard traffic to frontend.

---

## Directory Structure

```
secretscope/
├── docker-compose.yml       # Orchestrates the multi-container platform
├── README.md                # Installation and usage manual
├── backups/                 # Postgres & MinIO disaster recovery scripts
│   ├── backup_postgres.sh
│   └── backup_minio.sh
├── nginx/                   # Reverse Proxy settings
│   ├── nginx.conf
│   └── Dockerfile
├── backend/                 # FastAPI & Scanning Worker application
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── alembic.ini
│   ├── app/
│   │   ├── main.py          # App initialization & default rule seeder
│   │   ├── core/            # Config, security, DB settings
│   │   ├── models/          # SQLAlchemy Database Schemas
│   │   ├── schemas/         # Pydantic validation schemas
│   │   ├── api/             # FastAPI Versioned Routers (v1)
│   │   ├── tasks/           # Background scan jobs
│   │   └── services/        # Plugin Manager, Risk Engine, Storage, Reports
│   └── tests/               # Pytest automated test scripts
└── frontend/                # React Vite Dashboard
    ├── Dockerfile
    ├── package.json
    ├── tailwind.config.js
    └── src/                 # React code components, context, and router pages
```

---

## Getting Started

### 1. Requirements

Ensure you have the following installed on your machine:
* Docker
* Docker Compose
* git

### 2. Startup & Configuration

The easiest way to initialize the platform is by running the automated setup script. This script checks dependencies, prepares your `.env` environment variables file, generates secure cryptographic secret keys, and boots the container stack.

```bash
chmod +x setup.sh
./setup.sh
```

Alternatively, to configure and run the services manually:

1. Copy the environment template:
   ```bash
   cp .env.example .env
   ```
2. Open `.env` and fill in or customize security keys, database parameters, and storage paths.
3. Build and launch all services:
   ```bash
   docker compose up --build -d
   ```

### 3. Log In

1. Open your browser and navigate to `http://localhost`.
2. Login with the default seeded credentials:
   * **Username**: `admin@secretscope.local`
   * **Password**: `SecretScopeAdminPassword123!`

---

## Platform Features & Auditing

### 1. Scanning
* **Websites**: Scan public web pages, extract inline scripts, follow JS references, and decode source maps.
* **Git Repositories**: Shallow clones public or token-authenticated repositories and scans both the latest snapshot and historical commit diffs.
* **Local Directories**: Walk directory hierarchies scanning files like `.env`, config files, `.json`, `.yaml`, etc.

### 2. Risk Evaluation Engine
For each finding, the Risk Engine evaluates:
* **Exposure Risk**: Assessed by asset accessibility (Websites = Critical, Local Directory = Medium).
* **Compliance Risk**: Evaluates threat to SOC2/PCI-DSS standards (AWS/GitHub tokens = Critical).
* **Operational Risk**: Evaluates actionability of the key (AWS = Critical, Slack = Medium).

### 3. Remediation Workflow
FTS search allows auditing findings by status:
`OPEN` $\rightarrow$ `INVESTIGATING` $\rightarrow$ `CONFIRMED` $\rightarrow$ `REMEDIATED` $\rightarrow$ `CLOSED`.
Each status transition requires a logged reason, updating the compliance audit logs.

### 4. Backup & Disaster Recovery
We provide automated cron-ready scripts in `backups/`:
* Run `backups/backup_postgres.sh` to extract a daily compressed SQL database dump.
* Run `backups/backup_minio.sh` to archive report attachments stored in object buckets.
