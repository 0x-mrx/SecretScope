import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.core.config import settings
from app.core.database import Base, engine, SessionLocal
from app.api import auth, dashboard, projects, assets, scans, findings, reports
from app.models.secret_type import SecretType
from app.models.user import User
from app.core.security import get_password_hash

# Rate limiting setup
limiter = Limiter(key_func=get_remote_address)
app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    docs_url="/docs"
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict to frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Base healthcheck
@app.get("/health")
@limiter.limit("5/minute")
def health_check():
    return {"status": "healthy", "service": settings.PROJECT_NAME}

# API Routing
app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["Authentication"])
app.include_router(dashboard.router, prefix=f"{settings.API_V1_STR}/dashboard", tags=["Dashboard"])
app.include_router(projects.router, prefix=f"{settings.API_V1_STR}/projects", tags=["Projects"])
app.include_router(assets.router, prefix=f"{settings.API_V1_STR}/assets", tags=["Assets"])
app.include_router(scans.router, prefix=f"{settings.API_V1_STR}/scans", tags=["Scans"])
app.include_router(findings.router, prefix=f"{settings.API_V1_STR}/findings", tags=["Findings"])
app.include_router(reports.router, prefix=f"{settings.API_V1_STR}/reports", tags=["Reports"])

# Initialize Database Schema & Default Records
@app.on_event("startup")
def startup_event():
    # 1. Create tables if they do not exist
    Base.metadata.create_all(bind=engine)
    
    # 2. Populate Default Scanning Rules if missing
    db = SessionLocal()
    try:
        default_rules = [
            {
                "name": "AWS_ACCESS_KEY",
                "pattern": "AKIA[0-9A-Z]{16}",
                "description": "AWS Access Key ID token",
                "is_custom": False
            },
            {
                "name": "GOOGLE_API_KEY",
                "pattern": "AIzaSy[A-Za-z0-9-_]{33,35}",
                "description": "Google API and Cloud Platform keys",
                "is_custom": False
            },
            {
                "name": "GITHUB_TOKEN",
                "pattern": "gh[pousr]_[A-Za-z0-9_]{36,255}",
                "description": "GitHub developer personal and oauth tokens",
                "is_custom": False
            },
            {
                "name": "SLACK_TOKEN",
                "pattern": "xox[bp]-[0-9a-zA-Z-]{10,}",
                "description": "Slack integration bot and user tokens",
                "is_custom": False
            },
            {
                "name": "OPENAI_KEY",
                "pattern": "sk-[a-zA-Z0-9]{32,80}",
                "description": "OpenAI platform API keys",
                "is_custom": False
            }
        ]

        for rule in default_rules:
            existing = db.query(SecretType).filter(SecretType.name == rule["name"]).first()
            if not existing:
                st = SecretType(
                    name=rule["name"],
                    pattern=rule["pattern"],
                    description=rule["description"],
                    is_custom=rule["is_custom"]
                )
                db.add(st)
        db.commit()

        # 3. Create a Default Admin User if database is empty
        admin_email = "admin@secretscope.local"
        existing_admin = db.query(User).filter(User.email == admin_email).first()
        if not existing_admin:
            admin_user = User(
                email=admin_email,
                hashed_password=get_password_hash("SecretScopeAdminPassword123!"),
                role="ADMIN",
                is_active=True
            )
            db.add(admin_user)
            db.commit()
            print("Default admin created: admin@secretscope.local / SecretScopeAdminPassword123!")

    except Exception as e:
        db.rollback()
        print(f"Error initializing default records: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
