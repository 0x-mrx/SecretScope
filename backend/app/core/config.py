import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "SecretScope"
    API_V1_STR: str = "/api/v1"
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "super-secret-jwt-signing-key-change-in-prod-1234!")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7 # 1 week
    
    # DB & Redis
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://secretscope:SecretScopeSecurePassword123!@postgres:5432/secretscope")
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://redis:6379/0")
    
    # Storage
    STORAGE_PROVIDER: str = os.getenv("STORAGE_PROVIDER", "local") # "local" or "minio"
    LOCAL_STORAGE_DIR: str = os.getenv("LOCAL_STORAGE_DIR", "/var/lib/secretscope/storage")
    
    MINIO_ENDPOINT: str = os.getenv("MINIO_ENDPOINT", "minio:9000")
    MINIO_ACCESS_KEY: str = os.getenv("MINIO_ACCESS_KEY", "secretscope_admin")
    MINIO_SECRET_KEY: str = os.getenv("MINIO_SECRET_KEY", "SecretScopeMinioSecurePassword123!")
    MINIO_SECURE: bool = os.getenv("MINIO_SECURE", "false").lower() == "true"
    MINIO_BUCKET_NAME: str = os.getenv("MINIO_BUCKET_NAME", "secretscope-reports")
    
    # Encryption at rest
    ENCRYPTION_KEY: str = os.getenv("ENCRYPTION_KEY", "uP2Nl6eE2K3jP-hE0k_g3rO_b5DqR9xK6eJ7Z1d3nK4=") # 32-byte Fernet key

    class Config:
        case_sensitive = True

# We can bypass pydantic-settings if library not present by parsing from environment or simple dictionary
# Pydantic v2 has BaseSettings under pydantic_settings. Let's make it robust.
try:
    settings = Settings()
except Exception:
    # Fallback to simple object if pydantic_settings fails
    class FallbackSettings:
        PROJECT_NAME = "SecretScope"
        API_V1_STR = "/api/v1"
        SECRET_KEY = os.getenv("SECRET_KEY", "super-secret-jwt-signing-key-change-in-prod-1234!")
        ALGORITHM = "HS256"
        ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7
        DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://secretscope:SecretScopeSecurePassword123!@postgres:5432/secretscope")
        REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
        STORAGE_PROVIDER = os.getenv("STORAGE_PROVIDER", "local")
        LOCAL_STORAGE_DIR = os.getenv("LOCAL_STORAGE_DIR", "/var/lib/secretscope/storage")
        MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "minio:9000")
        MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "secretscope_admin")
        MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "SecretScopeMinioSecurePassword123!")
        MINIO_SECURE = os.getenv("MINIO_SECURE", "false").lower() == "true"
        MINIO_BUCKET_NAME = os.getenv("MINIO_BUCKET_NAME", "secretscope-reports")
        ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY", "uP2Nl6eE2K3jP-hE0k_g3rO_b5DqR9xK6eJ7Z1d3nK4=")
    settings = FallbackSettings()
