from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta

from app.core.database import get_db
from app.core.security import get_password_hash, verify_password, create_access_token, Roles
from app.models.user import User
from app.models.audit_log import AuditLog
from app.schemas.auth import UserCreate, Token, UserResponse, PasswordResetRequest, PasswordResetConfirm

router = APIRouter()

@router.post("/register", response_model=UserResponse)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    # Check if user exists
    existing = db.query(User).filter(User.email == user_in.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Hash password
    hashed = get_password_hash(user_in.password)
    user = User(
        email=user_in.email,
        hashed_password=hashed,
        role=user_in.role.upper() if user_in.role else "ANALYST",
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Log action
    log = AuditLog(
        user_id=user.id,
        action="USER_REGISTRATION",
        details=f"User {user.email} registered with role {user.role}"
    )
    db.add(log)
    db.commit()

    return user

@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        # Log failure
        log = AuditLog(
            action="LOGIN_FAILED",
            details=f"Failed login attempt for {form_data.username}"
        )
        db.add(log)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    # Create access token
    access_token = create_access_token(subject=user.id)
    
    # Log success
    log = AuditLog(
        user_id=user.id,
        action="LOGIN_SUCCESS",
        details=f"User {user.email} logged in successfully"
    )
    db.add(log)
    db.commit()

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": user.role,
        "email": user.email
    }

@router.post("/reset-password")
def request_password_reset(req: PasswordResetRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == req.email).first()
    if not user:
        # Prevent user enumeration by returning 200 anyway
        return {"message": "Password reset email sent if account exists"}

    # Mock Reset Code / Flow (MFA-ready / production structure)
    # Generates a temporary reset token (could be JWT with short expiry)
    reset_token = create_access_token(subject=f"reset_{user.id}", expires_delta=timedelta(minutes=15))
    
    log = AuditLog(
        user_id=user.id,
        action="PASSWORD_RESET_REQUESTED",
        details=f"Password reset token generated: {reset_token[:10]}..."
    )
    db.add(log)
    db.commit()
    
    return {"message": "Password reset token generated", "debug_token": reset_token}

@router.post("/reset-password/confirm")
def confirm_password_reset(confirm: PasswordResetConfirm, db: Session = Depends(get_db)):
    # Verify mock token
    from jose import jwt
    from app.core.config import settings
    try:
        payload = jwt.decode(confirm.token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        sub: str = payload.get("sub")
        if not sub.startswith("reset_"):
            raise HTTPException(status_code=400, detail="Invalid reset token")
        user_id = int(sub.split("_")[1])
    except Exception:
        raise HTTPException(status_code=400, detail="Expired or invalid reset token")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.hashed_password = get_password_hash(confirm.new_password)
    db.commit()

    log = AuditLog(
        user_id=user.id,
        action="PASSWORD_RESET_CONFIRMED",
        details=f"User {user.email} changed password successfully"
    )
    db.add(log)
    db.commit()

    return {"message": "Password reset successfully"}

@router.post("/mfa/setup")
def setup_mfa(token: str = Depends(OAuth2PasswordRequestForm), db: Session = Depends(get_db)):
    # Scaffold endpoint for MFA-ready architecture
    return {"secret": "mock_otp_secret_key_12345", "qr_code_url": "https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=OTP_MOCK"}
