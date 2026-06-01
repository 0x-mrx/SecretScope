# 🛡️ SecretScope - Enterprise Secret Discovery & Compliance Platform

SecretScope is a secure, production-grade DevSecOps and offensive/defensive security platform designed to discover, inventory, monitor, classify, and validate exposed secrets (such as AWS keys, Google API keys, Slack tokens, Git tokens, and OpenAI credentials) across public web assets, code repositories, files, and local directories.

The platform is engineered for **Security Engineers, DevSecOps Teams, and Bug Hunters** to identify credential exposure, verify key viability, ensure compliance regulations (SOC2, PCI-DSS, HIPAA), and manage the full remediation lifecycle.

---

## 🚀 Key Features

*   🔍 **Multi-Source Scanners**: 
    *   **Websites**: Crawl public assets, extract inline scripts, walk JS bundles, and parse exposed `.js.map` source maps.
    *   **Git Repositories**: Walk full commit logs, branches, authors, and historical diffs using shallow clone git walks.
    *   **Local Directories**: Traverse file hierarchies scanning files like `.env`, config files, `.json`, `.yaml`, `.xml`, etc.
*   🔌 **Plugin-Based Architecture**: Modular detectors and classifiers for AWS, Google Cloud, GitHub, Slack, OpenAI, and more.
*   ✅ **Active Key Validation**: Live HTTP validation checks to determine if a credential is active and output its permissions/scopes.
*   ⚙️ **Dynamic Custom Signatures**: Inject custom regex patterns on the fly via the database or API.
*   ⚖️ **Risk Engine**: Multi-dimensional risk score based on **Exposure Risk** (public vs. internal), **Compliance Risk** (threat to SOC2/PCI-DSS), and **Operational Risk** (write vs. read access).
*   🔒 **Enterprise Security**: 
    *   JWT Authentication & Role-Based Access Control (Admin, Analyst, Auditor).
    *   Fernet AES symmetric encryption for secrets at rest.
    *   Immutable database Audit Logs tracking every administrative and decryption action.
    *   Rate limiting on public endpoints.

---

## 🛠️ Technical Architecture

SecretScope operates as a multi-container Docker Compose application:

*   `frontend`: React + TypeScript dashboard served via Vite (mapped to port `5173`).
*   `backend`: FastAPI API server (mapped to port `8000`). Handles core application logic.
*   `postgres`: Relational database with full-text search indexes.
*   `redis`: Celery message broker and cache storage.
*   `celery_worker`: Scan worker packaging Git and Git-LFS tooling.
*   `celery_beat`: Periodic scheduler triggering automated scans.
*   `minio`: Object storage serving compliance PDF and HTML reports.
*   `nginx`: Reverse proxy routing `/api` traffic to backend and `/` to frontend.

---

## 📁 Directory Structure

```text
secretscope/
├── docker-compose.yml       # Docker Compose multi-container stack configuration
├── README.md                # System documentation
├── setup.sh                 # Dependency check & secure key generation script
├── backups/                 # Postgres & MinIO disaster recovery scripts
│   ├── backup_postgres.sh
│   └── backup_minio.sh
├── nginx/                   # Reverse Proxy settings
│   ├── nginx.conf
│   └── Dockerfile
├── backend/                 # FastAPI & Celery Worker application
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
│   │   └── services/        # Plugins, Risk Engine, Storage, Reports
│   └── tests/               # Pytest automated test scripts
└── frontend/                # React Vite Dashboard
    ├── Dockerfile
    ├── package.json
    ├── tailwind.config.js
    └── src/                 # Dashboard components, pages, services, context
```

---

## 🏁 Getting Started

### 1. Requirements

Ensure you have the following installed on your machine:
*   Docker & Docker Compose
*   Git
*   Python 3.8+ (optional, for setup wizard)
*   Node.js v18+ (optional, for running local non-docker developer flow)

---

### 2. Startup & Configuration (Docker Flow)

The easiest way to initialize the platform is by running the automated setup script. This script validates dependencies, prepares your `.env` configuration, generates unique secure keys for JWT and Fernet encryption, and starts the container stack.

```bash
chmod +x setup.sh
./setup.sh
```

#### Manual Docker Startup:
If you prefer to configure the environment manually:
1.  Copy the environment template:
    ```bash
    cp .env.example .env
    ```
2.  Open `.env` and configure your `SECRET_KEY`, `ENCRYPTION_KEY`, and Postgres passwords.
3.  Build and launch all services:
    ```bash
    docker compose up --build -d
    ```

---

### 3. Startup & Configuration (Local Development Flow)

If you are modifying code, debugging, or running without Docker:

#### Running the FastAPI Backend:
1.  Navigate to the `backend/` directory:
    ```bash
    cd backend
    ```
2.  Create and activate a virtual environment:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use: .\venv\Scripts\Activate.ps1
    ```
3.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
4.  Configure environment variables and start the server (uses local SQLite for ease):
    ```powershell
    # Windows PowerShell
    $env:DATABASE_URL="sqlite:///./secretscope.db"
    $env:STORAGE_PROVIDER="local"
    $env:LOCAL_STORAGE_DIR=".\storage"
    python -m app.main
    ```
    *(The backend API will run on `http://127.0.0.1:8000`)*

#### Running the React Frontend:
1.  Navigate to the `frontend/` directory:
    ```bash
    cd frontend
    ```
2.  Install packages and launch Vite:
    ```bash
    npm install
    npm run dev
    ```
    *(The frontend dashboard will run on `http://localhost:5173`)*

---

### 4. Default Seeded Credentials

1.  Open your browser and navigate to `http://localhost` (or `http://localhost:5173` if running locally).
2.  Log in using the default credentials:
    *   **Username**: `admin@secretscope.local`
    *   **Password**: `SecretScopeAdminPassword123!`

---

## 🎯 Bug Hunting & Security Research Features

SecretScope includes specialized API capabilities designed specifically for security researchers to retrieve raw credentials and verify active exposures:

### 1. Decrypt & View Raw Secret (`GET /api/v1/findings/{id}/raw`)
Raw credentials are encrypted at rest using base64 Fernet. Authorized users can decrypt the raw key to manually check and test the finding:
*   **Access**: Restricted to `ADMIN` and `ANALYST` roles.
*   **Auditability**: Every decryption event is logged in the database audit log with user details and timestamps.

### 2. Active Validation (`POST /api/v1/findings/{id}/validate`)
Instantly checks the live viability of the leaked credential against target platform APIs:
*   **Google API Key**: Queries Google Maps Geocoding API to test key status.
*   **GitHub Token**: Queries the GitHub `/user` endpoint to verify the token and parse its OAuth scopes.
*   **Slack Token**: Queries `auth.test` Slack API to test bot/user authentication, team name, and user ID.
*   **OpenAI Key**: Queries the OpenAI `/v1/models` endpoint to test model enumeration access.
*   **Result Transitions**: 
    *   If active $\rightarrow$ transition status to `CONFIRMED` and record scopes in remediation notes.
    *   If inactive/revoked $\rightarrow$ transition status to `CLOSED` and mark as inactive.

---

## ⚙️ Custom Scanning Rules

### Database Custom Rules
You can insert custom regular expression signatures directly into the `secret_types` table. The scanner will automatically fetch and apply them:
```sql
INSERT INTO secret_types (name, pattern, description, is_custom, is_active)
VALUES (
  'CUSTOM_INTERNAL_API_KEY',
  'company-prod-[a-f0-9]{32}',
  'Target-specific internal API key pattern',
  true,
  true
);
```

---

## 📊 Summary of REST API Endpoints

| Method | Endpoint | Description | Role Required |
| :--- | :--- | :--- | :--- |
| **POST** | `/api/v1/auth/login` | Login and retrieve JWT access token | Open |
| **GET** | `/api/v1/dashboard` | Executive analytics, trend lines, risk heatmap | All |
| **POST** | `/api/v1/projects` | Create a new project audit scope | Admin, Analyst |
| **POST** | `/api/v1/assets` | Register website, Git repository, or directory target | Admin, Analyst |
| **POST** | `/api/v1/scans` | Trigger manual scanning on a target asset | Admin, Analyst |
| **GET** | `/api/v1/findings` | List and search findings with full-text search filters | All |
| **GET** | `/api/v1/findings/{id}/raw` | Decrypt and retrieve raw secret value | Admin, Analyst |
| **POST** | `/api/v1/findings/{id}/validate` | Perform live active HTTP verification checks | Admin, Analyst |
| **POST** | `/api/v1/reports` | Generate PDF, HTML, or MD compliance report | Admin, Analyst |

---

## 🛡️ Defensive Use Disclaimer
This platform is intended strictly for defensive security, compliance validation, internal auditing, and authorized security research assessments. Do not use this tool on targets without explicit prior written authorization.
