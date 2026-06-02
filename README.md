# 🛡️ SecretScope - Gemini API Key Hunter & Exploiter Platform

SecretScope is a secure, production-grade security research and offensive/defensive auditing platform designed to discover, inventory, validate, bypass, and exploit exposed **Google / Gemini API keys** across public websites, Git repositories, local directories, or lists of pre-collected JavaScript URLs.

The platform is engineered for **Security Researchers, Bug Hunters, and DevSecOps Teams** to automate the detection and validation of Gemini API keys, test active permissions safely (including file access, corpora bypasses, and generation endpoints), and calculate real-world financial impacts.

---

## 🚀 Key Features

*   🔍 **5 Specialized Scanner Modes**:
    *   **Mode 1 (Single Domain)**: Scrapes a website, extracts API keys, and validates access.
    *   **Mode 2 (Batch Domains)**: Scans a list of domains in parallel from a `.txt` file or via frontend upload.
    *   **Mode 3 (JS List)**: Scans pre-collected lists of JavaScript files directly.
    *   **Mode 4 (Raw Key Validator)**: Direct verification of raw Google API keys including referer spoofing checks.
    *   **Mode 5 (Capability Evidence Scanner)**: Safe execution of exploitation tests (Generative AI capability verification, Files API, Corpora bypass).
*   ⚡ **Dynamic Exploit Verification (PoC Tests)**:
    *   **Generative Models**: Validates Text, Image, Video, and Text-to-Speech (TTS) endpoints.
    *   **Referer Bypass**: Tests if key restrictions can be spoofed using a custom `Referer` header.
    *   **Files / Corpora Bypass**: Verifies if file upload boundaries or project creation bypass restrictions are active.
*   💰 **Financial Impact Estimator**:
    *   Estimates potential overbilling costs per 1,000 requests using official Gemini pricing schedules (Text input/output, Imagen 4.0, Veo 3.0, and TTS modalities).
*   📝 **Bug Bounty Report Exporter**:
    *   Generates and lets you copy pre-formatted, detailed markdown bug bounty draft reports containing extracted evidence and calculated financial impact.
*   🔒 **Enterprise Foundation**:
    *   JWT-based authentication and role-based access control (Admin, Analyst, Auditor).
    *   AES-256 Fernet encryption for secrets stored at rest.
    *   Immutable database Audit Logs tracking every administrative and decryption action.

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

## 🎯 Specialized Gemini Exploit & Verification Center

SecretScope provides an interactive "Gemini Exploit Center" directly integrated into the dashboard's findings drawer to test exposed key scopes:

### 1. Active Capability Validation
Instantly checks the live viability of the leaked credential against Google APIs:
*   **Referer Bypass Check**: Automatically sends validation requests with and without `Referer: https://www.google.com/` to check for host restrictions.
*   **File API Probe**: Echoes a dummy payload to the Google File API, verifies if it can be listed, and deletes it immediately to guarantee safe scanning.
*   **Corpora Project Bypass**: Checks if a developer project can be created to bypass files upload restrictions.

### 2. Generative Content Verification
Triggers real-time test queries on the models allowed by the API key:
*   **Text**: Prompts `gemini-2.5-flash` to verify text output generation.
*   **Image**: Prompts `imagen-4.0-generate-001` to test automated picture creation.
*   **Video**: Prompts `veo-3.0-fast-generate-001` to check video generation (using async task polling).
*   **TTS (Audio)**: Queries the TTS preview model to synthesize speech from text.

### 3. Financial Quota Abuse Estimator
Automatically parses model capabilities and computes the maximum financial abuse capability (estimated dollar cost per 1,000 requests and general exposure rating).

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
| **POST** | `/api/v1/scans/gemini/scan` | Trigger a targeted Gemini scanner task | Admin, Analyst |
| **POST** | `/api/v1/scans/gemini/exploit` | Trigger real-time capability exploitation check on a key | Admin, Analyst |
| **POST** | `/api/v1/reports` | Generate PDF, HTML, or MD compliance report | Admin, Analyst |

---

## 🛡️ Defensive Use Disclaimer
This platform is intended strictly for defensive security, compliance validation, internal auditing, and authorized security research assessments. Do not use this tool on targets without explicit prior written authorization.
